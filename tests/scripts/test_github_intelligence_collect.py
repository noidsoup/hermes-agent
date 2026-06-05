from scripts.github_intelligence_collect import (
    RateLimitExhausted,
    _wait_for_rate_reset,
    build_search_query,
    load_existing_jsonl,
    merge_unique,
    parse_github_reset,
    partitioned_search_issues,
    redact,
    search_issues,
    write_jsonl,
)
from scripts.github_intelligence_query import search


def test_build_search_query():
    assert build_search_query("pr", "noidsoup", "authored") == "author:noidsoup is:pr"
    assert build_search_query("issue", "noidsoup", "involved", "2020-01-01") == "involves:noidsoup is:issue updated:>=2020-01-01"


def test_redact_token_shapes():
    redacted = redact({"body": "token=abc123456789 sk-abcdefghijklmnopqrstuvwxyz github_pat_abcdefghijklmnopqrstuvwxyz_1234567890"})
    body = redacted["body"]
    assert "abc123456789" not in body
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in body
    assert "github_pat_abcdefghijklmnopqrstuvwxyz_1234567890" not in body


def test_search_issues_raises_after_retries_exhausted(monkeypatch):
    """Updated behavior: on rate-limit, search_issues retries up to MAX_RETRIES
    times then raises RateLimitExhausted so the caller can record the partial
    failure in errors.jsonl. The exception's `partial_rows` carries any rows
    successfully collected from earlier pages of the same query."""
    import scripts.github_intelligence_collect as gic

    def fake_gh_json(args, timeout=120):
        # First call succeeds (yields 100 rows), subsequent calls rate-limit.
        # After MAX_RETRIES (5) retries, the exception should propagate.
        if not getattr(fake_gh_json, "first_done", False):
            fake_gh_json.first_done = True
            return {"items": [{"id": i} for i in range(100)]}
        raise RuntimeError("gh: API rate limit exceeded (HTTP 403)")

    monkeypatch.setattr(gic, "gh_json", fake_gh_json)
    monkeypatch.setattr(gic.time, "sleep", lambda _: None)  # don't actually wait
    import pytest
    with pytest.raises(RateLimitExhausted) as excinfo:
        search_issues("author:noidsoup is:pr")
    assert "retries exhausted" in str(excinfo.value).lower()
    assert "author:noidsoup is:pr" in str(excinfo.value)
    # Per-page partials: the 100 rows from the first page should be preserved
    assert len(excinfo.value.partial_rows) == 100
    assert excinfo.value.partial_rows[0]["id"] == 0


def test_search_issues_retries_then_succeeds(monkeypatch):
    """Two rate-limits, then success. search_issues should retry both and
    return the successful page's items."""
    import scripts.github_intelligence_collect as gic
    calls = []

    def fake_gh_json(args, timeout=120):
        calls.append(args)
        if len(calls) <= 2:
            raise RuntimeError("gh: API rate limit exceeded (HTTP 403)")
        # Third attempt succeeds; < per_page so we stop after this page.
        return {"items": [{"id": "ok-1"}, {"id": "ok-2"}]}

    monkeypatch.setattr(gic, "gh_json", fake_gh_json)
    monkeypatch.setattr(gic.time, "sleep", lambda _: None)
    rows = search_issues("author:noidsoup is:pr")
    assert len(rows) == 2
    assert [r["id"] for r in rows] == ["ok-1", "ok-2"]
    # Should have made 3 calls total (2 rate-limited + 1 success).
    assert len(calls) == 3


def test_wait_for_rate_reset_returns_short_wait_for_x_ratelimit_reset(monkeypatch):
    """_wait_for_rate_reset should parse x-ratelimit-reset: <unix-ts> and
    return a sleep duration close to the time until that timestamp."""
    import time as time_mod
    # 5 seconds in the future
    future_ts = int(time_mod.time()) + 5
    err = f"x-ratelimit-reset: {future_ts}"
    wait = _wait_for_rate_reset(err, attempt=1)
    # Should be ~5-7 seconds (reset + 2s buffer).
    assert 4.0 <= wait <= 10.0


