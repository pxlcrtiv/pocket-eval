"""Deep evaluation module: the QA / perplexity loop behind one interface.

This module holds the eval loop (``run_eval``) so that the loop lives in its
own deep module, beside ``EvalReport`` / ``QaResult``, instead of inside the
CLI adapter.  The loop branches on nothing: every backend-specific decision —
report seed, corpus token count, notes — lives behind the ``Backend`` seam.

The module keeps the exact string-or-adapter interface of the loop it replaces:

* ``run_eval(backend, model, seed, corpus, items, with_ppl)`` accepts either
  a backend *name* (str, resolved via ``backends.make_backend``) or any object
  satisfying the ``core.Backend`` protocol.
* The ``Backend`` seam — ``name`` / ``seed`` / ``answer`` / ``score_corpus`` /
  ``report_notes`` — and ``backends.make_backend`` do not change shape.
"""

from __future__ import annotations

from .backends import make_backend
from .core import (
    CorpusScore,
    EvalReport,
    QaItem,
    QaResult,
)


def run_eval(backend, model: str | None, seed: int, corpus: list[str], items: list[QaItem], with_ppl: bool) -> EvalReport:
    """Evaluate one backend over the bundled benchmark, deterministically.

    *backend* is either a backend name (str) — resolved here via
    ``make_backend`` — or any object satisfying the ``core.Backend`` seam
    (name / seed / answer / score_corpus / report_notes). The loop below
    branches on nothing: every backend-specific decision, including the
    report's seed, token count, and notes, lives behind the seam.
    """
    backend_obj = make_backend(backend, corpus, model, seed) if isinstance(backend, str) else backend
    score = backend_obj.score_corpus(corpus) if with_ppl else CorpusScore(None, 0)

    details: list[QaResult] = []
    for it in items:
        predicted, qa_score = backend_obj.answer(it.question, it.options)
        details.append(QaResult(it.id, predicted == it.answer, predicted, qa_score))

    correct = sum(1 for d in details if d.correct)
    accuracy = correct / len(items) if items else 0.0
    return EvalReport(
        model=model or backend_obj.name,
        backend=backend_obj.name,
        seed=backend_obj.seed,
        corpus_ppl=score.perplexity,
        corpus_tokens=score.tokens,
        qa_total=len(items),
        qa_correct=correct,
        qa_accuracy=accuracy,
        qa_details=details,
        notes=list(backend_obj.report_notes()),
    )
