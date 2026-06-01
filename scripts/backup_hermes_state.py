#!/usr/bin/env python3
"""Create sanitized local/Git backups for critical Hermes state."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_NAMES = {".env", "auth.json", "credentials.json", "state.db", "state.db-wal", "state.db-shm"}
EXCLUDE_PARTS = {"logs", "sessions", ".tmp", "tmp", "__pycache__", ".git", "node_modules", "venv", ".venv"}
SECRET_MARKERS = ["BEGIN PRIVATE KEY", "sk-", "gho_", "github_pat_", "AIRTABLE_API_KEY", "TOKEN="]


def _safe_copy(src: Path, dst: Path) -> None:
    if src.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in src.parts):
        return
    if src.is_dir():
        for child in src.iterdir():
            _safe_copy(child, dst / child.name)
        return
    try:
        data = src.read_bytes()
    except OSError:
        return
    if b"\0" in data[:4096]:
        return
    text = data.decode("utf-8", errors="ignore")
    for marker in SECRET_MARKERS:
        text = text.replace(marker, f"REDACTED_{marker.strip('=_-').upper()}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def create_backup(repo: Path, push: bool = False) -> dict:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = HERMES_HOME / "backups" / "state" / f"hermes-state-{stamp}"
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest = {"created_at": stamp, "repo": str(repo), "included": []}

    for rel in ["AGENTS.md", "wiki", "skills", "scripts", "config"]:
        src = repo / rel
        if src.exists():
            _safe_copy(src, backup_root / "repo" / rel)
            manifest["included"].append(f"repo/{rel}")
    for rel in ["cron/jobs.json", "config.yaml"]:
        src = HERMES_HOME / rel
        if src.exists():
            _safe_copy(src, backup_root / "hermes-home" / rel)
            manifest["included"].append(f"hermes-home/{rel}")

    (backup_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    tar_path = backup_root.with_suffix(".tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(backup_root, arcname=backup_root.name)
    shutil.rmtree(backup_root)

    result = {"success": True, "tarball": str(tar_path), "pushed": False}
    if push:
        branch = f"backup/hermes-state-{stamp}"
        subprocess.run(["git", "branch", "-f", branch], cwd=repo, check=False, capture_output=True, text=True)
        push_run = subprocess.run(["git", "push", "fork", branch], cwd=repo, capture_output=True, text=True, timeout=180)
        result["pushed"] = push_run.returncode == 0
        result["push_output"] = (push_run.stdout + push_run.stderr)[-1200:]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    print(json.dumps(create_backup(Path(args.repo).expanduser().resolve(), push=args.push), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
