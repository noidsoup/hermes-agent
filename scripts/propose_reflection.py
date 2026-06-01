#!/usr/bin/env python3
"""Propose durable reflection candidates for the memory oracle review queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VOLATILE_PATTERNS = [
    r"\bcurrent\b", r"\btoday\b", r"\bopen PR\b", r"\bcommit [0-9a-f]{7,}\b",
    r"\btoken\b", r"\bsecret\b", r"\bpassword\b", r"\bapi[_ -]?key\b",
]


def _rid(question: str, sources: list[str]) -> str:
    return "cand-" + hashlib.sha256((question + "\0" + "\0".join(sources)).encode()).hexdigest()[:12]


def _risk(text: str) -> list[str]:
    hits = []
    for pat in VOLATILE_PATTERNS:
        if re.search(pat, text, flags=re.I):
            hits.append(pat)
    return hits


def propose(repo: Path, question: str, answer: str, sources: list[str], approve: bool = False) -> dict:
    text = question + "\n" + answer + "\n" + "\n".join(sources)
    risks = _risk(text)
    rec = {
        "id": _rid(question, sources),
        "question": question,
        "answer": answer,
        "sources": sources,
        "type": "candidate",
        "stability": "stable-candidate",
        "created_at": datetime.now(timezone.utc).date().isoformat(),
        "risk_flags": risks,
        "status": "approved" if approve and not risks else "candidate" if not risks else "quarantined",
        "generator": "scripts/propose_reflection.py:v0",
    }
    memory_dir = repo / "wiki" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    target_name = "approved.jsonl" if rec["status"] == "approved" else "rejected.jsonl" if risks else "candidates.jsonl"
    target = memory_dir / target_name
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    return {"written": str(target), "record": rec}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--question", required=True)
    parser.add_argument("--answer", required=True)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()
    result = propose(Path(args.repo).expanduser().resolve(), args.question, args.answer, args.source, args.approve)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
