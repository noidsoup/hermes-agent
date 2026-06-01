---
title: Model Routing Policy
type: policy
updated: 2026-05-31
---

# Model Routing Policy

## Goals

- Use deterministic scripts for maintenance whenever possible.
- Use Copilot/Cursor-backed models for interactive coding and implementation when available.
- Use local Ollama models for offline synthesis and weekly knowledge maintenance.
- Use tools/live state for current truth; never ask a model to guess current state.

## Routes

- Fast/simple Q&A: current interactive provider or fast Copilot model.
- Code implementation: Copilot/Claude/Codex style coding model with file+terminal tools.
- Nightly deterministic maintenance: `no_agent` scripts.
- Wiki/deep synthesis: local Ollama 70B when configured, otherwise Copilot-backed model.
- Memory oracle: deterministic retrieval first; optional model only for future candidate generation.
- High-risk edits: require source verification and tests/evals.
- Windows/GPU offload: use `ssh yin` for heavy eval/index/model experiments when available.

## Guardrails

- Do not route secrets into model prompts.
- Do not encode current operational state in durable memory.
- Prefer source-linked answers over unsupported synthesis.
