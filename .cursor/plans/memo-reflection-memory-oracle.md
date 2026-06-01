# MeMo-style Reflection Memory Oracle Pilot

## Goal

Implement a lightweight MeMo-inspired memory layer for Hermes without model fine-tuning: generate durable QA/reflection records from stable project knowledge, store them as JSONL with source pointers, and provide a local query script that the executive model can use as a semantic memory oracle.

## Current context / assumptions

- Active repo: `/Users/thedao/.hermes/hermes-agent`.
- Project instructions say repo knowledge belongs in `wiki/`, SimpleMem, and Context7; do not store secrets or ephemeral PR/CI IDs in wiki/SimpleMem.
- User wants to incorporate MeMo in our work, but prior agreement was to start with generated reflection QA + source verification, not actual fine-tuning.
- Initial implementation should be safe, local, and source-linked.
- Avoid training costs and provenance loss for the pilot.

## Proposed approach

Build a minimal pipeline:

1. `scripts/generate_reflections.py`
   - Scans stable project docs/code context.
   - Produces deterministic starter reflections from headings, lists, and selected project docs.
   - Writes JSONL to `wiki/memory/reflections.jsonl`.
   - Includes `question`, `answer`, `sources`, `type`, `stability`, timestamps, and IDs.

2. `scripts/query_memory_oracle.py`
   - Loads `wiki/memory/reflections.jsonl`.
   - Uses lexical scoring/BM25-ish token overlap first, no model required.
   - Returns top matches as JSON or plaintext.
   - Keeps source pointers visible for verification.

3. `wiki/memory/README.md`
   - Documents the MeMo-inspired architecture and usage.
   - Clarifies what belongs/does not belong in reflections.

4. Optionally add a small eval fixture later.

## Step-by-step plan

- [ ] Inspect existing `scripts/maintain_wiki.py`, wiki layout, and repo conventions.
- [ ] Create `wiki/memory/README.md` documenting the memory oracle.
- [ ] Create `scripts/generate_reflections.py`.
  - [ ] Use only stdlib.
  - [ ] Default repo path = current working directory.
  - [ ] Default output = `wiki/memory/reflections.jsonl`.
  - [ ] Include stable seed sources: `AGENTS.md`, selected `wiki/*.md`, selected docs under `website/docs`, and important files such as `toolsets.py` / `cron/*.py` if present.
  - [ ] Avoid `.env`, credentials, logs, session dumps, and volatile files.
- [ ] Create `scripts/query_memory_oracle.py`.
  - [ ] Support `--repo`, `--limit`, `--json`.
  - [ ] Print source paths for each answer.
- [ ] Run generator once for Hermes repo.
- [ ] Run sample queries:
  - [ ] “How does Hermes cron work?”
  - [ ] “Where should stable repo knowledge go?”
  - [ ] “What should not be stored in memory?”
- [ ] Run syntax checks for new scripts.
- [ ] Summarize result and next steps.

## Files likely to change

- `.cursor/plans/memo-reflection-memory-oracle.md`
- `scripts/generate_reflections.py`
- `scripts/query_memory_oracle.py`
- `wiki/memory/README.md`
- `wiki/memory/reflections.jsonl`

## Tests / validation

- `python3 -m py_compile scripts/generate_reflections.py scripts/query_memory_oracle.py`
- `python3 scripts/generate_reflections.py --repo . --max-records 200`
- `python3 scripts/query_memory_oracle.py "How does Hermes cron work?" --limit 3`
- Confirm generated JSONL parses line-by-line.
- Confirm answers include source paths.

## Risks / tradeoffs

- Lexical search is not true MeMo; it is a safe pilot layer to create/evaluate reflection data before training.
- Generated reflections from deterministic heuristics may be lower quality than LLM-generated QA. This is acceptable for v0; LLM generation can be added later.
- Reflections can become stale. Store only stable facts and source paths; regenerate from stable docs as needed.
- Provenance must remain visible; do not let memory oracle answers become final authority without verification for high-risk tasks.

## Future enhancements

- Add LLM-backed reflection generation using configured Hermes providers.
- Add eval questions under `tests/fixtures` or `wiki/memory/evals.jsonl`.
- Add vector/BM25 indexing for better retrieval.
- Add a Hermes tool wrapper once the script proves useful.
- Later, fine-tune a small local MEMORY model on curated reflections if evals justify it.
