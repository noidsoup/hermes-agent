---
title: Memory Layers
type: concept
created: 2026-05-25
updated: 2026-05-25
tags: [memory, architecture]
status: active
---

# Memory Layers

Hermes uses several complementary stores — do not duplicate task logs across all of them.

## Hermes built-in `memory` tool

- **Scope**: Profile-wide (`~/.hermes/memories/`)
- **Injected**: Every turn (compact facts)
- **Use for**: User preferences, env facts, stable conventions
- **Avoid**: PR numbers, commit SHAs, session outcomes

## Session search

- **Scope**: SQLite FTS5 over past chats
- **Use for**: "What did we do about X?"

## Skills

- **Scope**: `skills/` + `~/.hermes/skills/`
- **Use for**: Procedures, commands, pitfalls

## SimpleMem (this repo)

- **Scope**: `docs/simplemem/memories.json`, namespace `hermes-agent`
- **Use for**: Repo-specific decisions and summaries; Cursor sessions
- **Bridge**: Nightly script + agent `workdir` here

## LLM Wiki (this repo)

- **Scope**: `wiki/` structured pages
- **Use for**: Architecture, entities, ADRs, runbooks
- **Best when**: Hermes cron/job sets `workdir` to hermes-agent

## Related

- [[entities/simplemem]]
- [[entities/llm-wiki]]
- [[guides/project-knowledge-maintenance]]
