#!/usr/bin/env python3
"""Create sanitized local/Git backups for critical Hermes state."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_NAMES = {
    ".env",
    ".env.local",
    ".envrc",
    ".npmrc",
    ".pypirc",
    "auth.json",
    "credentials.json",
    "state.db",
    "state.db-wal",
    "state.db-shm",
    "id_rsa",
    "id_ed25519",
}
EXCLUDE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
EXCLUDE_PARTS = {
    "logs",
    "sessions",
    ".tmp",
    "tmp",
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "secrets",
    "credentials",
    "audio_cache",
    "media_cache",
}
REDACTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd)(\s*[:=]\s*)(['\"]?)[^\s'\"]{6,}(['\"]?)"), r"\1\2\3REDACTED\4"),
    (re.compile(r"sk-[A-Za-z0-9_-]{12,}"), "sk-REDACTED"),
    (re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"), "gh_REDACTED"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "github_pat_REDACTED"),
    (re.compile(r"(?s)-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"), "-----BEGIN PRIVATE KEY-----\nREDACTED\n-----END PRIVATE KEY-----"),
]


def _is_excluded(src: Path) -> bool:
    if src.name in EXCLUDE_NAMES or src.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return any(part in EXCLUDE_PARTS for part in src.parts)


def _redact(text: str) -> str:
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _safe_copy(src: Path, dst: Path, manifest: dict) -> None:
    if _is_excluded(src):
        manifest.setdefault("excluded", []).append(str(src))
        return
    if src.is_dir():
        for child in src.iterdir():
            _safe_copy(child, dst / child.name, manifest)
        return
    try:
        data = src.read_bytes()
    except OSError:
        return
    if b"\0" in data[:4096]:
        manifest.setdefault("excluded", []).append(str(src))
        return
    text = data.decode("utf-8", errors="ignore")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(_redact(text), encoding="utf-8")


def _assert_archive_sanitized(tar_path: Path) -> list[str]:
    findings: list[str] = []
    suspicious = re.compile(r"sk-[A-Za-z0-9_-]{12,}|gh[opsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN [A-Z ]*PRIVATE KEY|(password|token|secret|api[_-]?key)\s*[:=]\s*[^\s'\"]{6,}", re.I)
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or member.size > 1_000_000:
                continue
            f = tar.extractfile(member)
            if not f:
                continue
            text = f.read().decode("utf-8", errors="ignore")
            if "REDACTED" in text:
                continue
            if suspicious.search(text):
                findings.append(member.name)
                if len(findings) >= 20:
                    break
    return findings


def create_backup(repo: Path, push: bool = False) -> dict:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = HERMES_HOME / "backups" / "state" / f"hermes-state-{stamp}"
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest = {"created_at": stamp, "repo": str(repo), "included": [], "excluded": []}

    for rel in ["AGENTS.md", "wiki", "skills", "scripts", "config"]:
        src = repo / rel
        if src.exists():
            _safe_copy(src, backup_root / "repo" / rel, manifest)
            manifest["included"].append(f"repo/{rel}")
    for rel in ["cron/jobs.json", "config.yaml"]:
        src = HERMES_HOME / rel
        if src.exists():
            _safe_copy(src, backup_root / "hermes-home" / rel, manifest)
            manifest["included"].append(f"hermes-home/{rel}")

    (backup_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    tar_path = backup_root.with_suffix(".tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(backup_root, arcname=backup_root.name)
    shutil.rmtree(backup_root)

    findings = _assert_archive_sanitized(tar_path)
    result = {"success": not findings, "tarball": str(tar_path), "pushed": False, "secret_findings": findings}
    if findings:
        return result
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
    result = create_backup(Path(args.repo).expanduser().resolve(), push=args.push)
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 2


if __name__ == "__main__":
    raise SystemExit(main())
