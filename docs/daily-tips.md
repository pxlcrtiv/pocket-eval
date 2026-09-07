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


## 2026-08-29 — Eval tip of the day: Tokenization is part of the model

BPE boundaries change what a prompt means to the model. 'erc 20' tokenizes differently than 'erc-20' — normalize inputs the same way for every model you compare.


## 2026-08-30 — Eval tip of the day: Short options inflate accuracy

With 4 short options, a model can win by pattern-matching surface form. Vary option length and distractors or you will measure format, not understanding.


## 2026-08-31 — Eval tip of the day: Score, then squint

Look at per-item scores, not just accuracy. Flat scores near zero mean the model cannot discriminate options at all — that is a finding, and it explains the accuracy.

> `pocket-eval qa --backend huggingface --format json`


## 2026-09-01 — Eval tip of the day: Match the prompt format to the model family

Instruct-tuned models expect chat templates; base models expect raw text. Scoring with the wrong format degrades every number you publish.


## 2026-09-02 — Eval tip of the day: Determinism is a feature of harnesses

Same model + same seed + same input must give the same report. If your eval is not bit-reproducible, regressions are invisible and comparisons are marketing.

> `pocket-eval demo --format json`


## 2026-09-03 — Eval tip of the day: Bound the runtime dependency

An eval that needs a GPU or an API key cannot run in CI, so it never runs. Keep a deterministic offline baseline in the default path — it is your regression gate.


## 2026-09-04 — Eval tip of the day: Benchmarks rot; corpora rot

Domain language changes ('NFT', 'L2', 'AA') and models absorb old benchmarks. Refresh the corpus and the item set on a calendar, not when someone remembers.


## 2026-09-05 — Eval tip of the day: Sample size tells you what to believe

The difference between 8/12 and 10/12 on one mini-benchmark is weak evidence. Scale items to 100+ before claiming a model is better; use the mini version to sanity-check pipelines.


## 2026-09-06 — Eval tip of the day: Report the floor and the ceiling

Random chance (floor) and the lexical baseline (cheap ceiling) bracket every model score. Publish all three; a score without context is a headline, not a result.

> `pocket-eval demo`


## 2026-09-07 — Eval tip of the day: Human review is the terminal test

Automated metrics miss the label errors, ambiguous items and tricks. Every release, hand-audit a sample of items and a sample of model answers.

