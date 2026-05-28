---
title: Copilot ACP Client
type: entity
created: 2026-05-25
updated: 2026-05-26
tags: [acp, transport, copilot]
status: active
---

# Copilot ACP Client

Module: `agent/copilot_acp_client.py`. Forwards Hermes chat requests to `copilot --acp --stdio` and maps responses to OpenAI-compatible shapes.

## Failure modes (May 2026)

1. **Permission deadlock** — Copilot sends `session/request_permission` for shell; if Hermes denies, subprocess waits until API timeout (~300s).
2. **Wrong shell path** — ACP subprocess must emit `<tool_call>` for Hermes `terminal`, not built-in bash.
3. **Process churn** — Spawning a new Copilot process every turn adds latency; prefer reusing the shared client when the gateway holds one open.

## Configuration

- `providers.acp.copilot_path` (or `command`) in `config.yaml` — bridged to `HERMES_COPILOT_ACP_COMMAND` / `COPILOT_CLI_PATH` at load time when env is unset
- `providers.acp.args` — optional; bridged to `HERMES_COPILOT_ACP_ARGS`
- `HERMES_COPILOT_ACP_COMMAND` / `COPILOT_CLI_PATH` — binary (default `copilot`)
- `HERMES_COPILOT_ACP_ARGS` — default `["--acp", "--stdio"]`
- `HERMES_COPILOT_ACP_AUTO_APPROVE` or `HERMES_YOLO_MODE` — auto-grant permissions

## Related

- [[decisions/0001-acp-auto-approve-permissions]]
- [[entities/hermes-agent]]
