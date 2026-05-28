---
title: s6-overlay Docker Supervision Plan
type: source
created: 2026-05-25
updated: 2026-05-25
tags: [docker, s6]
sources: ["docs/plans/2026-05-07-s6-overlay-dynamic-subagent-gateways.md"]
status: active
---

# s6-overlay Docker Supervision Plan

**Status: shipped** (PR #30136, May 2026). Preserved in `docs/plans/2026-05-07-s6-overlay-dynamic-subagent-gateways.md`.

## Goal

Replace `tini` with s6-overlay as PID 1 so main Hermes, dashboard, and per-profile gateways are supervised (restart, signals, zombie reaping).

## Architecture

- `/init` → s6-svscan
- Static services at image build; per-profile gateways registered dynamically under scandir
- `ServiceManager` abstracts systemd / launchd / Windows tasks / s6

## Related

- [[entities/hermes-agent]]
