# ResearchBench

![CI](https://github.com/CAOShurong/researchbench/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

> **Status: early-stage prototype, not a validated benchmark.**
>
> This project is a **research-capability evaluation framework prototype**. It
> does not yet have expert-validated datasets, gold answers, model evaluation
> results, or a leaderboard. The current scoring uses keyword matching as a
> **placeholder** — it is not scientifically valid and must not be presented as
> real model performance. See [`RESEARCH_BENCHMARK.md`](RESEARCH_BENCHMARK.md)
> for the design document and roadmap.
>
> **Naming note:** A 2025 paper and code repository named "ResearchBench"
> already exists (evaluating scientific discovery, idea retrieval, and
> hypothesis generation). Other related benchmarks include ResearcherBench,
> DeepResearch Bench, and RPC-Bench. This project's name may change to avoid
> confusion. See [`RESEARCH_BENCHMARK.md`](RESEARCH_BENCHMARK.md) Section 8.

## What this is

A framework for evaluating **AI as a research assistant** — paper
comprehension, idea generation, literature synthesis, experimental design,
peer review, reproduction diagnosis, and open question identification.

The central question it aims to answer:

> *"Which AI system is genuinely the better research assistant, in what
> research abilities, under what conditions, and how do we know?"*

The current v0.1.0 implementation provides:

- 7 task categories with a `evaluate(model) -> (score, details)` interface
- A CLI (`researchbench` / `python -m researchbench`) with 10 commands
- Mock mode (no API key required) for pipeline smoke testing
- Report formats: text, JSON, HTML
- 162 tests, CI, wheel builds

**What it does NOT yet have:**

- Expert-validated datasets or gold answers
- Evidence-based scoring (the current keyword matching is a placeholder)
- Subscription-model evaluation protocol (ChatGPT/Claude/Codex)
- Reproducibility metadata (timestamps, model settings, raw outputs)
- Contamination prevention (all papers are well-known classics)
- Any published model evaluation results or leaderboard

## Installation

```bash
pip install -e .

# To call real models (openai/anthropic clients):
pip install -e ".[judge]"
```

## Quick Start

```python
from researchbench import Benchmark

bench = Benchmark(tasks=["paper_comprehension", "idea_generation"])
result = bench.run(model="gpt-4o")
print(result.summary())
```

CLI:

```bash
researchbench run --tasks paper_comprehension,idea_generation --model gpt-4o
researchbench run --tasks all --model gpt-4o --format json --save report.json
researchbench compare --model gpt-4o --model claude-3-opus --tasks all
```

> Without an API key, tasks run in **mock mode** and return canned scores for
> smoke testing only — they are not real model evaluations.

## Documentation

- [`RESEARCH_BENCHMARK.md`](RESEARCH_BENCHMARK.md) — **authoritative design
  document**: purpose, philosophy, capability taxonomy, validity requirements,
  evaluation protocol, reproducibility, comparison with existing benchmarks.
- [`docs/RESEARCH.md`](docs/RESEARCH.md) — background research and gap analysis.
- [`docs/USAGE.md`](docs/USAGE.md) — CLI and Python API reference.
- [`docs/TASK_DEFINITIONS.md`](docs/TASK_DEFINITIONS.md) — task scoring formulas
  (note: these are placeholder mechanics, not validated evaluation).
- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — how to develop, test and extend.
- [`docs/FAQ.md`](docs/FAQ.md) — frequently asked questions.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — proposed direction.
- [`examples/`](examples/) — runnable demos (mock-mode safe).
- [`CHANGELOG.md`](CHANGELOG.md) — version history.

## Development

```bash
pip install -e ".[dev]"
ruff check src tests && ruff format --check src tests
mypy src
pytest tests -v
```

## License

MIT for code. Data follows source licenses (arXiv, OpenReview, etc.).