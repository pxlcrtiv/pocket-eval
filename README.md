# pocket-eval

[![CI](https://img.shields.io/github/actions/workflow/status/pxlcrtiv/pocket-eval/ci.yml?branch=main&label=CI)](https://github.com/pxlcrtiv/pocket-eval/actions)
[![License](https://img.shields.io/github/license/pxlcrtiv/pocket-eval)](LICENSE)
[![Stars](https://img.shields.io/github/stars/pxlcrtiv/pocket-eval)](https://github.com/pxlcrtiv/pocket-eval/stargazers)
[![Forks](https://img.shields.io/github/forks/pxlcrtiv/pocket-eval)](https://github.com/pxlcrtiv/pocket-eval/forks)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)

**The LLM eval harness that fits in your pocket.** CPU-only, keyless,
offline: evaluates language models on a bundled DeFi/on-chain/ML corpus —
perplexity + a 12-item multiple-choice mini-benchmark — with a
deterministic n-gram baseline that runs anywhere Python runs, and an
optional Hugging Face backend for real tiny models. **Zero runtime
dependencies, zero API keys, zero GPUs.**

## Problem

- Evaluations are the boring part of ML engineering — so they get skipped,
  or run ad-hoc with no baselines, no seeds, and no reproducible reports.
- State-of-the-art harnesses ([EleutherAI/lm-evaluation-harness](
  https://github.com/EleutherAI/lm-evaluation-harness)) assume a GPU farm
  and heavyweight model suites; they cannot run in CI or on a laptop.
- Nobody *reports the floor*: without a random baseline and a lexical
  baseline, a model's score is a headline, not a result.

## Solution

`pocket-eval` ships a self-contained evaluation in a single package:

| Backend | What it is | Requires |
| --- | --- | --- |
| `ngram` | add-1 smoothed bigram LM trained on the bundled corpus (stdlib-only, deterministic) | nothing |
| `random` | seeded uniform-choice chance floor | nothing |
| `huggingface` | any public causal LM (CPU, keyless) | `pip install "pocket-eval[hf]"` |

The bundled assets are **original and leakage-free**: a 15-doc corpus
(DeFi 101, smart-contract security, ERC standards, MEV, flash loans,
zk-rollups, LLM agents on-chain, …) and a 12-question multiple-choice
mini-benchmark with per-item topics and answers. You can swap in your own
corpus and items by editing the JSON/markdown in `pocket_eval/data/`.

## Quickstart

```bash
git clone https://github.com/pxlcrtiv/pocket-eval
cd pocket-eval
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Run the full bundled evaluation (ngram baseline):

```bash
pocket-eval demo
```

Score the mini-benchmark with a real (tiny) model — keyless, CPU, ~16 MB:

```bash
pip install "pocket-eval[hf]"
pocket-eval qa --backend huggingface --model sshleifer/tiny-gpt2
```

## Demo (live transcript, 2026-08-24)

```text
$ pocket-eval demo
# pocket-eval report

- model: **ngram-v1 (bundled bigram)**
- backend: `ngram` (seed 7)

## Perplexity (bundled corpus)

| metric | value |
| --- | --- |
| corpus tokens | 3487 |
| corpus perplexity | 520.72 |

## Multiple-choice QA (bundled mini-benchmark)

| metric | value |
| --- | --- |
| questions | 12 |
| correct | 10 |
| accuracy | 83.3% |
```

Run the chance floor:

```text
$ pocket-eval qa --backend random --seed 7
6/12 correct (50.0%)
  q01  correct  score=0.0000
  ...
```

And the honest comparison — a 15M-parameter model is *worse than chance*
on this benchmark, because its next-token probabilities are too flat to
discriminate options:

```text
$ pocket-eval qa --backend huggingface --model sshleifer/tiny-gpt2
2/12 correct (16.7%)
  q01  missed    score=0.0172
  ...

$ pocket-eval perplexity --backend huggingface --model distilgpt2 --json
{"perplexity": 1191.2760960550697}
```

## Results so far (real runs, keyless, CPU-only)

| Model / baseline | Corpus PPL | QA accuracy | What it shows |
| --- | --- | --- | --- |
| random (seed stream, avg) | — | ~25% | the chance floor |
| ngram-v1 (bundled bigram) | 520.7 | 10/12 (83.3%) | lexical co-occurrence memorizes definitions |
| `sshleifer/tiny-gpt2` | 49,982 | 2/12 (16.7%) | probabilities too flat to discriminate |
| `distilgpt2` | 1,191 | 3/12 (25.0%) | fluency ≠ definitional knowledge |
| `Qwen/Qwen2.5-0.5B-Instruct` | 4,918 | 3/12 (25.0%) | raw-logprob scoring ignores chat templates |

The lesson is the point of the harness: **a 10-line n-gram baseline over
the corpus beats GPT-2-class models on definitional items** — it memorizes
co-occurrence while small LMs emit fluent-but-flat probabilities, and
instruct-tuned models need chat-formatted scoring to answer at all. Plug
in a bigger or chat-templated scorer and watch the ordering flip; the
harness keeps the comparison reproducible either way.

## Commands

```bash
# full bundled evaluation (corpus perplexity + QA, markdown/json)
pocket-eval demo [--format json]

# perplexity of a sentence or the whole bundled corpus
pocket-eval perplexity "Flash loans must be repaid in the same transaction"
pocket-eval perplexity --backend huggingface --model distilgpt2

# multiple-choice QA with any backend
pocket-eval qa --backend ngram --seed 7
pocket-eval qa --backend random --seed 7
pocket-eval qa --backend huggingface --model sshleifer/tiny-gpt2 --format json

# deterministic corpus stats
pocket-eval corpus
```

## How it works

1. `tokenize()` — deterministic lowercase word tokenization (hyphenated
   terms like `checks-effects-interactions` stay one token).
2. `NgramLM` — add-1 smoothed word bigram trained at runtime on the bundled
   corpus; OOV words map to `<unk>` at query time only. Training is
   deterministic: same corpus bytes → same probabilities.
3. QA scoring — options are ranked by `log P(option | question)` (mean
   log-prob of the full sequence minus the question alone), the standard
   continuation score, applied identically to the n-gram and HF backends.
4. `RandomBaseline` — one seeded PRNG stream per run: varied picks,
   reproducible reports.
5. Reports render as stable markdown or JSON — no timestamps, no headers
   that would break diff-based regression review.

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -q        # 23 offline, deterministic tests (0.1s)
ruff check pocket_eval tests scripts
```

Every number in the tests is a golden: corpus stats, perplexities,
per-question predictions, seeded random picks. A dependency bump or data
edit that silently changes scores fails the build.

## Related portfolio repos

Built alongside my AI-security and blockchain tooling: [**inject-scout**](
https://github.com/pxlcrtiv/inject-scout) (prompt-injection scanner),
[**hf-hub-lint**](https://github.com/pxlcrtiv/hf-hub-lint) (HF Hub repo
linter), [**model-ledger**](https://github.com/pxlcrtiv/model-ledger)
(on-chain model provenance), and [**slither-chat**](
https://github.com/pxlcrtiv/slither-chat) (smart-contract audit copilot).
See the full AI/ML × blockchain portfolio on my
[profile](https://github.com/pxlcrtiv).

## Daily Green automation

This repo participates in the portfolio-wide daily-commit automation
(launchd on macOS 12:07 + 18:07 local, GitHub Actions
[`daily.yml`](.github/workflows/daily.yml) 12:00 UTC as cloud fallback).
Every day `scripts/daily_update.py` appends one curated LLM-evaluation tip
from `scripts/tips_pool.json` (24 entries) to `docs/daily-tips.md` and
pushes a dated, non-empty commit — idempotent, backfills missed days
(max 14), and never duplicates.

- Customize content: edit `scripts/tips_pool.json`.
- Pause this repo: `touch .daily-pause`.
- Pause globally: `launchctl bootout gui/$(id -u)/com.pxlcrtiv.daily-green`.

## License

MIT — see [LICENSE](LICENSE).