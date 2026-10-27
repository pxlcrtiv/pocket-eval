"""Offline, deterministic tests for pocket-eval. No network, no models."""

from __future__ import annotations

import json
import math

import pytest

from pocket_eval.backends import NgramLM, RandomBaseline, load_corpus, token_stats
from pocket_eval.cli import DATA_DIR, load_qa_bench
from pocket_eval.core import (
    PerplexityError,
    QaItem,
    best_option,
    perplexity_from_logprobs,
    tokenize,
)

CORPUS = load_corpus(DATA_DIR)
LM = NgramLM(CORPUS)  # module-level so golden tests share one deterministic model
ITEMS = load_qa_bench()


# ---------------------------------------------------------------- tokenizer
def test_tokenize_basic():
    assert tokenize("Flash loans! ERC-20, don't.") == ["flash", "loans", "erc-20", "don't"]


def test_tokenize_empty_and_punct():
    assert tokenize("!!! ...") == []


# ---------------------------------------------------------------- corpus data
def test_corpus_stats_golden():
    stats = token_stats(CORPUS)
    assert stats == {"docs": 15, "tokens": 3487, "vocab": 1183}


def test_qa_bench_schema():
    assert len(ITEMS) == 12
    ids = [it.id for it in ITEMS]
    assert len(set(ids)) == len(ids)
    for it in ITEMS:
        assert len(it.options) == 4
        assert 0 <= it.answer < 4
        assert it.topic


def test_qa_item_rejects_bad_shape():
    with pytest.raises(ValueError):
        QaItem.from_dict({"id": "x", "topic": "t", "question": "q", "options": ["a", "b"], "answer": 1})
    with pytest.raises(ValueError):
        QaItem.from_dict({"id": "x", "topic": "t", "question": "q", "options": ["a", "b", "c", "d"], "answer": 7})


# ---------------------------------------------------------------- n-gram LM
def test_ngram_corpus_perplexity_golden():
    ppl = LM.perplexity(" ".join(CORPUS))
    assert ppl == pytest.approx(520.7238, abs=1e-3)


def test_ngram_sentence_perplexity_golden():
    ppl = LM.perplexity("Flash loans must be repaid in the same transaction")
    assert ppl == pytest.approx(453.474309, abs=1e-4)


def test_ngram_oov_penalized_and_finite():
    in_domain = LM.perplexity("The seed phrase can regenerate every address in a wallet")
    oov = LM.perplexity("zzzqqq xyzzy quarkwark")
    assert math.isfinite(oov)
    assert oov > in_domain  # unknown words must be harder, never impossible


def test_ngram_deterministic_across_instances():
    lm2 = NgramLM(CORPUS)
    assert lm2.perplexity("Flash loans must be repaid in the same transaction") == pytest.approx(
        LM.perplexity("Flash loans must be repaid in the same transaction"), abs=1e-12
    )
    assert lm2.total_tokens == LM.total_tokens
    assert lm2.vocab_size == LM.vocab_size


def test_ngram_empty_text_raises():
    with pytest.raises(PerplexityError):
        LM.perplexity("")


def test_perplexity_from_logprobs_golden():
    # exp(-(-2.302585...)) == 10
    assert perplexity_from_logprobs([-math.log(10.0)]) == pytest.approx(10.0, abs=1e-9)
    assert perplexity_from_logprobs([0.0, 0.0]) == pytest.approx(1.0, abs=1e-9)


def test_ngram_qa_golden_10_of_12():
    predicted: dict[str, int] = {}
    for it in ITEMS:
        pred, _ = best_option(it.question, it.options, LM.score_continuation)
        predicted[it.id] = pred
    assert predicted == {
        "q01": 2, "q02": 1, "q03": 2, "q04": 0, "q05": 2,
        "q06": 0, "q07": 1, "q08": 2, "q09": 3, "q10": 3,
        "q11": 2, "q12": 3,
    }
    correct = sum(1 for it in ITEMS if predicted[it.id] == it.answer)
    assert correct == 10  # the two misses are the known reasoning-ish items q03/q10


def test_best_option_tie_goes_to_first():
    pred, _ = best_option("What token standard?",
                          ("ERC 20", "ERC 20", "ERC 20", "ERC 721"),
                          LM.score_continuation)
    assert pred == 0


