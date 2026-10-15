# ADR-0001: Backends sit behind a Backend protocol seam

- Status: accepted
- Date: 2026-10-15

## Context

The eval loop (`cli.run_eval`) and the `perplexity` command both dispatched on
a `backend: str` ("ngram" | "random" | "huggingface") with if/elif trees. The
same string appeared in five conditions across cli.py; `RandomBaseline`
deliberately violated the informal interface (`score_continuation` raised
`NotImplementedError`); and the QA loop — the core logic of the tool — was
testable only end-to-end through the CLI. A duplicated mean-logprob loop also
existed in both `core.average_logprob` and `NgramLM.mean_logprob`.

## Decision

1. `core.Backend` is a `@runtime_checkable` Protocol with `name`,
   `answer(question, options) -> (idx, score)`, and `corpus_ppl(corpus)`.
   All three backends implement it; the eval loop branches on nothing.
2. String→Backend mapping happens exactly once, in `backends.make_backend`.
   The string never escapes the CLI parser boundary.
3. `NgramLM.mean_logprob` delegates to `core.average_logprob` — one
   implementation of the mean-logprob loop, shared by every seam.
4. Dead code removed: the unused `_TOKEN_RE` regex copy in backends.py.

`run_eval` accepts either a backend name (resolved via `make_backend`) or any
object satisfying the seam — the latter is what makes the QA loop unit-testable
with a scripted fake backend.

## Consequences

- Adding a backend = one new class + one factory line; no dispatch-tree edits.
- The QA loop is tested with a `FakeBackend` (scripted scores) in addition to
  the golden end-to-end tests; all previous golden values (perplexity 520.7238,
  QA 10/12, seed-7 random stream) are unchanged and still enforced.
- `seed` in the report is CLI-derived metadata for local deterministic
  backends (ngram/random); it is not part of the seam.
- Not adopted (deferred, not rejected): an `EvalRequest` dataclass for
  `run_eval`'s six parameters — collapses naturally if a future backend needs
  per-request options.
