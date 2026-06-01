# MEMORY Model Training Notes

This is intentionally opt-in.

## Preconditions

- Retrieval baseline passes.
- Dataset has been reviewed for secrets and volatile facts.
- Training target is small first: 1B-3B model, LoRA/QLoRA.
- Evaluation compares against `scripts/run_memo_baseline_eval.py`.

## Candidate command shape

```bash
# Example only; do not run automatically.
mlx_lm.lora \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --train \
  --data experiments/memo/dataset \
  --batch-size 2 \
  --iters 200
```

## Keep even if training works

- Source-linked retrieval oracle
- `--verify-sources`
- evals
- review queues
- live tools for current truth
