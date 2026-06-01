#!/usr/bin/env python3
"""Hands-off maintenance for the Hermes MeMo-style memory oracle.

Regenerates source-linked reflections, runs evals, and prints only when
something changed or failed. Intended for cron/no_agent use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "generate_reflections.py"
EVAL_RUNNER = REPO_ROOT / "scripts" / "eval_memory_oracle.py"
REFLECTIONS = REPO_ROOT / "wiki" / "memory" / "reflections.jsonl"
STATE_PATH = Path.home() / ".hermes" / "state" / "memory_oracle_maintenance.json"


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _count_jsonl(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout)


def _write_state(payload: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _maybe_git_commit(enabled: bool, message: str) -> str:
    if not enabled:
        return ""
    tracked = ["wiki/memory/reflections.jsonl", "wiki/memory/evals.jsonl", "wiki/concepts/memory-oracle.md"]
    status = _run(["git", "status", "--porcelain", *tracked], timeout=30)
    if status.returncode != 0 or not status.stdout.strip():
        return ""
    add = _run(["git", "add", *tracked], timeout=30)
    if add.returncode != 0:
        return f"git add failed: {(add.stderr or add.stdout).strip()[:500]}"
    commit = _run(["git", "commit", "-m", message], timeout=60)
    if commit.returncode != 0:
        return f"git commit skipped/failed: {(commit.stderr or commit.stdout).strip()[:500]}"
    push = _run(["git", "push"], timeout=120)
    if push.returncode != 0:
        return f"git commit ok, push failed: {(push.stderr or push.stdout).strip()[:500]}"
    return "git committed and pushed memory oracle updates"


def maintain(max_records: int, include_website: bool, min_records: int, commit: bool, verbose: bool) -> int:
    before_hash = _sha256(REFLECTIONS)
    before_count = _count_jsonl(REFLECTIONS)

    gen_cmd = [sys.executable, str(GENERATOR), "--repo", str(REPO_ROOT), "--max-records", str(max_records)]
    if include_website:
        gen_cmd.append("--include-website")
    gen = _run(gen_cmd, timeout=180)

    after_hash = _sha256(REFLECTIONS)
    after_count = _count_jsonl(REFLECTIONS)
    changed = before_hash != after_hash

    eval_run = _run([sys.executable, str(EVAL_RUNNER), "--repo", str(REPO_ROOT)], timeout=120)
    ok = gen.returncode == 0 and eval_run.returncode == 0 and after_count >= min_records

    state = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "ok": ok,
        "changed": changed,
        "before_count": before_count,
        "after_count": after_count,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "generator_returncode": gen.returncode,
        "eval_returncode": eval_run.returncode,
    }
    _write_state(state)

    lines: list[str] = []
    if not ok:
        lines.extend([
            "Memory oracle maintenance FAILED",
            f"repo: {REPO_ROOT}",
            f"reflections: {before_count} -> {after_count} (minimum {min_records})",
            f"generator rc: {gen.returncode}",
            (gen.stdout + gen.stderr).strip()[:1200],
            f"eval rc: {eval_run.returncode}",
            (eval_run.stdout + eval_run.stderr).strip()[:1600],
        ])
    elif changed or verbose:
        lines.extend([
            "Memory oracle maintenance OK",
            f"repo: {REPO_ROOT.name}",
            f"reflections: {before_count} -> {after_count}",
            eval_run.stdout.strip(),
        ])
        git_note = _maybe_git_commit(commit and changed, "chore: refresh memory oracle reflections")
        if git_note:
            lines.append(git_note)

    output = "\n".join(line for line in lines if line).strip()
    if output:
        print(output)
    return 0 if ok else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-records", type=int, default=400)
    parser.add_argument("--min-records", type=int, default=250)
    parser.add_argument("--include-website", action="store_true", default=True)
    parser.add_argument("--no-include-website", dest="include_website", action="store_false")
    parser.add_argument("--commit", action="store_true", help="Commit/push changed memory files")
    parser.add_argument("--verbose", action="store_true", help="Print OK report even when unchanged")
    args = parser.parse_args()
    return maintain(args.max_records, args.include_website, args.min_records, args.commit, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
