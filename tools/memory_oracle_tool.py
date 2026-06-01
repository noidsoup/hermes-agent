#!/usr/bin/env python3
"""Native Hermes tool for querying repo-local memory oracle reflections."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from tools.registry import registry

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from query_memory_oracle import _load, search, verify_result_sources  # noqa: E402


MEMORY_ORACLE_QUERY_SCHEMA = {
    "name": "memory_oracle_query",
    "description": (
        "Query a repo-local MeMo-style reflection memory oracle for stable project knowledge. "
        "Use before raw file search for architecture, workflows, conventions, and durable pitfalls. "
        "Do not use as authority for current state; verify important claims with sources/tools."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Natural-language question to ask the memory oracle."},
            "repo": {
                "type": "string",
                "description": "Repository root containing wiki/memory/reflections.jsonl. Defaults to cwd, then Hermes source repo.",
            },
            "limit": {"type": "integer", "description": "Maximum results to return.", "default": 5},
            "min_score": {"type": "number", "description": "Suppress matches below this score.", "default": 10},
            "verify_sources": {
                "type": "boolean",
                "description": "Check whether listed source files currently exist under the repo.",
                "default": False,
            },
        },
        "required": ["question"],
    },
}


def _candidate_roots(repo: str | None) -> list[Path]:
    roots: list[Path] = []
    if repo:
        roots.append(Path(repo).expanduser())
    roots.append(Path.cwd())
    roots.append(REPO_ROOT)
    # Preserve order while de-duping resolved paths when possible.
    seen: set[str] = set()
    out: list[Path] = []
    for root in roots:
        try:
            key = str(root.resolve())
        except OSError:
            key = str(root)
        if key not in seen:
            seen.add(key)
            out.append(root)
    return out


def _resolve_memory(repo: str | None) -> tuple[Path, Path]:
    if repo:
        root = Path(repo).expanduser()
        return root, root / "wiki" / "memory" / "reflections.jsonl"
    for root in _candidate_roots(None):
        memory = root / "wiki" / "memory" / "reflections.jsonl"
        if memory.is_file():
            return root, memory
    fallback = Path.cwd()
    return fallback, fallback / "wiki" / "memory" / "reflections.jsonl"


def memory_oracle_query(
    question: str,
    repo: str | None = None,
    limit: int = 5,
    min_score: float = 10.0,
    verify_sources: bool = False,
) -> dict[str, Any]:
    root, memory = _resolve_memory(repo)
    if not memory.is_file():
        return {
            "success": False,
            "query": question,
            "repo": str(root),
            "memory_path": str(memory),
            "no_hit": True,
            "error": "memory oracle file not found",
            "results": [],
        }

    records = _load(memory)
    safe_limit = max(1, min(20, int(limit)))
    safe_min_score = max(0.0, float(min_score))
    matches = search(records, question, safe_limit, min_score=safe_min_score)
    results: list[dict[str, Any]] = []
    for score, rec in matches:
        item = dict(rec)
        item["score"] = round(score, 4)
        if verify_sources:
            item["source_verification"] = verify_result_sources(rec, root)
        results.append(item)

    return {
        "success": True,
        "query": question,
        "repo": str(root),
        "memory_path": str(memory),
        "min_score": safe_min_score,
        "no_hit": not results,
        "results": results,
    }


def _handle_memory_oracle_query(args: dict[str, Any], **kw) -> str:
    result = memory_oracle_query(
        question=str(args.get("question") or args.get("query") or ""),
        repo=args.get("repo"),
        limit=int(args.get("limit", 5) or 5),
        min_score=float(args.get("min_score", 10) or 0),
        verify_sources=bool(args.get("verify_sources", False)),
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


def _check_memory_oracle_reqs() -> bool:
    # Always expose the tool; it returns a structured no-hit/missing-file result when unavailable.
    return True


registry.register(
    name="memory_oracle_query",
    toolset="memory_oracle",
    schema=MEMORY_ORACLE_QUERY_SCHEMA,
    handler=_handle_memory_oracle_query,
    check_fn=_check_memory_oracle_reqs,
    emoji="🧠",
    max_result_size_chars=50_000,
)
