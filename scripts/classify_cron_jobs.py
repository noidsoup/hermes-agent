#!/usr/bin/env python3
"""Classify Hermes cron jobs by category, risk, delivery, and side effects."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"


def _load_jobs() -> list[dict]:
    path = HERMES_HOME / "cron" / "jobs.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        jobs = data.get("jobs", data)
        return list(jobs.values()) if isinstance(jobs, dict) else jobs if isinstance(jobs, list) else []
    return []


def classify(job: dict) -> dict:
    name = job.get("name", "")
    script = job.get("script") or ""
    prompt = job.get("prompt_preview") or job.get("prompt") or ""
    hay = " ".join([name, script, prompt]).lower()
    category = "ops"
    if "apfs" in hay or "airtable" in hay:
        category = "apfs"
    elif "wiki" in hay or "memory" in hay or "simplemem" in hay or "ai-memory" in hay:
        category = "knowledge"
    elif "health" in hay:
        category = "health"
    elif "pr-" in hay or "github" in hay:
        category = "github"
    elif "daily" in hay or "community" in hay:
        category = "personal"

    risk = "read_only"
    side_effects: list[str] = []
    if job.get("no_agent") is not True:
        risk = "agent_autonomy"
        side_effects.append("LLM agent can use enabled tools")
    if any(k in hay for k in ["sync", "refresh", "drain", "sweep", "commit", "push", "maintain", "backup"]):
        risk = "writes_or_external_side_effects" if risk == "read_only" else "high_autonomy"
        side_effects.append("may write local/external state")
    if "push" in hay or "github" in hay or "pr-" in hay:
        side_effects.append("may touch GitHub")
    return {
        "name": name,
        "schedule": job.get("schedule"),
        "deliver": job.get("deliver"),
        "script": script or "agent",
        "category": category,
        "risk": risk,
        "side_effects": side_effects,
        "enabled": job.get("enabled", True),
        "state": job.get("state"),
    }


def render(rows: list[dict]) -> str:
    lines = ["---", "title: Cron Risk Report", "type: report", f"updated: {datetime.now().isoformat(timespec='seconds')}", "---", "", "# Cron Risk Report", ""]
    for row in sorted(rows, key=lambda r: (r["category"], r["name"])):
        lines.extend([
            f"## {row['name']}",
            f"- Category: `{row['category']}`",
            f"- Risk: `{row['risk']}`",
            f"- Schedule: `{row['schedule']}`",
            f"- Delivery: `{row['deliver']}`",
            f"- Script: `{row['script']}`",
            f"- Side effects: {', '.join(row['side_effects']) if row['side_effects'] else 'none inferred'}",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output", default="wiki/cron-risk-report.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = [classify(j) for j in _load_jobs()]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    out = Path(args.output)
    if not out.is_absolute():
        out = Path(args.repo).expanduser().resolve() / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
