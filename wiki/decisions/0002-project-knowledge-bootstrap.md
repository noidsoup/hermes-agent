---
title: Project Knowledge Bootstrap
type: decision
created: 2026-05-25
updated: 2026-05-25
tags: [wiki, simplemem]
status: active
---

# Project Knowledge Bootstrap

## Context

User uses SimpleMem and LLM wiki in other repos; wanted the same in `hermes-agent` with ongoing maintenance.

## Decision

1. Bootstrap **SimpleMem** (local backend, committed `docs/simplemem/`)
2. Bootstrap **wiki/** with seed pages for core architecture
3. Wire upkeep into cron `nightly-self-improvement` and `scripts/maintain_project_knowledge.py`
4. Do not ingest `website/docs/` (Docusaurus); use `docs/plans/` for engineering plans only

## Related

- [[guides/project-knowledge-maintenance]]
- [[entities/simplemem]]
- [[entities/llm-wiki]]
