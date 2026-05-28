---
title: AGENTS.md Overview
type: source
created: 2026-05-25
updated: 2026-05-25
tags: [agents-md, architecture]
sources: []
status: active
---

# AGENTS.md Overview

Summary of root `AGENTS.md` (developer guide for this repo).

## Core layout

- `run_agent.py` — `AIAgent` loop
- `model_tools.py` + `tools/registry.py` — tool wiring
- `toolsets.py` — which tools each platform exposes
- `cli.py` / `hermes_cli/` — CLI, config, profiles, skins
- `gateway/` — messaging adapters
- `plugins/` — model providers, memory, kanban, etc.

## Policies worth remembering

- Use `get_hermes_home()` — never hardcode `~/.hermes`
- Run tests via `scripts/run_tests.sh` only
- No new in-tree memory providers under `plugins/memory/`
- Prompt caching: do not change toolsets or reload system prompt mid-session
- Slash commands that mutate skills/tools use deferred invalidation (`--now` optional)

## Testing

Subprocess-per-test isolation via `tests/_isolate_plugin.py`. Hermetic env in `tests/conftest.py`.

## Related

- [[entities/hermes-agent]]
