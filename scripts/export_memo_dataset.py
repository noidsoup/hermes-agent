#!/usr/bin/env python3
"""Export memory-oracle reflections as a deterministic MeMo experiment dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def export(repo: Path, eval_ratio: float = 0.15) -> dict:
    src = repo / "wiki" / "memory" / "reflections.jsonl"
    out_dir = repo / "experiments" / "memo" / "dataset"
    out_dir.mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = sorted(records, key=lambda r: r.get("id", ""))
    eval_every = max(2, round(1 / eval_ratio))
    train, evals = [], []
    for i, rec in enumerate(records):
        item = {
            "messages": [
                {"role": "user", "content": rec["question"]},
                {"role": "assistant", "content": rec["answer"]},
            ],
            "metadata": {"id": rec.get("id"), "sources": rec.get("sources", []), "type": rec.get("type")},
        }
        (evals if i % eval_every == 0 else train).append(item)
    for name, data in [("reflections_train.jsonl", train), ("reflections_eval.jsonl", evals)]:
        with (out_dir / name).open("w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    return {"train": len(train), "eval": len(evals), "out_dir": str(out_dir)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--eval-ratio", type=float, default=0.15)
    args = parser.parse_args()
    print(json.dumps(export(Path(args.repo).expanduser().resolve(), args.eval_ratio), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