# ---------------------------------------------------------------- random baseline
def test_random_baseline_seeded_deterministic():
    rb = RandomBaseline(seed=7)
    picks = [rb.pick(4) for _ in range(12)]
    assert picks == [2, 1, 3, 0, 0, 0, 2, 0, 1, 0, 0, 3]
    correct = sum(1 for pick, it in zip(picks, ITEMS) if pick == it.answer)
    assert correct == 6  # golden: seed 7 -> 6/12; the ^-average over seeds is ~25%


def test_random_baseline_approximates_chance():
    accs = []
    for seed in range(20):
        rb = RandomBaseline(seed=seed)
        picks = [rb.pick(4) for _ in range(12)]
        accs.append(sum(1 for p, it in zip(picks, ITEMS) if p == it.answer) / 12)
    mean = sum(accs) / len(accs)
    assert 0.15 <= mean <= 0.35  # deterministic-but-random: ~25% across seeds


# ---------------------------------------------------------------- reports
def test_report_markdown_deterministic_and_complete():
    from pocket_eval.cli import run_eval
    from pocket_eval.report import render_markdown

    r = run_eval("ngram", None, 7, CORPUS, ITEMS, with_ppl=True)
    md = render_markdown(r)
    assert "# pocket-eval report" in md
    assert "520.72" in md
    assert "83.3%" in md
    assert "ngram-v1" in md
    assert "seed 7" in md
    assert "2026-" not in md  # no timestamps anywhere


def test_report_json_roundtrip():
    from pocket_eval.cli import run_eval
    from pocket_eval.report import render_json

    r = run_eval("ngram", None, 7, CORPUS, ITEMS, with_ppl=True)
    payload = json.loads(render_json(r))
    assert payload["qa"]["correct"] == 10
    assert payload["qa"]["total"] == 12
    assert payload["corpus"]["perplexity"] == pytest.approx(520.7238, abs=1e-3)
    assert len(payload["qa"]["details"]) == 12


# ---------------------------------------------------------------- CLI
def test_cli_demo_exit_zero(capsys):
    from pocket_eval.cli import main

    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "corpus perplexity" in out
    assert "accuracy" in out


def test_cli_qa_table(capsys):
    from pocket_eval.cli import main

    assert main(["qa", "--backend", "ngram", "--seed", "7"]) == 0
    out = capsys.readouterr().out
    assert "10/12 correct" in out


def test_cli_perplexity_command(capsys):
    from pocket_eval.cli import main

    assert main(["perplexity", "Flash loans must be repaid in the same transaction"]) == 0
    assert "453.47" in capsys.readouterr().out


def test_cli_corpus_command(capsys):
    from pocket_eval.cli import main

    assert main(["corpus"]) == 0
    assert "docs: 15" in capsys.readouterr().out


def test_cli_hf_backend_graceful_without_transformers(monkeypatch, capsys):
    from pocket_eval import backends
    from pocket_eval.cli import main

    def boom(self):
        raise RuntimeError("The 'huggingface' backend needs the optional dependency")

    monkeypatch.setattr(backends.HFModel, "_load", boom)
    assert main(["qa", "--backend", "huggingface"]) == 1
    err = capsys.readouterr().err
    assert "huggingface" in err


