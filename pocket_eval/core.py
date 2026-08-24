"""Core evaluation math: perplexity and multiple-choice QA scoring."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

WORD_RE = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokenization — deterministic, locale-independent.

    >>> tokenize("Flash loans! ERC-20, don't.")
    ['flash', 'loans', 'erc-20', "don't"]
    """
    return [m.group(0) for m in WORD_RE.finditer(text.lower())]


@dataclass(frozen=True)
class QaItem:
    """One multiple-choice question from the bundled mini-benchmark."""

    id: str
    topic: str
    question: str
    options: tuple[str, ...]
    answer: int

    @classmethod
    def from_dict(cls, d: dict) -> QaItem:
        opts = tuple(str(o) for o in d["options"])
        if len(opts) != 4:
            raise ValueError(f"{d['id']}: expected 4 options, got {len(opts)}")
        ans = int(d["answer"])
        if not 0 <= ans < 4:
            raise ValueError(f"{d['id']}: answer index out of range: {ans}")
        return cls(id=str(d["id"]), topic=str(d["topic"]), question=str(d["question"]), options=opts, answer=ans)


@dataclass(frozen=True)
class QaResult:
    """Scored answers for one question."""

    item_id: str
    correct: bool
    predicted: int
    score: float  # chosen-option score (log-prob per token, higher = better)


class PerplexityError(ValueError):
    """Raised when a text cannot be scored (no in-vocabulary tokens)."""


def average_logprob(tokens: list[str], score_next) -> float:
    """Mean per-token log-probability of *tokens* given a scoring callable.

    ``score_next(prev, tok)`` returns the log-probability of ``tok`` given
    the previous token (or None for a sequence start). Deterministic given
    the callable.
    """
    if not tokens:
        raise PerplexityError("cannot score an empty token sequence")
    total = 0.0
    for i, tok in enumerate(tokens):
        prev = tokens[i - 1] if i > 0 else None
        lp = score_next(prev, tok)
        if lp is None or not math.isfinite(lp):
            raise PerplexityError(f"no probability for token {tok!r} at position {i}")
        total += lp
    return total / len(tokens)


def perplexity_from_logprobs(logprobs: list[float]) -> float:
    """Perplexity from per-token log-probabilities (natural log).

    PPL = exp(-mean(log p)). Deterministic by construction.
    """
    if not logprobs:
        raise PerplexityError("cannot compute perplexity of an empty sequence")
    return math.exp(-sum(logprobs) / len(logprobs))


def best_option(question: str, options: tuple[str, ...], score_continuation) -> tuple[int, float]:
    """Pick the option a scorer rates as the most likely continuation.

    ``score_continuation(question_tokens, option_tokens)`` returns the mean
    log-probability of the option tokens given the question tokens.
    Returns ``(option_index, score)`` — ties resolved by lowest index.
    """
    q_tokens = tokenize(question)
    best_i, best_score = 0, -math.inf
    for i, opt in enumerate(options):
        s = score_continuation(q_tokens, tokenize(opt))
        if s > best_score:
            best_i, best_score = i, s
    return best_i, best_score


@dataclass
class EvalReport:
    """Full evaluation snapshot for one model/backend."""

    model: str
    backend: str
    seed: int | None
    corpus_ppl: float | None
    corpus_tokens: int
    qa_total: int
    qa_correct: int
    qa_accuracy: float
    qa_details: list[QaResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def qa_summary(self) -> str:
        return f"{self.qa_correct}/{self.qa_total} correct ({self.qa_accuracy:.1%})"