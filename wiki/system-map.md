---
title: Hermes System Map
type: report
updated: 2026-06-01T03:15:29
---

# Hermes System Map

Generated: `2026-06-01T03:15:29`
Repo: `/Users/thedao/.hermes/hermes-agent`
Git head: `54e04c801 fix: make GitHub intelligence collection resumable`

## Memory Layers

- **Hermes profile memory**: user preferences, stable environment facts, durable conventions.
- **Skills**: reusable procedures and workflows.
- **Session search**: past conversation recall.
- **Wiki/SimpleMem**: repo-local project knowledge.
- **Memory oracle**: source-linked MeMo-style reflection QA for stable knowledge.
- **Live tools**: current truth for files, git, cron, Airtable, logs, processes.

## Memory Oracle

- Reflections: `399`
- Health: `True`
- Last checked: `2026-06-01T03:15:29`
- Eval summary: `memory oracle evals: 8/8 passed`
- Rule: use for stable conceptual orientation; verify important/current claims with sources/tools.

## Cron Overview

- Active jobs: `19`
- Paused/disabled jobs: `0`

- `ai-memory-nightly-reindex` — `0 3 * * *` — deliver `local` — script `ai-memory-nightly-reindex.sh`
- `apfs-actions-monitor` — `*/30 * * * *` — deliver `local` — script `apfs-actions-monitor.sh`
- `apfs-cat-cpt-stats` — `12 * * * * (hourly at :12)` — deliver `local` — script `apfs-cat-cpt-stats.sh`
- `apfs-fub-sync` — `0 19 * * * (daily ~02:00 UTC)` — deliver `local` — script `apfs-fub-sync.sh`
- `apfs-sp-contracted-sweep` — `0 6 * * 0 (Sun ~06:00 UTC)` — deliver `local` — script `apfs-sp-contracted-sweep.sh`
- `apfs-sp-daily-client-sync` — `0 5 * * * (daily ~12:00 UTC)` — deliver `local` — script `apfs-sp-daily-client-sync.sh`
- `apfs-sp-delta-contract-refresh` — `0 22 * * 6 (Sat ~Sun 05:00 UTC)` — deliver `local` — script `apfs-sp-delta-contract-refresh.sh`
- `apfs-sp-refresh-queue-drain` — `*/15 * * * *` — deliver `local` — script `apfs-sp-refresh-queue-drain.sh`
- `apfs-sp-weekly-sync` — `0 19 1,15 * * (1st & 15th ~02:00 UTC)` — deliver `local` — script `apfs-sp-weekly-sync.sh`
- `hermes-state-backup` — `30 4 * * 0` — deliver `telegram` — script `backup_hermes_state.sh`
- `il-community-hunter` — `0 22 * * *` — deliver `local` — script `il-community-hunter.sh`
- `memory-oracle-maintenance` — `15 3 * * *` — deliver `telegram` — script `maintain_memory_oracle.sh`
- `morning-daily-summary` — `0 8 * * *` — deliver `telegram` — script `morning-daily-summary.sh`
- `nightly-health` — `0 4 * * *` — deliver `telegram` — script `hermes_health_watchdog.py`
- `nightly-self-improvement` — `0 2 * * *` — deliver `telegram` — script `nightly-self-improvement-preflight.sh`
- `nightly-simplemem` — `30 3 * * *` — deliver `telegram` — script `maintain_all_simplemem.py`
- `pr-copilot-postmerge-capture` — `15,45 * * * * (every 30 min at :15 and :45)` — deliver `telegram` — script `pr-copilot-postmerge-capture.sh`
- `wiki-nightly-lint` — `45 3 * * *` — deliver `telegram` — script `maintain_all_wikis.py`
- `wiki-weekly-maintain` — `0 5 * * 0,3 (Sun Wed)` — deliver `telegram` — script `None`

## Backup State

- Local bundle: `/Users/thedao/.hermes/backups/git/hermes-agent-github-intelligence-resume-54e04c801-20260531-215330.bundle`
- Local bundle: `/Users/thedao/.hermes/backups/git/hermes-agent-github-intelligence-10983cde1-20260531-213134.bundle`
- Local bundle: `/Users/thedao/.hermes/backups/git/hermes-agent-audit-hardening-36efc6097-20260531-205853.bundle`

## Operating Principles

- Memory for stable understanding.
- Tools for current truth.
- Sources for verification.
- Cron for hands-off upkeep.
- Secrets stay out of wiki, SimpleMem, ai-memory, reflections, and backups.
