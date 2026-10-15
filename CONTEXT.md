# Domain Context — pocket-eval

## Scope
This repo's domain vocabulary and architectural decisions.

## Glossary
See parent CONTEXT.md for shared domain terms.

- **Backend** — the evaluation seam: any object with `name`, `answer(question, options) -> (idx, score)`, and `corpus_ppl(corpus) -> float | None`. The eval loop (`run_eval`) branches on nothing — every backend-specific decision lives behind this interface. Implementations: `NgramLM` (bundled bigram scorer), `RandomBaseline` (seeded chance floor), `HFModel` (optional Hugging Face). CLI strings ("ngram" | "random" | "huggingface") become Backends exactly once, in `backends.make_backend`.

## Architecture Decisions
See `docs/adr/`.

## Hot Spots
- `pocket_eval/cli.py` — `run_eval` / `main`: CLI argument parsing and report dispatch
- `pocket_eval/backends.py` — backend implementations + `make_backend` factory
- `pocket_eval/core.py` — eval math + the `Backend` protocol
