#!/usr/bin/env python3
"""Run lightweight evals for the reflection memory oracle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Import sibling query implementation without requiring package installation.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import query_memory_oracle  # noqa: E402

DEFAULT_EVALS = Path("wiki/memory/evals.jsonl")
DEFAULT_MEMORY = Path("wiki/memory/reflections.jsonl")


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{i}: {exc}") from exc
    return rows


def _contains_any(haystacks: list[str], needles: list[str]) -> bool:
    joined = "\n".join(haystacks).lower()
    return all(needle.lower() in joined for needle in needles)


def evaluate(repo: Path, evals_path: Path, memory_path: Path, verbose: bool) -> int:
    evals = _load_jsonl(evals_path)
    records = query_memory_oracle._load(memory_path)  # intentional local script API reuse
    failures: list[str] = []

    for idx, case in enumerate(evals, 1):
        query = case["query"]
        min_score = float(case.get("min_score", 0.0))
        limit = int(case.get("limit", 3))
        expect_hit = bool(case.get("expect_hit", True))
        results = query_memory_oracle.search(records, query, limit=limit, min_score=min_score)
        hit = bool(results)
        status = "PASS"
        reason = ""
        if expect_hit and not hit:
            status = "FAIL"
            reason = f"expected hit >= {min_score}, got no results"
        elif not expect_hit and hit:
            status = "FAIL"
            reason = f"expected no hit >= {min_score}, got score {results[0][0]:.2f}: {results[0][1].get('question')}"
        elif hit:
            top_score, top = results[0]
            source_needles = case.get("must_source_contains") or []
            answer_needles = case.get("must_answer_contains") or []
            if source_needles and not _contains_any(top.get("sources") or [], source_needles):
                status = "FAIL"
                reason = f"top sources {top.get('sources')} missing {source_needles}"
            elif answer_needles and not _contains_any([top.get("answer", "")], answer_needles):
                status = "FAIL"
                reason = f"top answer missing {answer_needles}"
            elif verbose:
                reason = f"score {top_score:.2f}: {top.get('question')}"
        elif verbose:
            reason = "no hit as expected"

        if status == "FAIL":
            failures.append(f"case {idx} {query!r}: {reason}")
        if verbose or status == "FAIL":
            print(f"{status} {idx}. {query} {('- ' + reason) if reason else ''}")

    passed = len(evals) - len(failures)
    print(f"memory oracle evals: {passed}/{len(evals)} passed")
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--evals", default=str(DEFAULT_EVALS), help="Eval JSONL path relative to repo")
    parser.add_argument("--memory", default=str(DEFAULT_MEMORY), help="Memory JSONL path relative to repo")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    evals_path = Path(args.evals)
    memory_path = Path(args.memory)
    if not evals_path.is_absolute():
        evals_path = repo / evals_path
    if not memory_path.is_absolute():
        memory_path = repo / memory_path
    return evaluate(repo, evals_path, memory_path, verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
