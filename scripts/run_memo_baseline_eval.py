#!/usr/bin/env python3
"""Run baseline evals for the MeMo experiment scaffold."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    eval_cmd = [sys.executable, str(repo / "scripts" / "eval_memory_oracle.py"), "--repo", str(repo)]
    p = subprocess.run(eval_cmd, capture_output=True, text=True, timeout=120)
    payload = {
        "baseline": "retrieval-memory-oracle",
        "returncode": p.returncode,
        "passed": p.returncode == 0,
        "output": p.stdout.strip(),
    }
    print(json.dumps(payload, indent=2))
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main())
