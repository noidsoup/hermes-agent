#!/usr/bin/env python3
"""Classify commit history into reusable workflow signals.

Reads the local GitHub intelligence vault and writes derived reports only. The
output is meant for Hermes preflight orientation: it summarizes patterns without
copying private code or commit bodies into global memory.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DATA = Path.home() / "Data" / "github-intelligence"
SECRET_RE = re.compile(
    r"(?i)(sk-[a-z0-9_-]{12,}|gh[pousr]_[a-z0-9_]{20,}|xox[baprs]-[a-z0-9-]{20,}|api[_-]?key\s*[:=]\s*['\"]?[a-z0-9_-]{16,}|token\s*[:=]\s*['\"]?[a-z0-9_-]{16,})"
)

WORKFLOWS: dict[str, dict[str, Any]] = {
    "bugfix_loops": {
        "label": "Bugfix loops",
        "description": "Fix-oriented churn; useful for debugging patterns and regression-prone areas.",
        "patterns": [r"^fix\b", r"\bfix(es|ed)?\b", r"bug", r"hotfix", r"regression", r"broken"],
    },
    "feature_delivery": {
        "label": "Feature delivery",
        "description": "Feature/addition work; useful for repo capability and product-area discovery.",
        "patterns": [r"^feat\b", r"^feature\b", r"\badd(s|ed)?\b", r"implement", r"support"],
    },
    "ci_github_actions": {
        "label": "CI / GitHub Actions",
        "description": "Workflow, runner, build, and CI changes; useful before touching automation gates.",
        "patterns": [r"github actions", r"\bgha\b", r"\bci\b", r"workflow", r"runner", r"build", r"checks?"],
    },
    "automation_cron_sync": {
        "label": "Automation / cron / sync",
        "description": "Schedulers, queues, webhooks, sync jobs, and scripts.",
        "patterns": [r"automation", r"cron", r"launchd", r"webhook", r"queue", r"sync", r"script", r"scheduler", r"watchdog"],
    },
    "airtable_apfs": {
        "label": "Airtable / APFS data automation",
        "description": "Airtable/FUB/SeniorPlace/APFS data workflows and their edge cases.",
        "patterns": [r"airtable", r"\bfub\b", r"senior\s*place", r"seniorplace", r"apfs", r"invoice", r"contract", r"community"],
    },
    "agent_cursor_hermes": {
        "label": "Agent / Cursor / Hermes",
        "description": "Agentic coding, Hermes, Cursor, Copilot, Claude/Codex, gateway, and tool work.",
        "patterns": [r"hermes", r"cursor", r"agent", r"copilot", r"claude", r"codex", r"gateway", r"tool"],
    },
    "memory_wiki_docs": {
        "label": "Memory / wiki / docs",
        "description": "SimpleMem, wiki, runbooks, docs, and session-memory maintenance.",
        "patterns": [r"simplemem", r"memory", r"wiki", r"runbook", r"docs?", r"documentation", r"session"],
    },
    "tests_quality": {
        "label": "Tests / quality gates",
        "description": "Tests, validators, linting, QA, and quality audit changes.",
        "patterns": [r"\btest(s|ing)?\b", r"pytest", r"spec", r"validator", r"lint", r"quality", r"audit"],
    },
    "refactor_cleanup": {
        "label": "Refactor / cleanup",
        "description": "Refactors, cleanups, renames, and internal simplification.",
        "patterns": [r"refactor", r"cleanup", r"rename", r"simplif", r"dedupe", r"remove unused"],
    },
    "deploy_release_ops": {
        "label": "Deploy / release ops",
        "description": "Deployment, release, production, Netlify/Vercel, Docker, and ops changes.",
        "patterns": [r"deploy", r"release", r"production", r"netlify", r"vercel", r"docker", r"container", r"migration"],
    },
}

COMPILED = {key: [re.compile(p, re.I) for p in meta["patterns"]] for key, meta in WORKFLOWS.items()}
STOP = {
    "the", "and", "for", "with", "from", "this", "that", "into", "your", "have", "will", "are", "was", "were",
    "not", "but", "you", "all", "add", "fix", "feat", "update", "github", "https", "http", "com", "null", "true", "false",
    "chore", "merge", "pull", "request", "branch", "main", "origin",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def redact(text: str) -> str:
    return SECRET_RE.sub("[REDACTED_SECRET]", text or "")


def commit_subject(commit: dict[str, Any]) -> str:
    return str(commit.get("subject") or commit.get("message") or "").split("\n", 1)[0]


def commit_repo(commit: dict[str, Any]) -> str:
    return str(commit.get("repo") or "unknown")


def is_remote_reachable(commit: dict[str, Any]) -> bool:
    refs = commit.get("refs") or []
    return any(isinstance(ref, str) and "/" in ref and not ref.startswith("tags/") for ref in refs)


def classify_subject(subject: str) -> list[str]:
    text = subject.lower()
    return [key for key, regexes in COMPILED.items() if any(rx.search(text) for rx in regexes)]


def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 4 and t not in STOP]


def classify_commits(commits: list[dict[str, Any]]) -> dict[str, Any]:
    workflows: dict[str, dict[str, Any]] = {
        key: {
            "key": key,
            "label": meta["label"],
            "description": meta["description"],
            "count": 0,
            "remote_ref_count": 0,
            "repos": Counter(),
            "terms": Counter(),
            "examples": [],
        }
        for key, meta in WORKFLOWS.items()
    }
    repo_profiles: dict[str, dict[str, Any]] = defaultdict(lambda: {"total": 0, "remote_ref_count": 0, "workflows": Counter(), "terms": Counter(), "examples": defaultdict(list)})
    unmatched = 0

    for commit in commits:
        subject = redact(commit_subject(commit))
        repo = commit_repo(commit)
        remote_ref = is_remote_reachable(commit)
        matched = classify_subject(subject)
        if not matched:
            unmatched += 1
        repo_profiles[repo]["total"] += 1
        if remote_ref:
            repo_profiles[repo]["remote_ref_count"] += 1
        for key in matched:
            wf = workflows[key]
            wf["count"] += 1
            if remote_ref:
                wf["remote_ref_count"] += 1
            wf["repos"][repo] += 1
            wf["terms"].update(tokenize(subject))
            if len(wf["examples"]) < 8:
                wf["examples"].append({
                    "repo": repo,
                    "sha": str(commit.get("sha") or "")[:12],
                    "committed_at": commit.get("committed_at") or commit.get("authored_at") or "",
                    "subject": subject,
                    "remote_ref": remote_ref,
                })
            rp = repo_profiles[repo]
            rp["workflows"][key] += 1
            rp["terms"].update(tokenize(subject))
            if len(rp["examples"][key]) < 3:
                rp["examples"][key].append(subject)

    workflow_rows = []
    for key, wf in workflows.items():
        row = {
            "key": key,
            "label": wf["label"],
            "description": wf["description"],
            "count": wf["count"],
            "remote_ref_count": wf["remote_ref_count"],
            "top_repos": wf["repos"].most_common(10),
            "top_terms": [term for term, _ in wf["terms"].most_common(12)],
            "examples": wf["examples"],
        }
        workflow_rows.append(row)
    workflow_rows.sort(key=lambda r: (r["count"], r["remote_ref_count"]), reverse=True)

    repo_rows = []
    for repo, profile in repo_profiles.items():
        top_workflows = profile["workflows"].most_common(8)
        if not top_workflows:
            continue
        repo_rows.append({
            "repo": repo,
            "total": profile["total"],
            "remote_ref_count": profile["remote_ref_count"],
            "top_workflows": top_workflows,
            "top_terms": [term for term, _ in profile["terms"].most_common(12)],
            "examples": {key: list(vals) for key, vals in profile["examples"].items()},
        })
    repo_rows.sort(key=lambda r: (sum(c for _, c in r["top_workflows"]), r["remote_ref_count"], r["total"]), reverse=True)

    return {
        "generated_at": now(),
        "total_commits": len(commits),
        "remote_ref_count": sum(1 for c in commits if is_remote_reachable(c)),
        "local_only_or_tag_only_count": sum(1 for c in commits if not is_remote_reachable(c)),
        "unmatched_count": unmatched,
        "workflows": workflow_rows,
        "repo_profiles": repo_rows,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, classified: dict[str, Any], top: int = 30) -> None:
    lines = [
        "# Commit Workflow Classifier",
        "",
        f"Generated: `{classified['generated_at']}`",
        "",
        "This report classifies local GitHub commit subjects into reusable workflow signals. It is for orientation only: verify against live repo files before editing, and prefer PRs/issues for narrative context.",
        "",
        "## Corpus Shape",
        "",
        f"- Commit records: `{classified['total_commits']}`",
        f"- Remote-ref reachable: `{classified['remote_ref_count']}`",
        f"- Local-only/tag-only/no-ref: `{classified['local_only_or_tag_only_count']}`",
        f"- Unmatched by workflow regexes: `{classified['unmatched_count']}`",
        "",
        "## Workflow Clusters",
        "",
    ]
    for wf in classified["workflows"]:
        if wf["count"] == 0:
            continue
        lines += [
            f"### {wf['label']} (`{wf['key']}`)",
            "",
            f"- Count: `{wf['count']}`",
            f"- Remote-ref reachable: `{wf['remote_ref_count']}`",
            f"- Description: {wf['description']}",
            f"- Top terms: {', '.join('`' + t + '`' for t in wf['top_terms'][:10])}",
            "- Top repos:",
        ]
        for repo, count in wf["top_repos"][:8]:
            lines.append(f"  - `{repo}`: {count}")
        lines.append("- Examples:")
        for ex in wf["examples"][:5]:
            reach = "remote" if ex["remote_ref"] else "local/tag/no-ref"
            lines.append(f"  - `{ex['repo']}` `{ex['sha']}` ({reach}) — {ex['subject']}")
        lines.append("")

    lines += ["## Repo Playbook Seeds", ""]
    for repo in classified["repo_profiles"][:top]:
        lines += [
            f"### `{repo['repo']}`",
            "",
            f"- Commit records: `{repo['total']}`; remote-ref reachable: `{repo['remote_ref_count']}`",
            f"- Dominant workflows: {', '.join(f'`{key}` ({count})' for key, count in repo['top_workflows'][:6])}",
            f"- Top terms: {', '.join('`' + t + '`' for t in repo['top_terms'][:10])}",
            "- Preflight action: query `github_history_query` with this repo plus the dominant workflow or exact error, then inspect live repo instructions.",
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact("\n".join(lines) + "\n"), encoding="utf-8")


def run(data: Path, top: int = 30) -> dict[str, Any]:
    commits = read_jsonl(data / "raw" / "commits.jsonl")
    classified = classify_commits(commits)
    reports = data / "reports"
    state = data / "state"
    write_markdown(reports / "commit-workflows.md", classified, top=top)
    write_json(state / "commit-workflows.json", classified)
    return {
        "ok": True,
        "commits": classified["total_commits"],
        "workflows": len([w for w in classified["workflows"] if w["count"]]),
        "report": str(reports / "commit-workflows.md"),
        "json": str(state / "commit-workflows.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()
    data = Path(args.data).expanduser().resolve()
    print(json.dumps(run(data, top=args.top), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
