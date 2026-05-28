---
title: ACP Auto-Approve Permissions
type: decision
created: 2026-05-25
updated: 2026-05-25
tags: [acp, copilot]
status: active
---

# ACP Auto-Approve Permissions

## Context

Copilot ACP blocks on `session/request_permission` before shell execution. Hermes previously denied all prompts, causing 300s API timeouts in Telegram.

## Decision

When `HERMES_COPILOT_ACP_AUTO_APPROVE` or `HERMES_YOLO_MODE` is truthy, respond with permission granted for ACP shell prompts. ACP subprocesses must route shell via Hermes `terminal` tool calls, not built-in bash.

## Consequences

- Faster Telegram turns; shell runs under Hermes terminal policy
- User must trust auto-approved commands in ACP mode

## Related

- [[entities/copilot-acp-client]]
