# Contributing

Thanks for helping make pocket-eval better. This is a focused, deterministic
LLM-evaluation harness for CPU-only environments: **offline-testable,
zero-runtime-dependencies, boring by design**. Please keep those properties.

## Ground rules

- **No runtime dependencies.** The default path (n-gram + random baselines)
  is pure Python stdlib. Hugging Face models stay an optional extra
  (`pip install "pocket-eval[hf]"`), imported lazily, never required.
- **Deterministic output.** Same input + same seed → same report. No
  timestamps, no randomness, no set-ordering dependence, no wall-clock in
  results.
- **Golden tests for every behavior change.** If a score, perplexity, or
  pick changes, update the golden numbers in `tests/` deliberately — that
  diff _is_ the changelog.
- **Tests stay offline.** No network, no model downloads, ever.
- **Benchmark items must be original.** No scraped benchmark text — this
  repo's corpus and mini-benchmark are self-written to avoid leakage.

## Daily Green

The repo commits one dated entry per day via `scripts/daily_update.py`
(pool: `scripts/tips_pool.json`). Add eval tips to the pool; never edit
`docs/daily-tips.md` by hand.

## PR process

1. Fork, branch, change, test: `python -m pytest tests/ -q` (all green).
2. `ruff check pocket_eval tests scripts` clean.
3. CLI smoke: `pocket-eval demo | head`.
4. Reference the golden numbers you changed (and why) in the PR body.

## Style

- Type hints on all public functions; `py3.10+`.
- Numbers in README come from real runs — re-run the command, don't retype
  the output.