def test_wait_for_rate_reset_parses_timestamp_format():
    """_wait_for_rate_reset should also parse 'timestamp YYYY-MM-DD HH:MM:SS UTC'
    format (the format emitted by the gh CLI)."""
    from datetime import datetime, timezone, timedelta
    # 3 seconds from now
    soon = (datetime.now(timezone.utc) + timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S")
    err = f"gh api ... failed: ... timestamp {soon} UTC"
    wait = _wait_for_rate_reset(err, attempt=1)
    assert 2.0 <= wait <= 8.0


def test_wait_for_rate_reset_fails_fast_on_far_future_reset():
    """If the reset is > 10 min away, _wait_for_rate_reset should raise
    RateLimitExhausted immediately rather than returning a wait that would
    busy-loop into the same limit (the adversarial loop's finding #3)."""
    from datetime import datetime, timezone, timedelta
    far = (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    err = f"gh api ... failed: ... timestamp {far} UTC"
    import pytest
    with pytest.raises(RateLimitExhausted) as excinfo:
        _wait_for_rate_reset(err, attempt=1)
    assert "1799s away" in str(excinfo.value) or "1800s away" in str(excinfo.value)


def test_wait_for_rate_reset_falls_back_to_backoff_when_no_reset_hint():
    """When the error has no parseable reset hint, fall through to exponential
    backoff. First attempt should be ~2 seconds."""
    wait = _wait_for_rate_reset("gh: API rate limit exceeded (no reset hint)", attempt=1)
    # First attempt: base=2, jitter ±10%
    assert 1.5 <= wait <= 3.0
    # Fifth attempt: base=32
    wait5 = _wait_for_rate_reset("gh: API rate limit exceeded (no reset hint)", attempt=5)
    assert 28.0 <= wait5 <= 36.0


def test_rate_limit_exhausted_is_runtime_error():
    """collect() catches generic Exception; subclass RuntimeError so existing
    error handling keeps working without per-class plumbing."""
    assert issubclass(RateLimitExhausted, RuntimeError)


def test_partitioned_search_continues_on_partial_year(monkeypatch):
    """If one year-partition raises RateLimitExhausted mid-partition, the
    loop should keep the rows from successful years, record the partial,
    and re-raise a summary at the end. The exception's `partial_rows`
    attribute carries the successful-years' data for the caller to merge."""
    import scripts.github_intelligence_collect as gic

    def fake_search_issues(query, max_pages=None, per_page=100):
        if "updated:2025" in query:
            raise RateLimitExhausted("simulated rate limit on 2025 partition")
        if "updated:2024" in query:
            return [{"id": "y2024-1"}]
        if "updated:2023" in query:
            return [{"id": "y2023-1"}]
        return []

    monkeypatch.setattr(gic, "search_issues", fake_search_issues)
    monkeypatch.setattr(gic.time, "sleep", lambda _: None)
    import pytest
    with pytest.raises(RateLimitExhausted) as excinfo:
        gic.partitioned_search_issues("author:noidsoup is:pr")
    # Should have partial-failure message that mentions 1 partition failed
    assert "1 year-partition" in str(excinfo.value)
    # The 2024 + 2023 rows should be on the exception for the caller to merge
    assert sorted(r["id"] for r in excinfo.value.partial_rows) == ["y2023-1", "y2024-1"]


def test_collect_merges_partial_rows_on_rate_limit_exhausted(tmp_path, monkeypatch):
    """End-to-end: when partitioned_search_issues raises RateLimitExhausted
    with partial_rows, collect() should record the error AND merge the
    partial rows with on-disk data. This is the data-preservation fix the
    adversarial loop demanded."""
    import json
    import scripts.github_intelligence_collect as gic

    out = tmp_path / "vault"
    (out / "raw").mkdir(parents=True)
    (out / "state").mkdir(parents=True)

    # Seed on-disk data: 1 pre-existing PR record
    (out / "raw" / "prs-involved.jsonl").write_text(
        json.dumps({"id": 1, "title": "old"}) + "\n"
    )

    # Stub gh_json (auth check etc.)
    monkeypatch.setattr(gic, "run_gh", lambda args, timeout=60: (0, json.dumps({"login": "noidsoup"}), ""))
    monkeypatch.setattr(gic, "gh_json", lambda args, timeout=60: {"login": "noidsoup"})
    monkeypatch.setattr(gic, "write_json", lambda p, o: None)

    # partitioned_search_issues raises with partial_rows
    def fake_partitioned(query, max_pages=None, per_page=100):
        raise RateLimitExhausted("simulated", partial_rows=[{"id": 2, "title": "new"}])

    monkeypatch.setattr(gic, "partitioned_search_issues", fake_partitioned)
    monkeypatch.setattr(gic.time, "sleep", lambda _: None)

    # Run collect. We don't care about the return; we care about side effects.
    try:
        gic.collect(out, max_pages=1, resume=True)
    except Exception:
        pass

    # After the run: file should have BOTH old (id=1) and new (id=2) records,
    # errors.jsonl should have a record, manifest should show the file.
    final = [json.loads(l) for l in (out / "raw" / "prs-involved.jsonl").read_text().splitlines() if l.strip()]
    assert sorted(r["id"] for r in final) == [1, 2]
    errs = [json.loads(l) for l in (out / "state" / "errors.jsonl").read_text().splitlines() if l.strip() and l.strip() != "[]"]
    assert any("simulated" in e.get("error", "") for e in errs)


def test_partitioned_search_returns_all_rows_when_no_failures(monkeypatch):
    """Sanity: when no year fails, partitioned_search_issues returns the
    union of all years' rows, deduped by id."""
    import scripts.github_intelligence_collect as gic

    def fake_search_issues(query, max_pages=None, per_page=100):
        if "updated:2024" in query:
            return [{"id": "a"}, {"id": "b"}]
        if "updated:2023" in query:
            return [{"id": "b"}, {"id": "c"}]  # "b" is a duplicate
        return []

    monkeypatch.setattr(gic, "search_issues", fake_search_issues)
    monkeypatch.setattr(gic.time, "sleep", lambda _: None)
    rows = gic.partitioned_search_issues("author:noidsoup is:pr")
    assert sorted(r["id"] for r in rows) == ["a", "b", "c"]


def test_partitioned_search_uses_simple_path_for_smoke(monkeypatch):
    calls = []

    def fake_search(query, max_pages=None, per_page=100):
        calls.append((query, max_pages, per_page))
        return [{"id": 1, "html_url": "https://example.test/1"}]

    monkeypatch.setattr("scripts.github_intelligence_collect.search_issues", fake_search)
    rows = partitioned_search_issues("author:noidsoup is:pr", max_pages=1)
    assert rows == [{"id": 1, "html_url": "https://example.test/1"}]
    assert calls == [("author:noidsoup is:pr", 1, 100)]


def test_resume_helpers_merge_and_parse_reset(tmp_path):
    path = tmp_path / "rows.jsonl"
    write_jsonl(path, [{"id": 1, "title": "old"}])
    existing = load_existing_jsonl(path)
    merged = merge_unique(existing, [{"id": 1, "title": "old duplicate"}, {"id": 2, "title": "new"}])
    assert [row["id"] for row in merged] == [1, 2]
    assert parse_github_reset("timestamp 2026-06-01 04:30:36 UTC") == "2026-06-01T04:30:36+00:00"


def test_write_jsonl_and_query(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    write_jsonl(raw / "repos.jsonl", [{"full_name": "noidsoup/hermes-agent", "description": "Hermes AI agent"}])
    (tmp_path / "reports").mkdir()
    hits = search(tmp_path, "Hermes", limit=3)
    assert hits
    assert hits[0]["score"] >= 1
