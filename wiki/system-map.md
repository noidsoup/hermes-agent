---
title: Hermes System Map
type: report
updated: 2026-06-11T03:15:55
---

# Hermes System Map

Generated: `2026-06-11T03:15:55`
Repo: `/Users/thedao/.hermes/hermes-agent`
Git head: `919f86ec4 fix: harden GitHub intelligence collection against rate limits`

## Memory Layers

- **Hermes profile memory**: user preferences, stable environment facts, durable conventions.
- **Skills**: reusable procedures and workflows.
- **Session search**: past conversation recall.
- **Wiki/SimpleMem**: repo-local project knowledge.
- **Memory oracle**: source-linked MeMo-style reflection QA for stable knowledge.
- **Live tools**: current truth for files, git, cron, Airtable, logs, processes.

## Memory Oracle

- Reflections: `400`
- Health: `True`
- Last checked: `2026-06-11T03:15:55`
- Eval summary: `memory oracle evals: 8/8 passed`
- Rule: use for stable conceptual orientation; verify important/current claims with sources/tools.

## Cron Overview

- Active jobs: `29`
- Paused/disabled jobs: `0`

- `PPIHC 2026 results verification` — `once at 2026-06-22 08:00` — deliver `telegram` — script `None`
- `ai-memory-nightly-reindex` — `0 3 * * *` — deliver `local` — script `ai-memory-nightly-reindex.sh`
- `ai-memory-watchdog` — `5 4 * * *` — deliver `local` — script `ai-memory-watchdog.py`
- `apfs-actions-monitor` — `*/30 * * * *` — deliver `local` — script `apfs-actions-monitor.sh`
- `apfs-cat-cpt-stats` — `12 * * * * (hourly at :12)` — deliver `local` — script `apfs-cat-cpt-stats.sh`
- `apfs-fub-sync` — `0 19 * * * (daily ~02:00 UTC)` — deliver `local` — script `apfs-fub-sync.sh`
- `apfs-sp-contracted-sweep` — `0 6 * * 0 (Sun ~06:00 UTC)` — deliver `local` — script `apfs-sp-contracted-sweep.sh`
- `apfs-sp-daily-client-sync` — `0 5 * * * (daily ~12:00 UTC)` — deliver `local` — script `apfs-sp-daily-client-sync.sh`
- `apfs-sp-delta-contract-refresh` — `0 22 * * 6 (Sat ~Sun 05:00 UTC)` — deliver `local` — script `apfs-sp-delta-contract-refresh.sh`
- `apfs-sp-refresh-queue-drain` — `*/15 * * * *` — deliver `local` — script `apfs-sp-refresh-queue-drain.sh`
- `apfs-sp-weekly-sync` — `0 19 1,15 * * (1st & 15th ~02:00 UTC)` — deliver `local` — script `apfs-sp-weekly-sync.sh`
- `ascii-pool-grow` — `0 3 * * *` — deliver `origin` — script `None`
- `ghembed-weekly-reindex` — `30 9 * * 1` — deliver `telegram` — script `ghembed-weekly-reindex.sh`
- `github-intelligence-weekly-digest` — `0 9 * * 1` — deliver `telegram` — script `github-intelligence-digest.sh`
- `github-vault-health-daily` — `0 9 * * *` — deliver `telegram` — script `github-vault-health.sh`
- `hermes-state-backup` — `30 4 * * 0` — deliver `telegram` — script `backup_hermes_state.sh`
- `il-community-hunter` — `0 22 * * *` — deliver `local` — script `il-community-hunter.sh`
- `memory-oracle-maintenance` — `15 3 * * *` — deliver `telegram` — script `maintain_memory_oracle.sh`
- `memory-pressure-watchdog` — `30 4 * * *` — deliver `telegram` — script `memory_pressure_watchdog.py`
- `monitors-off-9pm` — `0 21 * * *` — deliver `origin` — script `monitors_off.sh`
- `morning-daily-summary` — `0 8 * * *` — deliver `telegram` — script `morning-daily-summary.sh`
- `nightly-ascii-art` — `0 21 * * *` — deliver `telegram` — script `None`
- `nightly-health` — `0 4 * * *` — deliver `telegram` — script `hermes_health_watchdog.py`
- `nightly-self-improvement` — `0 2 * * *` — deliver `telegram` — script `nightly-self-improvement-preflight.sh`
- `nightly-simplemem` — `30 3 * * *` — deliver `telegram` — script `maintain_all_simplemem.py`
- `pr-copilot-postmerge-capture` — `15,45 * * * * (every 30 min at :15 and :45)` — deliver `telegram` — script `pr-copilot-postmerge-capture.sh`
- `scheduler-config-audit` — `15 5 * * *` — deliver `telegram` — script `scheduler_audit.py`
- `wiki-nightly-lint` — `45 3 * * *` — deliver `local` — script `maintain_all_wikis.py`
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
