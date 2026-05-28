---
title: Hermes Agent
type: entity
created: 2026-05-25
updated: 2026-05-25
tags: [core, runtime]
status: active
---

# Hermes Agent

Python AI agent framework: CLI, messaging gateway, TUI, plugins, skills, tools, cron, kanban, and provider plugins.

## Load-bearing entry points

- `run_agent.py` — `AIAgent` conversation loop
- `model_tools.py` — tool discovery and dispatch
- `cli.py` / `hermes_cli/` — CLI and subcommands
- `gateway/` — platform adapters (Telegram, Discord, …)
- `agent/` — provider adapters, memory, compression, ACP
- `tools/` — auto-discovered via `tools/registry.py`
- `skills/` + `optional-skills/` — procedural knowledge

## Config

- `~/.hermes/config.yaml` — settings
- `~/.hermes/.env` — API keys only
- Profiles: `HERMES_HOME` override per instance

## Related

- [[entities/copilot-acp-client]]
- [[concepts/memory-layers]]
- [[sources/agents-md-overview]]
