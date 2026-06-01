---
title: Cron Risk Report
type: report
updated: 2026-05-31T20:49:18
---

# Cron Risk Report

## apfs-actions-monitor
- Category: `apfs`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '*/30 * * * *', 'display': '*/30 * * * *'}`
- Delivery: `local`
- Script: `apfs-actions-monitor.sh`
- Side effects: none inferred

## apfs-cat-cpt-stats
- Category: `apfs`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '12 * * * *', 'display': '12 * * * * (hourly at :12)'}`
- Delivery: `local`
- Script: `apfs-cat-cpt-stats.sh`
- Side effects: none inferred

## apfs-fub-sync
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '0 19 * * *', 'display': '0 19 * * * (daily ~02:00 UTC)'}`
- Delivery: `local`
- Script: `apfs-fub-sync.sh`
- Side effects: may write local/external state

## apfs-sp-contracted-sweep
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '0 6 * * 0', 'display': '0 6 * * 0 (Sun ~06:00 UTC)'}`
- Delivery: `local`
- Script: `apfs-sp-contracted-sweep.sh`
- Side effects: may write local/external state

## apfs-sp-daily-client-sync
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '0 5 * * *', 'display': '0 5 * * * (daily ~12:00 UTC)'}`
- Delivery: `local`
- Script: `apfs-sp-daily-client-sync.sh`
- Side effects: may write local/external state

## apfs-sp-delta-contract-refresh
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '0 22 * * 6', 'display': '0 22 * * 6 (Sat ~Sun 05:00 UTC)'}`
- Delivery: `local`
- Script: `apfs-sp-delta-contract-refresh.sh`
- Side effects: may write local/external state

## apfs-sp-refresh-queue-drain
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '*/15 * * * *', 'display': '*/15 * * * *'}`
- Delivery: `local`
- Script: `apfs-sp-refresh-queue-drain.sh`
- Side effects: may write local/external state

## apfs-sp-weekly-sync
- Category: `apfs`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '0 19 1,15 * *', 'display': '0 19 1,15 * * (1st & 15th ~02:00 UTC)'}`
- Delivery: `local`
- Script: `apfs-sp-weekly-sync.sh`
- Side effects: may write local/external state

## pr-copilot-postmerge-capture
- Category: `github`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '15,45 * * * *', 'display': '15,45 * * * * (every 30 min at :15 and :45)'}`
- Delivery: `telegram`
- Script: `pr-copilot-postmerge-capture.sh`
- Side effects: may touch GitHub

## nightly-health
- Category: `health`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '0 4 * * *', 'display': '0 4 * * *'}`
- Delivery: `telegram`
- Script: `hermes_health_watchdog.py`
- Side effects: none inferred

## ai-memory-nightly-reindex
- Category: `knowledge`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '0 3 * * *', 'display': '0 3 * * *'}`
- Delivery: `local`
- Script: `ai-memory-nightly-reindex.sh`
- Side effects: none inferred

## memory-oracle-maintenance
- Category: `knowledge`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '15 3 * * *', 'display': '15 3 * * *'}`
- Delivery: `telegram`
- Script: `maintain_memory_oracle.sh`
- Side effects: may write local/external state

## nightly-self-improvement
- Category: `knowledge`
- Risk: `high_autonomy`
- Schedule: `{'kind': 'cron', 'expr': '0 2 * * *', 'display': '0 2 * * *'}`
- Delivery: `telegram`
- Script: `nightly-self-improvement-preflight.sh`
- Side effects: LLM agent can use enabled tools, may write local/external state, may touch GitHub

## nightly-simplemem
- Category: `knowledge`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '30 3 * * *', 'display': '30 3 * * *'}`
- Delivery: `telegram`
- Script: `maintain_all_simplemem.py`
- Side effects: may write local/external state

## wiki-nightly-lint
- Category: `knowledge`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '45 3 * * *', 'display': '45 3 * * *'}`
- Delivery: `telegram`
- Script: `maintain_all_wikis.py`
- Side effects: may write local/external state

## wiki-weekly-maintain
- Category: `knowledge`
- Risk: `high_autonomy`
- Schedule: `{'kind': 'cron', 'expr': '0 5 * * 0,3', 'display': '0 5 * * 0,3 (Sun Wed)'}`
- Delivery: `telegram`
- Script: `agent`
- Side effects: LLM agent can use enabled tools, may write local/external state, may touch GitHub

## hermes-state-backup
- Category: `ops`
- Risk: `writes_or_external_side_effects`
- Schedule: `{'kind': 'cron', 'expr': '30 4 * * 0', 'display': '30 4 * * 0'}`
- Delivery: `telegram`
- Script: `backup_hermes_state.sh`
- Side effects: may write local/external state

## il-community-hunter
- Category: `personal`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '0 22 * * *', 'display': '0 22 * * *'}`
- Delivery: `local`
- Script: `il-community-hunter.sh`
- Side effects: none inferred

## morning-daily-summary
- Category: `personal`
- Risk: `read_only`
- Schedule: `{'kind': 'cron', 'expr': '0 8 * * *', 'display': '0 8 * * *'}`
- Delivery: `telegram`
- Script: `morning-daily-summary.sh`
- Side effects: none inferred
