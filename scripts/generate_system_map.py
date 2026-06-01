#!/usr/bin/env python3
"""Generate a concise system map for the local Hermes setup."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
HERMES_HOME = Path.home() / ".hermes"


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as exc:
        return 1, str(exc)


def _json_load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _count_jsonl(path: Path) -> int:
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except Exception:
        return 0


def _display_schedule(schedule: Any) -> str:
    if isinstance(schedule, dict):
        return str(schedule.get("display") or schedule.get("expr") or schedule)
    return str(schedule)


def _cron_jobs() -> list[dict]:
    jobs_path = HERMES_HOME / "cron" / "jobs.json"
    data = _json_load(jobs_path, [])
    if isinstance(data, dict):
        return list(data.get("jobs", {}).values()) if isinstance(data.get("jobs"), dict) else data.get("jobs", [])
    return data if isinstance(data, list) else []


def generate(repo: Path) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    reflections = repo / "wiki" / "memory" / "reflections.jsonl"
    health = _json_load(repo / "wiki" / "memory" / "health.json", {})
    jobs = _cron_jobs()
    active = [j for j in jobs if j.get("enabled", True) and j.get("state") != "paused"]
    paused = [j for j in jobs if not j.get("enabled", True) or j.get("state") == "paused"]
    git_rc, git_head = _run(["git", "log", "-1", "--oneline"], cwd=repo)
    backup_dir = HERMES_HOME / "backups" / "git"
    bundles = sorted(backup_dir.glob("*.bundle"), key=lambda p: p.stat().st_mtime, reverse=True)[:3] if backup_dir.exists() else []

    lines = [
        "---",
        "title: Hermes System Map",
        "type: report",
        f"updated: {now}",
        "---",
        "",
        "# Hermes System Map",
        "",
        f"Generated: `{now}`",
        f"Repo: `{repo}`",
        f"Git head: `{git_head if git_rc == 0 else 'unknown'}`",
        "",
        "## Memory Layers",
        "",
        "- **Hermes profile memory**: user preferences, stable environment facts, durable conventions.",
        "- **Skills**: reusable procedures and workflows.",
        "- **Session search**: past conversation recall.",
        "- **Wiki/SimpleMem**: repo-local project knowledge.",
        "- **Memory oracle**: source-linked MeMo-style reflection QA for stable knowledge.",
        "- **Live tools**: current truth for files, git, cron, Airtable, logs, processes.",
        "",
        "## Memory Oracle",
        "",
        f"- Reflections: `{_count_jsonl(reflections)}`",
        f"- Health: `{health.get('ok', 'unknown')}`",
        f"- Last checked: `{health.get('checked_at', 'unknown')}`",
        f"- Eval summary: `{health.get('eval_summary', 'unknown')}`",
        "- Rule: use for stable conceptual orientation; verify important/current claims with sources/tools.",
        "",
        "## Cron Overview",
        "",
        f"- Active jobs: `{len(active)}`",
        f"- Paused/disabled jobs: `{len(paused)}`",
        "",
    ]
    for job in sorted(active, key=lambda j: j.get("name", "")):
        lines.append(
            f"- `{job.get('name')}` — `{_display_schedule(job.get('schedule'))}` — "
            f"deliver `{job.get('deliver')}` — script `{job.get('script', 'agent')}`"
        )
    lines.extend(["", "## Backup State", ""])
    if bundles:
        for b in bundles:
            lines.append(f"- Local bundle: `{b}`")
    else:
        lines.append("- No local git bundle backups found.")
    lines.extend([
        "",
        "## Operating Principles",
        "",
        "- Memory for stable understanding.",
        "- Tools for current truth.",
        "- Sources for verification.",
        "- Cron for hands-off upkeep.",
        "- Secrets stay out of wiki, SimpleMem, ai-memory, reflections, and backups.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--output", default=str(REPO_ROOT / "wiki" / "system-map.md"))
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    out = Path(args.output).expanduser()
    if not out.is_absolute():
        out = repo / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(generate(repo), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
