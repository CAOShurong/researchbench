# ResearchBench

![CI](https://github.com/CAOShurong/researchbench/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-270%20passed-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![Provenance](https://img.shields.io/badge/provenance-W3C%20JSON--LD-purple)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

> **Status: Active research evaluation framework (v0.4.0).**
>
> This project provides a **rigorous evaluation harness for frontier AI scientific reasoning**,
> featuring calibrated domain rubrics, hard-negative reasoning traps, and blinded human expert
> calibration across heterogeneous integration, peer review, and reproduction diagnosis.
> See [`RESEARCH_BENCHMARK.md`](RESEARCH_BENCHMARK.md) for the design document and roadmap.

## What this is

A framework for evaluating **AI as a research assistant** — paper
comprehension, idea generation, literature synthesis, experimental design,
peer review, reproduction diagnosis, and open question identification.

The central question it aims to answer:

> *"Which AI system is genuinely the better research assistant, in what
> research abilities, under what conditions, and how do we know?"*

The current v0.4.0 implementation provides:

- 7 core scientific task categories with standardized evaluation interfaces
- Heterogeneous integration & BEOL device physics pilot with blinded human expert calibration
- Immutable experiment provenance using W3C JSON-LD and `.eln` exchange bundles
- A CLI (`researchbench` / `python -m researchbench`) with 10 commands
- Mock mode (no API key required) for offline testing and deterministic CI
- Report formats: text, JSON, HTML, and JSON-LD
- **270 passing unit tests**, complete type hints (`mypy --strict`), and automated multi-OS CI

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