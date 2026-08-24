"""Scoring backends for pocket-eval.

Three tiers:
- ``NgramLM``     — bundled, stdlib-only, deterministic. Trains on the bundled
                    corpus at runtime; never touches the network.
- ``RandomBaseline`` — deterministic chance floor for QA (seeded).
- ``HFModel``     — optional. Loads small public causal LMs from Hugging Face
                    (keyless), CPU only. Requires ``transformers``.
"""

from __future__ import annotations

import math
import random
import re
from pathlib import Path

from .core import PerplexityError, tokenize

UNKNOWN = "<unk>"
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)*")


class NgramLM:
    """Add-1 smoothed bigram language model, trained on a bundled corpus.

    Fully deterministic: same corpus bytes -> same probabilities. Word-level,
    lowercase, OOV maps to ``<unk>`` (which is itself counted during
    training, so OOV sequences still get finite probabilities).
    """

    def __init__(self, corpus_docs: list[str]):
        self.vocab: dict[str, int] = {}
        self.unigram: dict[str, int] = {}
        self.bigram: dict[tuple[str, str], int] = {}
        self.total_tokens = 0
        for text in corpus_docs:
            prev: str | None = None
            for tok in tokenize(text):
                # Every token seen during training is in-vocabulary by
                # definition; <unk> is reserved for query-time OOV words.
                self._add_token(tok)
                if prev is not None:
                    self.bigram[(prev, tok)] = self.bigram.get((prev, tok), 0) + 1
                prev = tok
        self.vocab_size = len(self.vocab)

    def _add_token(self, tok: str) -> None:
        self.unigram[tok] = self.unigram.get(tok, 0) + 1
        self.total_tokens += 1
        if tok not in self.vocab:
            self.vocab[tok] = len(self.vocab)

    def _seen(self, tok: str) -> str:
        return tok if tok in self.vocab else UNKNOWN

    def logprob(self, prev: str | None, tok: str) -> float:
        """log P(tok | prev) with add-1 smoothing."""
        cur = self._seen(tok)
        if prev is None:
            return math.log((self.unigram.get(cur, 0) + 1) / (self.total_tokens + self.vocab_size + 1))
        p = self._seen(prev)
        denom = self.unigram.get(p, 0) + self.vocab_size
        num = self.bigram.get((p, cur), 0) + 1
        return math.log(num / denom)

    def mean_logprob(self, tokens: list[str]) -> float:
        """Mean per-token log-probability; raises PerplexityError if empty."""
        if not tokens:
            raise PerplexityError("empty token sequence")
        total = 0.0
        for i, tok in enumerate(tokens):
            lp = self.logprob(tokens[i - 1] if i else None, tok)
            if not math.isfinite(lp):
                raise PerplexityError(f"non-finite logprob for token {tok!r}")
            total += lp
        return total / len(tokens)

    def perplexity(self, text: str) -> float:
        toks = tokenize(text)
        if not toks:
            raise PerplexityError("text contains no tokenizable words")
        m = self.mean_logprob(toks)
        return math.exp(-m)

    def score_continuation(self, q_tokens: list[str], opt_tokens: list[str]) -> float:
        """Conditional continuation score: mean log-prob of the question+option
        sequence minus the question alone — i.e. log P(option | question).
        Deterministic; ranks options by how much the option tokens change the
        probability of the prompt, which counteracts option-length bias."""
        if not opt_tokens:
            return -math.inf
        if not q_tokens:
            return self.mean_logprob(opt_tokens)
        full = self.mean_logprob(q_tokens + opt_tokens)
        q_only = self.mean_logprob(q_tokens)
        return full - q_only


class RandomBaseline:
    """Seeded uniform-choice baseline — the honest chance floor for QA.

    Uses one persistent PRNG per evaluation so picks form a stream (varied
    per question) while staying fully deterministic across runs.
    """

    def __init__(self, seed: int = 7):
        self.seed = seed
        self._rng = random.Random(seed)

    def pick(self, option_count: int) -> int:
        return self._rng.randrange(option_count)

    def score_continuation(self, q_tokens: list[str], opt_tokens: list[str]) -> float:
        # Random baseline scores are not meaningful; the CLI handles picking
        # directly. This stub keeps the backend interface uniform.
        raise NotImplementedError("RandomBaseline is a picker, not a scorer")