def test_cli_demo_json_valid(capsys):
    from pocket_eval.cli import main

    assert main(["demo", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["qa"]["correct"] == 10


# ---------------------------------------------------------------- backend seam
def test_backend_protocol_conformance():
    """Every real backend satisfies the core.Backend seam — the eval loop
    can treat them interchangeably."""
    from pocket_eval.core import Backend

    for backend in (NgramLM(CORPUS), RandomBaseline(seed=7)):
        assert isinstance(backend, Backend)
        assert backend.name
        idx, score = backend.answer("What is a flash loan?", ("a", "b", "c", "d"))
        assert 0 <= idx < 4
        assert isinstance(score, float)


def test_make_backend_factory():
    from pocket_eval.backends import HFModel, make_backend

    assert isinstance(make_backend("ngram", CORPUS), NgramLM)
    rb = make_backend("random", CORPUS, seed=3)
    assert isinstance(rb, RandomBaseline)
    assert rb.seed == 3
    assert isinstance(make_backend("huggingface", CORPUS, model="x/y"), HFModel)
    with pytest.raises(ValueError):
        make_backend("bogus", CORPUS)


def test_run_eval_accepts_a_fake_backend():
    """The payoff of the seam: the eval loop is unit-testable with a scripted
    fake — no corpus, no model, no CLI strings."""
    from pocket_eval.cli import run_eval

    class FakeBackend:
        name = "fake"
        seed = None

        def answer(self, question, options):
            return (0, 1.5)  # always pick the first option, fixed score

        def corpus_ppl(self, corpus):
            return 42.0

    items = [
        QaItem(id="a", topic="t", question="q1", options=("x", "y", "z", "w"), answer=0),
        QaItem(id="b", topic="t", question="q2", options=("x", "y", "z", "w"), answer=3),
    ]
    r = run_eval(FakeBackend(), None, 7, [], items, with_ppl=True)
    assert r.backend == "fake"
    assert r.model == "fake"
    assert r.corpus_ppl == 42.0
    assert r.corpus_tokens == 0  # token_stats([]) -> 0 tokens, no corpus needed
    assert r.qa_total == 2
    assert r.qa_correct == 1  # item a: picked 0 == answer 0
    assert r.qa_accuracy == 0.5
    assert [d.score for d in r.qa_details] == [1.5, 1.5]


def test_run_eval_string_still_works():
    """Backwards compatibility: the CLI passes strings, resolved by the factory."""
    from pocket_eval.cli import run_eval

    r = run_eval("ngram", None, 7, CORPUS, ITEMS, with_ppl=False)
    assert r.qa_correct == 10
    assert r.backend == "ngram-v1 (bundled bigram)"


def test_average_logprob_is_shared():
    """core.average_logprob is now exercised through NgramLM — one implementation."""
    from pocket_eval.core import PerplexityError, average_logprob

    with pytest.raises(PerplexityError):
        average_logprob([], lambda prev, tok: -1.0)
    # a fixed scorer makes the math exact: mean of three -1.0s
    assert average_logprob(["a", "b", "c"], lambda prev, tok: -1.0) == -1.0
    # NgramLM's mean_logprob routes through the same function
    assert LM.mean_logprob(["flash", "loans"]) == pytest.approx(
        average_logprob(["flash", "loans"], LM.logprob), abs=1e-12
    )


# ---------------------------------------------------------------- perplexity seam
def test_run_perplexity_accepts_a_fake_backend():
    """The perplexity path is unit-testable with a scripted fake — no corpus,
    no model, no CLI strings."""
    from pocket_eval.cli import run_perplexity

    class FakeBackend:
        name = "fake"
        seed = None

        def answer(self, question, options):
            return (0, 1.5)

        def corpus_ppl(self, corpus):
            return 42.0

    # empty corpus + explicit text
    assert run_perplexity(FakeBackend(), None, [], ["some text"]) == 42.0
    # real ngram backend through the factory
    assert run_perplexity("ngram", None, CORPUS, None) == pytest.approx(520.7238, abs=1e-3)


def test_cli_perplexity_default_corpus(capsys):
    from pocket_eval.cli import main

    assert main(["perplexity"]) == 0
    out = capsys.readouterr().out
    assert "520.72" in out


def test_run_perplexity_hf_backend_returns_float(monkeypatch):
    """The huggingface backend's corpus_ppl is exercised through run_perplexity
    and returns a float — no network, no real model."""
    from pocket_eval import backends
    from pocket_eval.cli import run_perplexity

    monkeypatch.setattr(backends.HFModel, "_load", lambda self: None)
    monkeypatch.setattr(
        backends.HFModel,
        "corpus_perplexity",
        lambda self, corpus: (42.0, sum(len(c.split()) for c in corpus)),
    )

    result = run_perplexity("huggingface", None, CORPUS, None)
    assert isinstance(result, float)
    assert result == 42.0


def test_cli_perplexity_random_backend_error(capsys):
    from pocket_eval.cli import main

    assert main(["perplexity", "--backend", "random"]) == 1
    err = capsys.readouterr().err
    assert "random cannot compute perplexity" in err
