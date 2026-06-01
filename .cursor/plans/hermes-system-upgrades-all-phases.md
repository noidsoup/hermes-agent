# Hermes System Upgrades All Phases Implementation Plan

> **For Hermes:** Implement this plan step-by-step. Keep each phase independently shippable. Verify after every phase. Do not store secrets or volatile state in memory/wiki/reflections/backups.

**Goal:** Complete every proposed upgrade: native memory oracle access, automatic routing conventions, system map/reporting, smarter verified reflections, learning/review queues, resilient backups, cron risk metadata, model routing, Windows offload scaffold, and a true MeMo-style small MEMORY model experiment scaffold.

**Architecture:** Keep the current source-linked reflection oracle as the safe foundation. Add deterministic scripts/tools first, then optional LLM/model experiments behind explicit scripts and evals. Live/current state remains tool-derived; stable knowledge goes to wiki/reflections; questionable generated knowledge goes to review queues.

**Tech Stack:** Python stdlib, Hermes tool registry, cron jobs, Git/GitHub fork backups, JSON/JSONL, markdown wiki, optional SSH to Windows host, optional future LoRA training scaffold.

---

## Done Criteria

- Native `memory_oracle_query` tool exists and is in the core/toolset definitions.
- `AGENTS.md` documents memory-oracle-first routing for stable project knowledge.
- Nightly maintenance generates system map and memory oracle health artifacts.
- Reflection generator includes code-aware summaries and relation records.
- Query script supports verification against source files and low-score no-hit behavior.
- Candidate/review queue exists for learned reflections.
- Hermes backup script sanitizes and backs up critical state to a local bundle + GitHub branch/tag where possible.
- Cron risk report classifies jobs by category/risk/delivery/side effects.
- Model routing policy exists as machine-readable config + human-readable docs.
- Windows offload scaffold can run a safe SSH probe or report unavailable cleanly.
- True MeMo experiment scaffold exists, is opt-in, and has eval commands; no expensive training runs by default.
- Tests/evals pass and work is committed + pushed/backup branch created.

---

## Phase 1 — Operationalize Memory Oracle

### Task 1.1: Native tool module

**Objective:** Add a Hermes tool `memory_oracle_query` that queries `wiki/memory/reflections.jsonl` without shelling out.

**Files:**
- Create: `tools/memory_oracle_tool.py`
- Modify: `toolsets.py`
- Test: `tests/tools/test_memory_oracle_tool.py`

**Implementation notes:**
- Reuse/import `scripts.query_memory_oracle.search` and `_load` if import-safe; otherwise factor shared logic minimally.
- Tool schema params: `question`, `repo`, `limit`, `min_score`, `verify_sources`.
- Default `repo` to cwd when it contains `wiki/memory/reflections.jsonl`; otherwise Hermes source repo.
- Return JSON string with `{success, query, results, no_hit, memory_path}`.

**Verification:**
```bash
python3 -m py_compile tools/memory_oracle_tool.py scripts/query_memory_oracle.py
python3 -m pytest tests/tools/test_memory_oracle_tool.py -q -o 'addopts='
```

### Task 1.2: Memory-oracle-first routing docs

**Objective:** Document how agents should use the oracle before raw search for stable knowledge.

**Files:**
- Modify: `AGENTS.md`
- Modify: `wiki/concepts/memory-oracle.md`

**Verification:** Query oracle for “How should stable project knowledge be routed?” and ensure the doc is discoverable after regeneration.

### Task 1.3: System map report

**Objective:** Generate `~/.hermes/reports/system-map.md` and repo copy `wiki/system-map.md` summarizing cron, memory layers, maintenance, backups, model policy, and risks.

**Files:**
- Create: `scripts/generate_system_map.py`
- Modify: `scripts/maintain_memory_oracle.py` to call it after evals.
- Create/Update: `wiki/system-map.md`

**Verification:**
```bash
python3 scripts/generate_system_map.py --repo . --output wiki/system-map.md
python3 scripts/maintain_memory_oracle.py --verbose
```

### Task 1.4: Health artifact/reporting

**Objective:** Emit `wiki/memory/health.json` with eval count, reflection count, source count, hashes, and last run.

**Files:**
- Modify: `scripts/maintain_memory_oracle.py`
- Modify: `scripts/eval_memory_oracle.py` if needed for JSON output.

**Verification:** health JSON parses and reports 8/8+ passing.

---

## Phase 2 — Smarter Memory

### Task 2.1: Code-aware reflection generation

**Objective:** Generate reflection records from selected Python files: module purpose, top-level classes/functions, imports, and test references.

**Files:**
- Modify: `scripts/generate_reflections.py`
- Test: `tests/scripts/test_generate_reflections.py`

**Verification:** generated reflections include `type: code-symbols` and `type: code-relations` records for cron/tool files.

