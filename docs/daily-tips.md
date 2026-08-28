# pocket-eval tips of the day

> Maintained by `scripts/daily_update.py` (Daily Green automation) — one
> dated, non-empty evaluation tip per day, rotated from the pool in
> `scripts/tips_pool.json`. Pause by creating a `.daily-pause` file in the
> repo root, or unload the scheduler job (see README, Daily Green).


## 2026-08-24 — Eval tip of the day: A lexical baseline shows what counting buys

An n-gram model over your corpus is the cheapest known answer. Models that cannot beat it on definitional trivia are not 'thinking' — they are re-emitting training statistics.

> `pocket-eval qa --backend ngram`


## 2026-08-25 — Eval tip of the day: One run is a rumor

LLM evaluation is noisy: sampling, tie-breaking and batching shift scores. Report seeds, repeat runs, and treat single-run numbers as anecdotes, not evidence.

> `pocket-eval qa --backend ngram --seed 7`


## 2026-08-26 — Eval tip of the day: Perplexity is a fluency meter, not a reasoning meter

Perplexity measures how well a model predicts tokens. Tiny models can score low perplexity on memorized text yet fail every reasoning question; report both.

> `pocket-eval demo`


## 2026-08-27 — Eval tip of the day: Leakage is the silent inflator

If benchmark text appears in pretraining data, scores are rent, not capability. Write your own items (this repo's mini-benchmark is original) or check overlap first.


## 2026-08-28 — Eval tip of the day: Contamination corrupts comparisons

Comparing model A on a benchmark B already saw in training is unfair. Keep a held-out set nobody shipped, and re-derive it when models get refreshed.

