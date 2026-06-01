# MeMo Experiment Scaffold

This directory contains the opt-in scaffold for a future true MeMo-style MEMORY model experiment.

## Current baseline

The production system is still the source-linked retrieval memory oracle:

```bash
python3 scripts/query_memory_oracle.py "How does Hermes cron work?" --min-score 10 --verify-sources
python3 scripts/eval_memory_oracle.py --verbose
```

## Dataset export

```bash
python3 scripts/export_memo_dataset.py --repo .
```

Outputs:

- `experiments/memo/dataset/reflections_train.jsonl`
- `experiments/memo/dataset/reflections_eval.jsonl`

Format is chat-style JSONL plus metadata with source paths.

## Baseline eval

```bash
python3 scripts/run_memo_baseline_eval.py --repo .
```

This must pass before any model training is considered.

## Training policy

No training runs happen automatically. Training requires explicit user approval because it can consume GPU time, produce stale parametric memory, and reduce provenance. Prefer LoRA/QLoRA on a 1B-3B model first, compare against retrieval baseline, and keep retrieval/source verification even if the model improves.
