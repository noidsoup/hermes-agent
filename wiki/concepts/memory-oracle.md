---
title: Memory Oracle
type: concept
created: 2026-05-31
updated: 2026-05-31
tags: [memory, memo, reflections, retrieval]
aliases: [MeMo pilot, reflection memory, memory oracle]
sources: ["[[concepts/memory-layers]]"]
status: active
---

# Memory Oracle

The memory oracle is a lightweight, MeMo-inspired semantic memory layer for Hermes Agent. It stores stable project knowledge as source-linked question/answer reflections before any model fine-tuning is attempted.

## What it is

MeMo separates memory from reasoning: a MEMORY component answers targeted questions about stable knowledge, while an EXECUTIVE model decomposes the user's task and synthesizes the final answer. This pilot implements the MEMORY component as `wiki/memory/reflections.jsonl` plus local query scripts, not as a trained neural model.

## Files

- `wiki/memory/reflections.jsonl` — generated JSONL reflection records.
- `scripts/generate_reflections.py` — builds the reflection corpus from stable repo docs/wiki/code summaries.
- `scripts/query_memory_oracle.py` — lexical query interface over the reflections.
- `scripts/eval_memory_oracle.py` — lightweight regression eval runner.
- `scripts/maintain_memory_oracle.py` — hands-off cron entrypoint that regenerates reflections, runs evals, records state, and prints only on change/failure.

## Record shape

Each reflection includes:

- `question` — a targeted natural-language question.
- `answer` — concise stable answer.
- `sources` — repo-relative paths used for verification.
- `type` — summary, section, code-summary, code-symbols, etc.
- `stability` — usually `stable`; volatile facts should not be stored.

## Usage

Generate or refresh reflections:

```bash
python3 scripts/generate_reflections.py --repo . --max-records 250
```

Query the oracle:

```bash
python3 scripts/query_memory_oracle.py "How does Hermes cron work?" --limit 5
```

Suppress low-confidence matches:

```bash
python3 scripts/query_memory_oracle.py "How should I debug voice transcription?" --min-score 10
```

Emit JSON for tool integration:

```bash
python3 scripts/query_memory_oracle.py "Where should project knowledge go?" --json
```

Run evals:

```bash
python3 scripts/eval_memory_oracle.py --verbose
```

Hands-off maintenance entrypoint:

```bash
python3 scripts/maintain_memory_oracle.py
```

Cron should call the maintenance entrypoint, not ask the user to regenerate or evaluate manually.

## What belongs here

Good candidates:

- Stable architecture and workflow knowledge.
- Durable repo conventions.
- Safety rules and known pitfalls.
- Cross-document concepts that are hard to retrieve from one chunk.
- Source-linked summaries of `AGENTS.md`, wiki pages, docs, and important code entry points.

Bad candidates:

- Current cron lists, PRs, issues, logs, Airtable records, git status, or temporary task progress.
- Secrets, tokens, credentials, private URLs with embedded credentials.
- Any fact likely to become stale within a week.
- Claims that require exact legal/compliance provenance without source verification.

## How agents should use it

Use the memory oracle for stable conceptual orientation before raw search. Do not treat it as final authority for high-risk or current-state answers. Verify important claims against the listed source files, live tools, or current system state.

## Related

- [[concepts/memory-layers]]
- [[guides/project-knowledge-maintenance]]