class HFModel:
    """Optional Hugging Face causal-LM backend (CPU, keyless, small models).

    Importing transformers is deferred so the default install needs nothing
    beyond the stdlib; ``transformers`` is only required when this backend is
    actually used.
    """

    DEFAULT_MODEL = "sshleifer/tiny-gpt2"

    def __init__(self, model_id: str | None = None, max_length: int = 512):
        self.model_id = model_id or self.DEFAULT_MODEL
        self.max_length = max_length
        self._model = None
        self._tok = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            import transformers
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "The 'huggingface' backend needs the optional dependency: "
                "pip install 'pocket-eval[hf]' (installs transformers)"
            ) from exc
        try:
            self._tok = transformers.AutoTokenizer.from_pretrained(self.model_id)
            self._model = transformers.AutoModelForCausalLM.from_pretrained(
                self.model_id, torch_dtype="auto", low_cpu_mem_usage=True
            )
            self._model.eval()
        except Exception as exc:  # pragma: no cover - network/model dependent
            raise RuntimeError(
                f"failed to load model {self.model_id!r} (offline? wrong id?): {exc}"
            ) from exc

    def corpus_perplexity(self, corpus_docs: list[str]) -> tuple[float, int]:
        """Corpus perplexity via the model's own cross-entropy loss."""
        self._load()
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "The 'huggingface' backend needs optional dependencies: "
                "pip install 'pocket-eval[hf]' (installs transformers + torch)"
            ) from exc
        tok = self._tok
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        enc = tok(
            corpus_docs,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=True,
        )
        with torch.no_grad():
            out = self._model(**enc, labels=enc["input_ids"])
        loss = float(out.loss.item())
        total_tokens = int((enc["attention_mask"].sum()).item())
        if loss <= 0 or total_tokens == 0:
            raise PerplexityError("model returned a non-positive loss; cannot compute perplexity")
        return math.exp(loss), total_tokens

    def score_continuation(self, q_tokens: list[str], opt_tokens: list[str]) -> float:
        """log P(option | question): mean log-prob of the full sequence minus
        the question prefix (standard continuation scoring)."""
        self._load()
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "The 'huggingface' backend needs optional dependencies: "
                "pip install 'pocket-eval[hf]' (installs transformers + torch)"
            ) from exc
        tok = self._tok
        q_text = " ".join(q_tokens)
        full_text = q_text + " " + " ".join(opt_tokens)

        def seq_logprob(text: str) -> float:
            ids = tok(text, return_tensors="pt")["input_ids"]
            if ids.numel() == 0:
                return -math.inf
            with torch.no_grad():
                logits = self._model(ids).logits[0, :-1, :]
            logp = torch.log_softmax(logits.float(), dim=-1)
            chosen = logp[torch.arange(ids.numel() - 1), ids[0][1:]]
            return float(chosen.mean().item())

        full = seq_logprob(full_text)
        q_only = seq_logprob(q_text)
        return full - q_only


def load_corpus(data_dir: Path) -> list[str]:
    """Read bundled corpus markdown docs in stable filename order."""
    corpus_dir = data_dir / "corpus"
    docs = sorted(corpus_dir.glob("*.md"))
    if not docs:
        raise FileNotFoundError(f"no corpus docs under {corpus_dir}")
    return [d.read_text(encoding="utf-8") for d in docs]


def token_stats(corpus_docs: list[str]) -> dict:
    """Deterministic corpus statistics for the report."""
    n_tokens = 0
    vocab: set[str] = set()
    for doc in corpus_docs:
        toks = tokenize(doc)
        n_tokens += len(toks)
        vocab.update(toks)
    return {"docs": len(corpus_docs), "tokens": n_tokens, "vocab": len(vocab)}


def make_ngram(corpus_docs: list[str]) -> NgramLM:
    from functools import lru_cache

    @lru_cache(maxsize=1)
    def _build() -> NgramLM:
        return NgramLM(corpus_docs)

    return _build()