# ResearchBench

![CI](https://github.com/CAOShurong/researchbench/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-277%20passed-brightgreen)
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

The current prototype provides:

- 7 keyword-matching placeholder task categories (not scientifically valid scores)
- An 8th task, `heterogeneous_pilot`: BEOL / heterogeneous-integration items with
  rubric scoring. Five items are marked reviewed; later items may be `draft`
  (skipped unless `--allow-draft`)
- A CLI (`researchbench` / `python -m researchbench`)
- Mock mode (no API key required) for offline testing and deterministic CI
- Report formats: text, JSON, HTML
- **277 passing unit tests** and multi-OS CI

**What it does NOT yet have:**

- Expert-validated datasets or gold answers (q6 is a 2026-paper draft)
- Evidence-based scoring on the original seven tasks (keyword matching is a placeholder)
- A public name that does not collide with Liu et al. ResearchBench (ACL 2026 Findings)
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
researchbench run --tasks paper_comprehension,idea_generation --model gpt-4o --allow-draft
researchbench run --tasks heterogeneous_pilot --model gpt-4o
researchbench run --tasks all --model gpt-4o --allow-draft --format json --save report.json
researchbench compare --model gpt-4o --model claude-3-opus --tasks all --allow-draft
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