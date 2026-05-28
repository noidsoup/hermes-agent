---
title: Project Knowledge Maintenance
type: guide
created: 2026-05-25
updated: 2026-05-25
tags: [wiki, simplemem, cron]
status: active
---

# Project Knowledge Maintenance

## Manual run

```bash
cd /Users/thedao/.hermes/hermes-agent
export SIMPLEMEM_ENABLED=true SIMPLEMEM_BACKEND=local SIMPLEMEM_NAMESPACE=hermes-agent
python3 scripts/maintain_project_knowledge.py
```

## Nightly (automatic)

Cron job `nightly-self-improvement` (`9562ddd2c3bd`, 02:00 local) includes wiki lint + SimpleMem sync when `workdir` is this repo.

## Agent duties after significant work

1. **Wiki** — File decisions/entities; append `wiki/log.md`; update `wiki/index.md`
2. **SimpleMem** — `python3 simplemem_cli.py add --text "..." --metadata type=decision`
3. **Hermes memory** — Only profile-wide durable facts (not repo task logs)
4. **Commit** — `docs/simplemem/memories.json` when SimpleMem changes

## What not to store

Secrets, tokens, PII, or ephemeral PR/CI identifiers in wiki or SimpleMem.

## Related

- [[entities/simplemem]]
- [[entities/llm-wiki]]
- [[concepts/memory-layers]]
