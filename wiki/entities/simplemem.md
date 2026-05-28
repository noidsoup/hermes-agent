---
title: SimpleMem
type: entity
created: 2026-05-25
updated: 2026-05-25
tags: [memory, cursor]
status: active
---

# SimpleMem

Repo-local persistent memory for Cursor and Hermes jobs with `workdir` set to this repo.

## Paths

- `simplemem_client.py`, `simplemem_cli.py` — client + CLI
- `docs/simplemem/memories.json` — committed local store (namespace `hermes-agent`)
- `.cursor/rules/simplemem.mdc` — Cursor rule

## Backends

- **local** (default here) — JSON keyword search
- **mcp** — cloud semantic memory when `SIMPLEMEM_TOKEN` is set

## Related

- [[concepts/memory-layers]]
- [[guides/project-knowledge-maintenance]]
