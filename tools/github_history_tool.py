"""Local-only query tool for Nicholas's GitHub intelligence vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from tools.registry import registry

DEFAULT_DATA = Path.home() / "Data" / "github-intelligence"
MAX_LIMIT = 25
MAX_SNIPPET_CHARS = 600


def _vault_exists(data_dir: Path | None = None) -> bool:
    data = data_dir or DEFAULT_DATA
    return (data / "raw").is_dir() or (data / "reports").is_dir()


def _safe_resolve_data_dir(data_dir: str | None = None) -> Path:
    """Resolve the vault path without creating files or requiring network access."""
    if not data_dir:
        return DEFAULT_DATA
    return Path(data_dir).expanduser().resolve()


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    try:
        f = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with f:
        # Iterate physical JSONL records. Do not use splitlines(): JSON strings
        # may contain unicode line separators that Python treats as line breaks.
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = json.dumps(obj, ensure_ascii=False, sort_keys=True)
            yield {
                "dataset": path.stem,
                "path": str(path),
                "line": line_no,
                "title": obj.get("title") or obj.get("full_name") or obj.get("name") or obj.get("subject") or obj.get("repo"),
                "url": obj.get("html_url") or obj.get("url"),
                "text": text,
            }
    return


def _iter_markdown(path: Path) -> Iterable[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for line_no, line in enumerate(lines, 1):
        yield {
            "dataset": f"report:{path.stem}",
            "path": str(path),
            "line": line_no,
            "title": path.name,
            "url": None,
            "text": line,
        }


def _iter_records(data_dir: Path) -> Iterable[dict[str, Any]]:
    raw_dir = data_dir / "raw"
    if raw_dir.is_dir():
        for path in sorted(raw_dir.glob("*.jsonl")):
            yield from _iter_jsonl(path)

    reports_dir = data_dir / "reports"
    if reports_dir.is_dir():
        for path in sorted(reports_dir.glob("*.md")):
            yield from _iter_markdown(path)


def _tokenize(query: str) -> list[str]:
    return [token.lower() for token in query.split() if len(token.strip()) >= 2]


def _score(text: str, tokens: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(token) for token in tokens)


def _snippet(text: str, tokens: list[str], max_chars: int = MAX_SNIPPET_CHARS) -> str:
    compact = " ".join(text.split())
    lowered = compact.lower()
    positions = [lowered.find(token) for token in tokens if token in lowered]
    positions = [pos for pos in positions if pos >= 0]
    if not positions:
        return compact[:max_chars]
    start = max(0, min(positions) - 120)
    end = min(len(compact), start + max_chars)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(compact) else ""
    return f"{prefix}{compact[start:end]}{suffix}"


def query_github_history(query: str, limit: int = 10, data_dir: str | None = None) -> dict[str, Any]:
    """Search the local GitHub intelligence vault and return compact evidence-linked hits."""
    query = (query or "").strip()
    if not query:
        return {"success": False, "error": "query is required"}

    tokens = _tokenize(query)
    if not tokens:
        return {"success": False, "error": "query must include at least one 2+ character token"}

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 10
    limit = max(1, min(limit, MAX_LIMIT))

    data = _safe_resolve_data_dir(data_dir)
    if not _vault_exists(data):
        return {
            "success": False,
            "error": f"GitHub intelligence vault not found at {data}",
            "data_dir": str(data),
        }

    hits: list[dict[str, Any]] = []
    scanned = 0
    for rec in _iter_records(data):
        scanned += 1
        score = _score(rec["text"], tokens)
        if score <= 0:
            continue
        hits.append(
            {
                "score": score,
                "dataset": rec["dataset"],
                "path": rec["path"],
                "line": rec["line"],
                "title": rec.get("title"),
                "url": rec.get("url"),
                "snippet": _snippet(rec["text"], tokens),
            }
        )

    hits.sort(key=lambda hit: (hit["score"], hit.get("url") is not None), reverse=True)
    return {
        "success": True,
        "query": query,
        "data_dir": str(data),
        "scanned_records": scanned,
        "count": min(len(hits), limit),
        "hits": hits[:limit],
    }


_SCHEMA = {
    "name": "github_history_query",
    "description": (
        "Search Nicholas's local GitHub intelligence vault (repos, PRs, issues, "
        "reviews, reports) for prior work and evidence. Read-only and local-only; "
        "does not call GitHub or the network. Use before repo work when past "
        "patterns may matter."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search terms, e.g. 'airtable automation', 'cursor task_runner', or 'memory oracle'.",
            },
            "limit": {
                "type": "integer",
                "description": f"Maximum hits to return (1-{MAX_LIMIT}).",
                "default": 10,
                "minimum": 1,
                "maximum": MAX_LIMIT,
            },
            "data_dir": {
                "type": "string",
                "description": "Optional override path for tests or alternate local vaults. Defaults to ~/Data/github-intelligence.",
            },
        },
        "required": ["query"],
    },
}


registry.register(
    name="github_history_query",
    toolset="github_history",
    schema=_SCHEMA,
    handler=lambda args, **kwargs: json.dumps(
        query_github_history(
            query=args.get("query", ""),
            limit=args.get("limit", 10),
            data_dir=args.get("data_dir"),
        ),
        ensure_ascii=False,
    ),
    check_fn=_vault_exists,
    description=_SCHEMA["description"],
    emoji="🐙",
    max_result_size_chars=16000,
)
