"""pocket-eval CLI — deterministic eval commands, keyless by default."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .backends import HFModel, RandomBaseline, load_corpus, make_ngram, token_stats
from .core import EvalReport, QaItem, QaResult, best_option

DATA_DIR = Path(__file__).resolve().parent / "data"
BACKENDS = ("ngram", "random", "huggingface")
EXIT_OK, EXIT_NO_BACKEND, EXIT_ERROR = 0, 2, 1


def load_qa_bench() -> list[QaItem]:
    bench_path = DATA_DIR / "bench" / "qa_mini.json"
    raw = json.loads(bench_path.read_text(encoding="utf-8"))
    return [QaItem.from_dict(d) for d in raw["questions"]]


def run_eval(backend: str, model: str | None, seed: int, corpus: list[str], items: list[QaItem], with_ppl: bool) -> EvalReport:
    """Evaluate one backend over the bundled benchmark, deterministically."""
    notes: list[str] = []
    corpus_ppl: float | None = None
    corpus_tokens = 0
    if with_ppl:
        stats = token_stats(corpus)
        corpus_tokens = stats["tokens"]
        if backend == "ngram":
            corpus_ppl = make_ngram(corpus).perplexity(" ".join(corpus))
        elif backend == "huggingface":
            hf = HFModel(model)
            corpus_ppl, corpus_tokens = hf.corpus_perplexity(corpus)
            notes.append(f"HF model: {hf.model_id}")
        else:
            corpus_ppl = None

    details: list[QaResult] = []
    if backend in ("random", "ngram") or backend == "huggingface":
        if backend == "random":
            picker = RandomBaseline(seed)
            for it in items:
                predicted = picker.pick(len(it.options))
                details.append(QaResult(it.id, predicted == it.answer, predicted, 0.0))
            notes.append("random baseline: uniform chance floor (seeded, deterministic)")
        else:
            scorer = make_ngram(corpus) if backend == "ngram" else HFModel(model)
            for it in items:
                predicted, score = best_option(it.question, it.options, scorer.score_continuation)
                details.append(QaResult(it.id, predicted == it.answer, predicted, score))
    correct = sum(1 for d in details if d.correct)
    accuracy = correct / len(items) if items else 0.0

    if backend == "huggingface" and not details:
        # models that cannot score options (e.g. encoder-only) still get a report
        notes.append("QA skipped: backend scored no options")
    return EvalReport(
        model=model or ({"ngram": "ngram-v1 (bundled bigram)", "random": "random-uniform", "huggingface": HFModel.DEFAULT_MODEL}.get(backend, backend)),
        backend=backend,
        seed=seed if backend in ("random", "ngram") else None,
        corpus_ppl=corpus_ppl,
        corpus_tokens=corpus_tokens,
        qa_total=len(items),
        qa_correct=correct,
        qa_accuracy=accuracy,
        qa_details=details,
        notes=notes,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pocket-eval",
        description="CPU-only, keyless LLM evaluation: perplexity + multiple-choice QA.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="full bundled evaluation (ngram + random baselines)")
    d.add_argument("--format", choices=("markdown", "json"), default="markdown")
    d.add_argument("--seed", type=int, default=7)

    c = sub.add_parser("perplexity", help="perplexity of a text or the bundled corpus")
    c.add_argument("text", nargs="?", help="text to score (default: whole bundled corpus)")
    c.add_argument("--backend", choices=BACKENDS, default="ngram")
    c.add_argument("--model", default=None, help="HF model id for --backend huggingface")
    c.add_argument("--json", action="store_true", help="print JSON result")

    q = sub.add_parser("qa", help="multiple-choice QA on the bundled mini-benchmark")
    q.add_argument("--backend", choices=BACKENDS, default="ngram")
    q.add_argument("--model", default=None, help="HF model id for --backend huggingface")
    q.add_argument("--seed", type=int, default=7)
    q.add_argument("--format", choices=("markdown", "json", "table"), default="table")

    m = sub.add_parser("corpus", help="stats about the bundled corpus")
    m.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    corpus = load_corpus(DATA_DIR)
    try:
        if args.command == "corpus":
            stats = token_stats(corpus)
            if args.json:
                print(json.dumps(stats, sort_keys=True))
            else:
                print(f"docs: {stats['docs']} | tokens: {stats['tokens']} | vocab: {stats['vocab']}")
            return EXIT_OK

        if args.command == "perplexity":
            if args.backend == "ngram":
                lm = make_ngram(corpus)
                ppl = lm.perplexity(args.text if args.text else " ".join(corpus))
            elif args.backend == "huggingface":
                try:
                    hf = HFModel(args.model)
                    ppl, _ = hf.corpus_perplexity([args.text] if args.text else corpus)
                except RuntimeError as exc:
                    print(f"error: {exc}", file=sys.stderr)
                    return EXIT_NO_BACKEND
            else:
                print("error: --backend random cannot compute perplexity", file=sys.stderr)
                return EXIT_ERROR
            if getattr(args, "json", False):
                print(json.dumps({"perplexity": ppl}, sort_keys=True))
            else:
                print(f"perplexity: {ppl:.2f}")
            return EXIT_OK

        if args.command == "qa":
            items = load_qa_bench()
            report = run_eval(args.backend, args.model, args.seed, corpus, items, with_ppl=False)
            if args.format == "json":
                from .report import render_json

                print(render_json(report), end="")
            elif args.format == "markdown":
                from .report import render_markdown

                print(render_markdown(report))
            else:
                print(report.qa_summary)
                for d in report.qa_details:
                    mark = "correct" if d.correct else "missed  "
                    print(f"  {d.item_id}  {mark}  score={d.score:.4f}")
            return EXIT_OK

        if args.command == "demo":
            items = load_qa_bench()
            report = run_eval("ngram", None, args.seed, corpus, items, with_ppl=True)
            if report.corpus_ppl:
                report.notes.insert(0, "ngram baseline: bundled add-1 bigram LM (stdlib-only, deterministic)")
            if args.format == "json":
                from .report import render_json

                print(render_json(report), end="")
            else:
                from .report import render_markdown

                print(render_markdown(report))
            return EXIT_OK
    except Exception as exc:  # noqa: BLE001 - CLI boundary; report and exit non-zero
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())