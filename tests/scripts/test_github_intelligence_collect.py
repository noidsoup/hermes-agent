from scripts.github_intelligence_collect import build_search_query, partitioned_search_issues, redact, search_issues, write_jsonl
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


def test_search_issues_keeps_partial_on_rate_limit(monkeypatch):
    calls = []

    def fake_gh_json(args, timeout=120):
        calls.append(args)
        if len(calls) == 1:
            return {"items": [{"id": 1}] * 100}
        raise RuntimeError("gh: API rate limit exceeded (HTTP 403)")

    monkeypatch.setattr("scripts.github_intelligence_collect.gh_json", fake_gh_json)
    monkeypatch.setattr("scripts.github_intelligence_collect.time.sleep", lambda _: None)
    rows = search_issues("author:noidsoup is:pr")
    assert len(rows) == 100


def test_partitioned_search_uses_simple_path_for_smoke(monkeypatch):
    calls = []

    def fake_search(query, max_pages=None, per_page=100):
        calls.append((query, max_pages, per_page))
        return [{"id": 1, "html_url": "https://example.test/1"}]

    monkeypatch.setattr("scripts.github_intelligence_collect.search_issues", fake_search)
    rows = partitioned_search_issues("author:noidsoup is:pr", max_pages=1)
    assert rows == [{"id": 1, "html_url": "https://example.test/1"}]
    assert calls == [("author:noidsoup is:pr", 1, 100)]


def test_write_jsonl_and_query(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    write_jsonl(raw / "repos.jsonl", [{"full_name": "noidsoup/hermes-agent", "description": "Hermes AI agent"}])
    (tmp_path / "reports").mkdir()
    hits = search(tmp_path, "Hermes", limit=3)
    assert hits
    assert hits[0]["score"] >= 1
