# ResearchBench

![CI](https://github.com/CAOShurong/researchbench/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A comprehensive benchmark for evaluating AI academic and research capabilities.

## Why?

There are many AI benchmarks (MMLU, HumanEval, SWE-bench, GPQA, HELM, AGIEval), but
**none comprehensively measure AI academic and research capabilities**:

- Can an AI deeply **understand a research paper** (not just answer factual QA,
  but critique methodology, identify limitations, summarize contributions)?
- Can it **generate novel research hypotheses** from a gap analysis?
- Can it **synthesize multiple papers** into a coherent literature review?
- Can it **design a valid experiment** with controls, sample size, and analysis plan?
- Can it provide **constructive peer review** identifying methodological flaws?
- Can it **reproduce results** from a paper's code and debug failures?
- Can it identify the most important **open questions** from a body of work?

ResearchBench fills this gap with 7 task categories, a structured scoring framework,
and a CLI for running evaluations. The gap analysis is recorded in
[`docs/RESEARCH.md`](docs/RESEARCH.md); exact scoring rules for every task are in
[`docs/TASK_DEFINITIONS.md`](docs/TASK_DEFINITIONS.md).

## Installation

```bash
pip install researchbench

# To call real models (openai/anthropic clients):
pip install researchbench[judge]
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
> smoke testing only — they are not real model evaluations. See
> [`docs/USAGE.md`](docs/USAGE.md#evaluating-real-models).

## Task Categories

| # | Task | Input | Output | Scoring |
|---|------|-------|--------|---------|
| 1 | Paper Comprehension | arXiv papers | Deep understanding answers | Reference-keyword rubric |
| 2 | Idea Generation | Research context | Novel hypothesis | Novelty + feasibility keywords |
| 3 | Literature Synthesis | N papers | Structured review | Keyword coverage + length |
| 4 | Experimental Design | Hypothesis | Experiment plan | Coverage + structure completeness |
| 5 | Peer Review | Mock submission | Review text | Flaw detection + keywords + recommendation |
| 6 | Reproduction | Paper + code repo | Reproduction report | Cause detection + keywords + diagnosis |
| 7 | Open Question ID | Papers | Open question | Coverage + importance/progress/future |

Precise formulas, weights, caps and baseline floors for each task are
documented in [`docs/TASK_DEFINITIONS.md`](docs/TASK_DEFINITIONS.md).

## Documentation

- [`docs/RESEARCH.md`](docs/RESEARCH.md) — background research and the confirmed gap
  (why no existing benchmark covers academic/research capabilities).
- [`docs/USAGE.md`](docs/USAGE.md) — CLI and Python API reference, report formats,
  evaluating real models, troubleshooting.
- [`docs/TASK_DEFINITIONS.md`](docs/TASK_DEFINITIONS.md) — normative task definitions
  and scoring rules.
- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — how to develop, test and extend.
- [`examples/`](examples/) — runnable CLI and Python API demos (mock-mode safe).
- [`CHANGELOG.md`](CHANGELOG.md) — version history.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — proposed direction (non-binding).
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) / [`SECURITY.md`](SECURITY.md) —
  community norms and vulnerability reporting.

## Development

```bash
pip install -e ".[dev]"
ruff check src tests && ruff format --check src tests
pytest tests -v
```

## License

MIT for code. Data follows source licenses (arXiv, OpenReview, etc.).