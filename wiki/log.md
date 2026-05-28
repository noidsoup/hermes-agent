---
title: Wiki Log
type: log
created: 2026-05-25
updated: 2026-05-28
---

# Wiki Log

> Chronological record of wiki operations. Append-only.

## [2026-05-25] create | Wiki bootstrapped

Initial wiki structure created. Seeded entities (hermes-agent, copilot-acp-client), concepts (memory-layers), decisions (ACP permissions, knowledge bootstrap), and maintenance guide.

## [2026-05-25] migrate | docs/plans partial ingest

Ingested `docs/plans/2026-05-07-s6-overlay-dynamic-subagent-gateways.md` as source summary (website/docs/ excluded — Docusaurus user docs, not project KB).

## [2026-05-26] session | Nightly self-improvement

- Health scan: recurring `providers.acp: unknown config keys ignored: copilot_path` warnings; cron failures on `il-community-hunter` (ACP 300s timeout), APFS SeniorPlace scripts (bootstrap/shell errors).
- Fixed config bridge: `providers.acp.copilot_path` now maps to `HERMES_COPILOT_ACP_COMMAND` at load; ACP block skipped from custom-provider normalization.
- Ran `maintain_project_knowledge.py` (wiki lint OK, SimpleMem synced 2 log entries). Curator deferred (7d interval, 0 stale skills).

## [2026-05-27] maintain | Scheduled wiki automation

- Added `scripts/maintain_wiki.py` + `maintain_all_wikis.py` (lint, dead links, recent `docs/` ingest inventory).
- Cron `wiki-nightly-lint` (3:45 AM) — script report to Telegram when issues exist.
- Cron `wiki-weekly-maintain` (Sun 5 AM) — Ollama agent round-robin: ingest, improve thin pages, update index/log per repo.

## [2026-05-27] session | Nightly self-improvement

- Health: all 16 enabled crons `last_status=ok`; no new errors.log entries today. Yesterday: copilot-acp 300s timeouts, Telegram polling conflicts, OpenRouter auxiliary credit errors (user session fixed stale_timeout + auxiliary provider).
- Verified working-tree `providers.acp.copilot_path` bridge (`test_provider_config_validation.py` 21/21).
- `maintain_project_knowledge.py`: wiki lint OK, synced 3 log entries. Curator still deferred (7d interval, 0 stale).

## [2026-05-27] maintain | Wiki auto-commit policy

- Added `scripts/wiki_git_commit.py` — scoped commit/push for `wiki/`, `docs/simplemem/`, `docs/` markdown only.
- **Excluded (manual verify):** `cocktail-party`, `marketing` (PostScript).
- Wired into `nightly-simplemem`, `wiki-weekly-maintain`, and `nightly-self-improvement` (wiki/SimpleMem only; code stays uncommitted).

## [2026-05-28] session | Nightly self-improvement

- Preflight: `ai-memory-nightly-reindex` failed at 03:00 (psql not on cron PATH); script already patched with Homebrew PATH + `$PSQL` guard — manual rerun indexed 26 repos OK.
- Recurring copilot-acp 300s stale timeouts on large cron prompts (~12k tokens); one run hit wrong path `/Users/thedao/scripts/maintain_project_knowledge.py` — use absolute path under `~/.hermes/hermes-agent/scripts/`.
- `maintain_project_knowledge.py`: wiki lint OK, synced 5 log entries. Curator deferred (7d interval, 0 stale).
