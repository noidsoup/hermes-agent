#!/usr/bin/env python3
"""Read-only GitHub intelligence collector for Nicholas's accessible GitHub history.

This script only performs read operations through `gh`. It writes raw API/search
payloads into a local data vault and never mutates GitHub state.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from urllib.parse import quote
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_OUT = Path.home() / "Data" / "github-intelligence"
TOKEN_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd)(\s*[:=]\s*)(['\"]?)[^\s'\"]{6,}(['\"]?)"),
]


def redact(value: Any) -> Any:
    if isinstance(value, str):
        text = value
        for pat in TOKEN_PATTERNS:
            text = pat.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}REDACTED{m.group(4)}" if m.lastindex and m.lastindex >= 4 else "REDACTED", text)
        return text
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    return value


def run_gh(args: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def gh_json(args: list[str], timeout: int = 120) -> Any:
    rc, out, err = run_gh(args, timeout=timeout)
    if rc != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {err.strip()[-1000:]}")
    if not out.strip():
        return None
    return json.loads(out)


def ensure_layout(out: Path) -> None:
    for rel in ["raw", "state", "reports", "index"]:
        (out / rel).mkdir(parents=True, exist_ok=True)
    readme = out / "README.md"
    if not readme.exists():
        readme.write_text(
            "# GitHub Intelligence Vault\n\n"
            "Local read-only archive of GitHub metadata accessible to the authenticated `gh` account.\n\n"
            "Raw private/org data should stay local. Promote only reviewed, stable summaries into Hermes memory.\n",
            encoding="utf-8",
        )


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(redact(obj), indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(redact(row), ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def append_error(out: Path, stage: str, error: Exception | str) -> None:
    rec = {"stage": stage, "error": str(error), "at": datetime.now(timezone.utc).isoformat()}
    with (out / "state" / "errors.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(redact(rec), sort_keys=True) + "\n")


def paginated_api(endpoint: str, max_pages: int | None = None) -> list[Any]:
    cmd = ["api", "--paginate", endpoint]
    # gh emits one JSON document per page for REST pagination; use jq to flatten
    cmd.extend(["--jq", ".[]"])
    rc, out, err = run_gh(cmd, timeout=600)
    if rc != 0:
        raise RuntimeError(err.strip())
    rows: list[Any] = []
    for line in out.splitlines():
        if line.strip():
            rows.append(json.loads(line))
            if max_pages and len(rows) >= max_pages * 100:
                break
    return rows


def build_search_query(kind: str, login: str, relation: str, since: str | None = None) -> str:
    if relation == "authored":
        q = f"author:{login}"
    elif relation == "involved":
        q = f"involves:{login}"
    elif relation == "reviewed":
        q = f"reviewed-by:{login}"
    else:
        raise ValueError(f"unknown relation: {relation}")
    if kind == "pr":
        q += " is:pr"
    elif kind == "issue":
        q += " is:issue"
    else:
        raise ValueError(f"unknown kind: {kind}")
    if since:
        q += f" updated:>={since}"
    return q


def search_issues(query: str, max_pages: int | None = None, per_page: int = 100) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while True:
        endpoint = f"search/issues?q={quote(query)}&per_page={per_page}&page={page}"
        try:
            data = gh_json(["api", endpoint], timeout=180)
        except RuntimeError as exc:
            msg = str(exc)
            if "Only the first 1000 search results are available" in msg:
                print(f"  search cap reached at page {page}; keeping {len(rows)} partial results ({query})", flush=True)
                break
            if "API rate limit exceeded" in msg or "secondary rate limit" in msg.lower():
                print(f"  search rate limit hit at page {page}; keeping {len(rows)} partial results ({query})", flush=True)
                break
            raise
        items = data.get("items", []) if isinstance(data, dict) else []
        rows.extend(items)
        print(f"  search page {page}: {len(items)} items ({query})", flush=True)
        if len(items) < per_page or (max_pages and page >= max_pages):
            break
        page += 1
        time.sleep(2.2)
    return rows


def partitioned_search_issues(base_query: str, max_pages: int | None = None, per_page: int = 100) -> list[dict]:
    """Search issues/PRs, partitioning by updated year to avoid GitHub's 1000-result cap.

    GitHub Search only exposes the first 1000 results for a query. For full runs,
    split broad PR/issue queries by updated year. Smoke tests (`max_pages`) keep
    the simple one-query behavior for speed.
    """
    if max_pages:
        return search_issues(base_query, max_pages=max_pages, per_page=per_page)

    current_year = datetime.now(timezone.utc).year
    # GitHub launched in 2008; include current year and an older catch-all.
    ranges = [f"updated:{year}-01-01..{year}-12-31" for year in range(current_year, 2007, -1)]
    ranges.append("updated:<2008-01-01")
    seen: set[str] = set()
    rows: list[dict] = []
    for qualifier in ranges:
        query = f"{base_query} {qualifier}"
        part = search_issues(query, max_pages=None, per_page=per_page)
        print(f"  partition {qualifier}: {len(part)} items", flush=True)
        for item in part:
            key = str(item.get("id") or item.get("node_id") or item.get("html_url"))
            if key not in seen:
                seen.add(key)
                rows.append(item)
        time.sleep(2.2)
    return rows


def collect(out: Path, max_pages: int | None = None, since: str | None = None) -> dict[str, Any]:
    ensure_layout(out)
    manifest: dict[str, Any] = {"started_at": datetime.now(timezone.utc).isoformat(), "out": str(out), "files": {}, "errors": []}

    print("checking gh auth...", flush=True)
    rc, auth_out, auth_err = run_gh(["auth", "status"], timeout=60)
    if rc != 0:
        raise RuntimeError(auth_err or auth_out)

    user = gh_json(["api", "user"], timeout=60)
    login = user["login"]
    write_json(out / "raw" / "user.json", user)
    manifest["login"] = login
    print(f"authenticated as {login}", flush=True)

    stages = [
        ("orgs", lambda: paginated_api("user/orgs?per_page=100", max_pages=max_pages), out / "raw" / "orgs.jsonl"),
        ("repos", lambda: paginated_api("user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=updated", max_pages=max_pages), out / "raw" / "repos.jsonl"),
        ("gists", lambda: paginated_api("gists?per_page=100", max_pages=max_pages), out / "raw" / "gists.jsonl"),
        ("events", lambda: paginated_api(f"users/{login}/events/public?per_page=100", max_pages=max_pages), out / "raw" / "events.jsonl"),
    ]
    for name, fn, path in stages:
        try:
            print(f"collecting {name}...", flush=True)
            rows = fn()
            manifest["files"][str(path)] = write_jsonl(path, rows)
        except Exception as exc:
            append_error(out, name, exc)
            manifest["errors"].append({"stage": name, "error": str(exc)})

    searches = [
        ("prs-authored", build_search_query("pr", login, "authored", since), out / "raw" / "prs-authored.jsonl"),
        ("prs-involved", build_search_query("pr", login, "involved", since), out / "raw" / "prs-involved.jsonl"),
        ("prs-reviewed", build_search_query("pr", login, "reviewed", since), out / "raw" / "reviews.jsonl"),
        ("issues-authored", build_search_query("issue", login, "authored", since), out / "raw" / "issues-authored.jsonl"),
        ("issues-involved", build_search_query("issue", login, "involved", since), out / "raw" / "issues-involved.jsonl"),
    ]
    for name, query, path in searches:
        try:
            print(f"collecting {name}: {query}", flush=True)
            rows = partitioned_search_issues(query, max_pages=max_pages)
            manifest["files"][str(path)] = write_jsonl(path, rows)
        except Exception as exc:
            append_error(out, name, exc)
            manifest["errors"].append({"stage": name, "error": str(exc)})

    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_json(out / "state" / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages per paginated collection/search for smoke tests")
    parser.add_argument("--since", default=None, help="Only search PR/issues updated on/after YYYY-MM-DD")
    args = parser.parse_args()
    manifest = collect(Path(args.out).expanduser().resolve(), max_pages=args.max_pages, since=args.since)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0 if not manifest.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