### Task 2.2: Verified query mode

**Objective:** Add `--verify-sources` to query script/tool, reading source snippets and marking missing/available sources.

**Files:**
- Modify: `scripts/query_memory_oracle.py`
- Modify: `tools/memory_oracle_tool.py`
- Test: `tests/tools/test_memory_oracle_tool.py`

**Verification:** source verification reports true for existing files and false for intentionally missing test file.

### Task 2.3: Learning/review queue

**Objective:** Add queue files and helper script to propose durable reflections from completed session summaries/manual text.

**Files:**
- Create: `scripts/propose_reflection.py`
- Create: `wiki/memory/candidates.jsonl`
- Create: `wiki/memory/rejected.jsonl`
- Create: `wiki/memory/approved.jsonl`

**Rules:**
- Reject/flag secrets and volatile terms.
- Never auto-merge candidate reflections into canonical `reflections.jsonl` unless `--approve` is used.

**Verification:** propose a harmless reflection; verify it lands in candidates and evals still pass.

### Task 2.4: Update maintenance to process queue safely

**Objective:** Maintenance reports candidate counts and quarantines risky candidates.

**Files:**
- Modify: `scripts/maintain_memory_oracle.py`
- Modify: `wiki/concepts/memory-oracle.md`

---

## Phase 3 — Resilience and Operations

### Task 3.1: Automated Hermes state backup

**Objective:** Create sanitized backup script for critical Hermes state.

**Files:**
- Create: `scripts/backup_hermes_state.py`
- Create wrapper: `~/.hermes/scripts/backup_hermes_state.sh`
- Cron: `hermes-state-backup`

**Include:** skills, wiki, memory oracle, cron jobs metadata, non-secret config summary, scripts list.
**Exclude:** `.env`, tokens, credentials, raw logs, tmp dirs.

**Verification:** backup tar/bundle exists; no obvious secret strings; GitHub backup branch/tag pushed when auth permits.

### Task 3.2: Cron classification/risk report

**Objective:** Generate `wiki/cron-risk-report.md` with category/risk/delivery/side-effect classifications.

**Files:**
- Create: `scripts/classify_cron_jobs.py`
- Modify: `scripts/generate_system_map.py`

**Verification:** report includes all active jobs and identifies mutating/high-autonomy jobs.

### Task 3.3: Model routing policy

**Objective:** Add machine-readable and wiki-readable routing policy.

**Files:**
- Create: `config/model-routing-policy.yaml` or `wiki/model-routing-policy.md` if no config dir.
- Modify: `wiki/system-map.md` generation.

**Verification:** policy validates as YAML/JSON or docs render as markdown.

### Task 3.4: Windows offload scaffold

**Objective:** Add safe script to probe `ssh yin`, record GPU/OS/Python availability, and optionally run reflection/eval workloads remotely.

**Files:**
- Create: `scripts/windows_offload_probe.py`
- Update: `wiki/system-map.md` generation.

**Verification:** script either succeeds with host info or exits 0 with clear unavailable status.

---

## Phase 4 — True MeMo Experiment Scaffold

### Task 4.1: Experiment docs and dataset export

**Objective:** Export reflection corpus to training/eval format for future LoRA without running expensive training.

**Files:**
- Create: `experiments/memo/README.md`
- Create: `scripts/export_memo_dataset.py`
- Output: `experiments/memo/dataset/reflections_train.jsonl`, `reflections_eval.jsonl`

**Verification:** export produces deterministic train/eval split.

### Task 4.2: Baseline eval runner

**Objective:** Compare retrieval oracle vs optional local model command.

**Files:**
- Create: `scripts/run_memo_baseline_eval.py`

**Verification:** retrieval baseline reports pass/fail using current evals.

### Task 4.3: Optional training scaffold

**Objective:** Provide opt-in LoRA config/template, no training by default.

**Files:**
- Create: `experiments/memo/train_lora_template.yaml`
- Create: `experiments/memo/TRAINING.md`

**Verification:** docs clearly mark cost/risk and require explicit user action.

---

## Final Verification

Run:

```bash
python3 -m py_compile tools/memory_oracle_tool.py scripts/*.py
python3 scripts/generate_reflections.py --repo . --max-records 500 --include-website
python3 scripts/eval_memory_oracle.py --verbose
python3 scripts/maintain_memory_oracle.py --verbose
python3 scripts/generate_system_map.py --repo . --output wiki/system-map.md
python3 scripts/classify_cron_jobs.py --repo . --output wiki/cron-risk-report.md
python3 scripts/export_memo_dataset.py --repo .
python3 scripts/run_memo_baseline_eval.py --repo .
python3 -m pytest tests/tools/test_memory_oracle_tool.py -q -o 'addopts='
```

Then commit focused files and push to fork + backup branch/tag.
