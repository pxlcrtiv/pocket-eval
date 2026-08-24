# Changelog

All notable changes to pocket-eval are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] — 2026-08-24

### Added
- Initial release: `pocket-eval` CLI with three scoring backends —
  deterministic bundled n-gram baseline (stdlib-only, trains on the
  15-doc DeFi/on-chain/ML corpus), seeded random chance baseline, and an
  optional Hugging Face backend for tiny CPU-friendly causal models
  (keyless public downloads, `sshleifer/tiny-gpt2` works out of the box).
- `demo` (full bundled evaluation: corpus perplexity + 12-item QA),
  `perplexity` (text or whole corpus), `qa` (multiple-choice scoring with
  table/markdown/JSON output), `corpus` (deterministic stats).
- 12-item original mini-benchmark (`data/bench/qa_mini.json`) and 15-doc
  original corpus (`data/corpus/*.md`), both leakage-free and self-written.
- 23-offline-test suite with golden numbers; Daily Green automation
  (24-eval-tip pool); CI + daily workflows.