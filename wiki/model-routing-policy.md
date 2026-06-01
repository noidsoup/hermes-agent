---
title: Model Routing Policy
type: policy
updated: 2026-06-01
---

# Model Routing Policy

Hermes now has an opt-in v0 automatic model router for CLI/chat turns.

This is intentionally conservative: it is a deterministic keyword classifier, not an LLM router. If routing is disabled or a configured route cannot be resolved, Hermes keeps the current session provider/model.

## Goals

- Use deterministic scripts for maintenance whenever possible.
- Use Copilot/Cursor-backed models for interactive coding and implementation when available.
- Use local Ollama models for offline synthesis and weekly knowledge maintenance.
- Use tools/live state for current truth; never ask a model to guess current state.
- Keep explicit user model/provider choices authoritative.

## Implemented v0 behavior

Config lives under `model_routing` in `config.yaml`:

```yaml
model_routing:
  enabled: false
  show_decisions: false
  routes:
    default: {}
    fast: {}
    coding: {}
    wiki: {}
    research: {}
    memory: {}
```

When `enabled: true`, Hermes classifies each CLI/chat turn as one of:

- `coding` — implement, fix, debug, refactor, test, commit, code/script work.
- `wiki` — wiki, docs, Obsidian, SimpleMem, memory-oracle, knowledge-base work.
- `research` — search, web, arXiv, current/latest facts, benchmarks.
- `memory` — “where are we at”, “what did we do”, prior-session/status questions.
- `fast` — quick summaries or brief explanations.
- `default` — no specific match.

Each route may specify:

```yaml
provider: copilot-acp
model: composer-2.5-fast
```

Empty route entries mean “keep the current session provider/model.”

## Example local config

```yaml
model_routing:
  enabled: true
  show_decisions: true
  routes:
    coding:
      provider: copilot-acp
      model: composer-2.5-fast
    wiki:
      provider: ollama
      model: llama3.3:70b
    fast:
      provider: copilot-acp
      model: composer-2.5-fast
```

## Guardrails

- Explicit CLI `--model` or `--provider` bypasses auto-routing.
- Cron jobs still use explicit per-job `model` / `provider` pins; the automatic router does not change existing cron behavior.
- The router never sees or handles API keys directly.
- If runtime resolution fails for a route, Hermes logs a warning and falls back to the current route.
- Do not route secrets into model prompts.
- Do not encode current operational state in durable memory.
- Prefer source-linked answers over unsupported synthesis.

## Routes policy

- Fast/simple Q&A: current interactive provider or fast Copilot model.
- Code implementation: Copilot/Claude/Codex style coding model with file+terminal tools.
- Nightly deterministic maintenance: `no_agent` scripts.
- Wiki/deep synthesis: local Ollama 70B when configured, otherwise Copilot-backed model.
- Memory oracle: deterministic retrieval first; optional model only for future candidate generation.
- High-risk edits: require source verification and tests/evals.
- Windows/GPU offload: use `ssh yin` for heavy eval/index/model experiments when available.

## Known limitations

- v0 is keyword-based, so it can misclassify ambiguous requests.
- The router currently applies to CLI/chat turn construction, not to every internal subagent or gateway-specific execution path.
- It selects provider/model only; it does not yet automatically narrow toolsets per route.
- It is not a cost optimizer yet.
