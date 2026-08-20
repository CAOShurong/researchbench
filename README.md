# ResearchBench

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
and a CLI for running evaluations.

## Installation

```bash
pip install researchbench
```

For LLM-as-judge scoring:

```bash
pip install researchbench[judge]
```

## Quick Start

```python
from researchbench import Benchmark

bench = Benchmark()
results = bench.run(tasks=["paper_comprehension", "idea_generation"])
print(results.summary())
```

CLI:

```bash
researchbench run --tasks paper_comprehension,idea_generation --model gpt-4o
```

## Task Categories

| # | Task | Input | Output | Scoring |
|---|------|-------|--------|---------|
| 1 | Paper Comprehension | arXiv paper | Deep understanding answers | Exact + rubric |
| 2 | Idea Generation | Research context | Novel hypothesis | LLM-judge (novelty/feasibility) |
| 3 | Literature Synthesis | N papers | Structured review | LLM-judge (coverage/coherence) |
| 4 | Experimental Design | Hypothesis | Experiment plan | Rubric (controls/stats) |
| 5 | Peer Review | Mock submission | Review text | LLM-judge (accuracy/constructiveness) |
| 6 | Reproduction | Paper + code repo | Reproduction report | Code execution |
| 7 | Open Question ID | Papers | Open question | LLM-judge (significance/feasibility) |

## License

MIT for code. Data follows source licenses (arXiv, OpenReview, etc.).

## Background Research

See `RESEARCH.md` in the [research repository](https://github.com/CAOShurong/researchbench)
for the full landscape analysis of existing benchmarks and the confirmed gap.
