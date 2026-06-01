#!/usr/bin/env python3
"""Query the lightweight MeMo-style reflection memory oracle."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

DEFAULT_MEMORY = Path("wiki/memory/reflections.jsonl")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "when",
    "where", "which", "who", "why", "with", "about", "does", "do", "know",
}


SYNONYMS = {
    "stored": ["store", "candidates"],
    "storing": ["store", "candidates"],
    "avoid": ["bad", "not"],
    "forbidden": ["bad", "not"],
    "secrets": ["secret", "credentials", "tokens"],
    "credential": ["credentials", "secret"],
    "credentials": ["credential", "secret"],
}


def _normalize_token(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _tokens(text: str, *, expand: bool = False) -> list[str]:
    raw = [t for t in re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]{1,}", text.lower()) if t not in STOPWORDS]
    toks: list[str] = []
    for tok in raw:
        norm = _normalize_token(tok)
        toks.append(norm)
        if expand:
            toks.extend(_normalize_token(s) for s in SYNONYMS.get(tok, []))
            toks.extend(_normalize_token(s) for s in SYNONYMS.get(norm, []))
    return toks


def _load(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.is_file():
        raise SystemExit(f"memory oracle not found: {path}\nRun scripts/generate_reflections.py first.")
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{i}: {exc}") from exc
        records.append(rec)
    return records


def _score(query: str, rec: dict, df: Counter[str], n_docs: int) -> float:
    q_tokens = _tokens(query, expand=True)
    if not q_tokens:
        return 0.0
    fields = " ".join(
        str(rec.get(k, "")) for k in ("question", "answer", "type", "stability")
    )
    fields += " " + " ".join(rec.get("sources") or [])
    doc_tokens = _tokens(fields)
    tf = Counter(doc_tokens)
    score = 0.0
    for tok in q_tokens:
        if tok not in tf:
            continue
        idf = math.log((1 + n_docs) / (1 + df[tok])) + 1
        question_tokens = _tokens(str(rec.get("question", "")))
        boost = 3.5 if tok in question_tokens else 1.0
        if tok in {"not", "avoid", "bad", "secret", "secrets", "volatile", "current"}:
            boost *= 2.0
        score += (1 + math.log(tf[tok])) * idf * boost
    return score


def search(records: list[dict], query: str, limit: int, min_score: float = 0.0) -> list[tuple[float, dict]]:
    df: Counter[str] = Counter()
    for rec in records:
        toks = set(_tokens(" ".join(str(rec.get(k, "")) for k in ("question", "answer"))))
        toks.update(_tokens(" ".join(rec.get("sources") or [])))
        df.update(toks)
    ranked = [(_score(query, rec, df, len(records)), rec) for rec in records]
    ranked = [(s, r) for s, r in ranked if s > 0 and s >= min_score]
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:limit]


def verify_result_sources(rec: dict, repo: Path) -> list[dict]:
    checks: list[dict] = []
    for source in rec.get("sources") or []:
        source_path = repo / source
        checks.append({
            "source": source,
            "exists": source_path.exists(),
            "path": str(source_path),
        })
    return checks


def _print_text(results: list[tuple[float, dict]], repo: Path | None = None, verify_sources: bool = False) -> None:
    if not results:
        print("No matching reflections found.")
        return
    for idx, (score, rec) in enumerate(results, 1):
        print(f"[{idx}] {rec.get('question')}  (score {score:.2f})")
        print(f"Answer: {rec.get('answer')}")
        sources = rec.get("sources") or []
        if sources:
            print("Sources: " + ", ".join(sources))
        if verify_sources and repo is not None:
            checks = verify_result_sources(rec, repo)
            ok = sum(1 for item in checks if item["exists"])
            print(f"Source verification: {ok}/{len(checks)} found")
        print(f"Type: {rec.get('type', '?')} · Stability: {rec.get('stability', '?')} · ID: {rec.get('id')}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language memory query")
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--memory", default=str(DEFAULT_MEMORY), help="Memory JSONL path relative to repo")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.0, help="Suppress matches below this score")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--verify-sources", action="store_true", help="Check whether result source files currently exist")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    memory = Path(args.memory)
    if not memory.is_absolute():
        memory = repo / memory
    records = _load(memory)
    results = search(records, args.query, args.limit, min_score=args.min_score)
    if args.json:
        payload = []
        for score, rec in results:
            item = dict(score=score, **rec)
            if args.verify_sources:
                item["source_verification"] = verify_result_sources(rec, repo)
            payload.append(item)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _print_text(results, repo=repo, verify_sources=args.verify_sources)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
