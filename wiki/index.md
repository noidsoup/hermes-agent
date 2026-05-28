---
title: Wiki Index
type: index
created: 2026-05-25
updated: 2026-05-25
---

# Hermes Agent Wiki

> Content catalog. The LLM reads this first when answering queries.

## Sources

| Page | Summary | Date |
|------|---------|------|
| [[sources/agents-md-overview]] | High-level repo map from AGENTS.md | 2026-05-25 |
| [[sources/docs-plans-s6-overlay]] | s6-overlay Docker supervision plan (shipped) | 2026-05-25 |

## Entities

| Page | What it is |
|------|------------|
| [[entities/hermes-agent]] | Core Python package and runtime |
| [[entities/copilot-acp-client]] | Copilot ACP transport shim |
| [[entities/simplemem]] | Repo-local SimpleMem store |
| [[entities/llm-wiki]] | This wiki vault |

## Concepts

| Page | Summary |
|------|---------|
| [[concepts/memory-layers]] | Hermes memory vs SimpleMem vs wiki vs skills |

## Decisions

| # | Decision | Status |
|---|----------|--------|
| [[decisions/0001-acp-auto-approve-permissions]] | Auto-approve Copilot ACP permission prompts | active |
| [[decisions/0002-project-knowledge-bootstrap]] | Bootstrap wiki + SimpleMem in-repo | active |

## Guides

| Page | Purpose |
|------|---------|
| [[guides/project-knowledge-maintenance]] | Nightly wiki/SimpleMem upkeep for agents |
