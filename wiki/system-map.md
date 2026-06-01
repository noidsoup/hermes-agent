---
title: Hermes System Map
type: report
updated: 2026-05-31T20:49:18
---

# Hermes System Map

Generated: `2026-05-31T20:49:18`
Repo: `/Users/thedao/.hermes/hermes-agent`
Git head: `e45e459d0 feat: add memory oracle maintenance`

## Memory Layers

- **Hermes profile memory**: user preferences, stable environment facts, durable conventions.
- **Skills**: reusable procedures and workflows.
- **Session search**: past conversation recall.
- **Wiki/SimpleMem**: repo-local project knowledge.
- **Memory oracle**: source-linked MeMo-style reflection QA for stable knowledge.
- **Live tools**: current truth for files, git, cron, Airtable, logs, processes.

## Memory Oracle

- Reflections: `398`
- Health: `True`
- Last checked: `2026-05-31T20:49:18`
- Eval summary: `memory oracle evals: 8/8 passed`
- Rule: use for stable conceptual orientation; verify important/current claims with sources/tools.

## Cron Overview

- Active jobs: `19`
- Paused/disabled jobs: `0`

- `ai-memory-nightly-reindex` — `{'kind': 'cron', 'expr': '0 3 * * *', 'display': '0 3 * * *'}` — deliver `local` — script `ai-memory-nightly-reindex.sh`
- `apfs-actions-monitor` — `{'kind': 'cron', 'expr': '*/30 * * * *', 'display': '*/30 * * * *'}` — deliver `local` — script `apfs-actions-monitor.sh`
- `apfs-cat-cpt-stats` — `{'kind': 'cron', 'expr': '12 * * * *', 'display': '12 * * * * (hourly at :12)'}` — deliver `local` — script `apfs-cat-cpt-stats.sh`
- `apfs-fub-sync` — `{'kind': 'cron', 'expr': '0 19 * * *', 'display': '0 19 * * * (daily ~02:00 UTC)'}` — deliver `local` — script `apfs-fub-sync.sh`
- `apfs-sp-contracted-sweep` — `{'kind': 'cron', 'expr': '0 6 * * 0', 'display': '0 6 * * 0 (Sun ~06:00 UTC)'}` — deliver `local` — script `apfs-sp-contracted-sweep.sh`
- `apfs-sp-daily-client-sync` — `{'kind': 'cron', 'expr': '0 5 * * *', 'display': '0 5 * * * (daily ~12:00 UTC)'}` — deliver `local` — script `apfs-sp-daily-client-sync.sh`
- `apfs-sp-delta-contract-refresh` — `{'kind': 'cron', 'expr': '0 22 * * 6', 'display': '0 22 * * 6 (Sat ~Sun 05:00 UTC)'}` — deliver `local` — script `apfs-sp-delta-contract-refresh.sh`
- `apfs-sp-refresh-queue-drain` — `{'kind': 'cron', 'expr': '*/15 * * * *', 'display': '*/15 * * * *'}` — deliver `local` — script `apfs-sp-refresh-queue-drain.sh`
- `apfs-sp-weekly-sync` — `{'kind': 'cron', 'expr': '0 19 1,15 * *', 'display': '0 19 1,15 * * (1st & 15th ~02:00 UTC)'}` — deliver `local` — script `apfs-sp-weekly-sync.sh`
- `hermes-state-backup` — `{'kind': 'cron', 'expr': '30 4 * * 0', 'display': '30 4 * * 0'}` — deliver `telegram` — script `backup_hermes_state.sh`
- `il-community-hunter` — `{'kind': 'cron', 'expr': '0 22 * * *', 'display': '0 22 * * *'}` — deliver `local` — script `il-community-hunter.sh`
- `memory-oracle-maintenance` — `{'kind': 'cron', 'expr': '15 3 * * *', 'display': '15 3 * * *'}` — deliver `telegram` — script `maintain_memory_oracle.sh`
- `morning-daily-summary` — `{'kind': 'cron', 'expr': '0 8 * * *', 'display': '0 8 * * *'}` — deliver `telegram` — script `morning-daily-summary.sh`
- `nightly-health` — `{'kind': 'cron', 'expr': '0 4 * * *', 'display': '0 4 * * *'}` — deliver `telegram` — script `hermes_health_watchdog.py`
- `nightly-self-improvement` — `{'kind': 'cron', 'expr': '0 2 * * *', 'display': '0 2 * * *'}` — deliver `telegram` — script `nightly-self-improvement-preflight.sh`
- `nightly-simplemem` — `{'kind': 'cron', 'expr': '30 3 * * *', 'display': '30 3 * * *'}` — deliver `telegram` — script `maintain_all_simplemem.py`
- `pr-copilot-postmerge-capture` — `{'kind': 'cron', 'expr': '15,45 * * * *', 'display': '15,45 * * * * (every 30 min at :15 and :45)'}` — deliver `telegram` — script `pr-copilot-postmerge-capture.sh`
- `wiki-nightly-lint` — `{'kind': 'cron', 'expr': '45 3 * * *', 'display': '45 3 * * *'}` — deliver `telegram` — script `maintain_all_wikis.py`
- `wiki-weekly-maintain` — `{'kind': 'cron', 'expr': '0 5 * * 0,3', 'display': '0 5 * * 0,3 (Sun Wed)'}` — deliver `telegram` — script `None`

## Backup State

- Local bundle: `/Users/thedao/.hermes/backups/git/hermes-agent-memory-oracle-e45e459d0-20260531-181508.bundle`

## Operating Principles

- Memory for stable understanding.
- Tools for current truth.
- Sources for verification.
- Cron for hands-off upkeep.
- Secrets stay out of wiki, SimpleMem, ai-memory, reflections, and backups.
