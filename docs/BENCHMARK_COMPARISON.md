# Existing-benchmark comparison (RESEARCH_BENCHMARK.md §8)

This document answers the §8.3 questions for each named competitor.
It does **not** claim this prototype is a validated benchmark, and it
does **not** claim that no overlapping work exists.

Differentiation, if this project continues, must come from:

- domain-grounded EE / BEOL / heterogeneous-integration items;
- executable or rubric-checked answers rather than report-quality judges;
- subscription vs API as separate experimental conditions;
- inspectable run records and raw outputs.

It must **not** come from a novelty slogan.

## Naming collision

A 2025–2026 ACL Findings paper already uses the name **ResearchBench**:

- Liu et al., *ResearchBench: Benchmarking LLMs in Scientific Discovery
  via Inspiration-Based Task Decomposition*, arXiv:2503.21248, ACL 2026
  Findings ([anthology](https://aclanthology.org/2026.findings-acl.644/)).
- Dataset: [ankilok/ResearchBench](https://huggingface.co/datasets/ankilok/ResearchBench).
- Code: `ankitala/ResearchBench`.
- Scope: inspiration retrieval, hypothesis composition, hypothesis ranking
  on 1,386 papers (2024+) across 12 disciplines.

This repository's public name collides with that paper. Rename candidates
are in `docs/NAME_CANDIDATES.md`. The rename is a user decision.

## Competitor table

| Benchmark | Measures | Ground truth | Evaluation | Gaps relative to this project's *intent* |
|---|---|---|---|---|
| **ResearchBench (Liu 2025/26)** | Inspiration retrieval, hypothesis composition, ranking | Components extracted from 2024+ papers; expert-checked extraction | Automated LLM pipeline; ranking/retrieval metrics | Broad discovery, not EE device physics. Does not record subscription vs API. Does not score BEOL constraints or hard negatives in process integration. |
| **ResearcherBench (Xu 2025, COLM 2026)** | Deep AI research systems on 65 frontier AI questions | Expert-curated questions; dual rubric + citation checks | Rubric insight quality + factual/citation scores | AI-research questions, not semiconductor process/device reasoning. Product-level DARS evaluation. |
| **DeepResearch Bench (Du 2025, arXiv:2506.11763)** | Deep-research *agents* writing citation-rich reports (100 PhD-level tasks, 22 fields) | Expert-written tasks; RACE report quality + FACT citations | LLM-as-judge aligned to humans | Report-writing agents, not closed scientific items with physical constraints. |
| **Deep Research Bench (FutureSearch, arXiv:2506.06287)** | Web-research agents on 89 frozen-web tasks | Human-worked answers; RetroSearch snapshot | Automated trace eval + live/offline comparison | Web search quality, not lab/device reasoning. |
| **RPC-Bench (Chen et al., arXiv:2601.14289)** | Paper comprehension QA from CS review–rebuttal (15k QA) | Human-verified QA from peer-review dialogue | Correctness / completeness / conciseness | CS paper QA, not EE process questions. No run-record protocol for products. |
| **PaperQA2** | A paper-QA *system*, not a benchmark | Literature corpora | Task-specific QA metrics | Wrong category: we evaluate models, we are not a retrieval product. |
| **SciCode** | Scientific coding problems | Unit tests | Execution | Coding, not research-assistant reasoning over devices/papers. |
| **MLAgentBench** | ML experiment agents | Experiment outcomes | Agent success | ML engineering loop, not EE scientific reasoning. |
| **MMLU / GPQA** | Knowledge MCQ | Answer keys | Accuracy | Recall, not process skill or evidence tracing. |
| **SWE-bench** | GitHub issue fixing | Tests in repos | Fail-to-pass | Software engineering, not research. |

## §8.3 answers (compressed)

### What existing suites actually measure

Most current “research” benchmarks measure one of: (1) hypothesis-shaped
text over papers, (2) long web-research reports, or (3) paper QA. None
of them ask whether a model can state a BEOL thermal ceiling, name the
right ferroelectric phase of HZO, or reject an unphysical IGZO p-type
claim.

### What they fail to measure (and we intend to)

- Domain constraints that a fluent wrong answer will violate.
- Hard negatives designed by someone who works in the field.
- Subscription-product vs API as distinct conditions.
- Per-item provenance, contamination flags, and re-gradable raw output.

### How ground truth is usually built

Competitors use LLM extraction from papers, expert-written open questions,
or review–rebuttal mining. Our *pilot* uses expert-curated items with
explicit provenance and rubric criteria. That is still a small,
unvalidated sample — not a published gold set.

### How reliable is evaluation

Report-quality and LLM-as-judge scores can reward fluency. Keyword
matching (our seven legacy tasks) is worse. The heterogeneous pilot uses
pattern-backed rubrics plus hard-negative penalties; that is still not
human agreement, and it can be gamed by parroting rubric phrases.

### Can models game it?

Yes, any regex rubric can be gamed. Human calibration is required before
claiming validity (`HANDOFF.md`).

### Contamination

Liu ResearchBench uses 2024+ papers. Five reviewed pilot items are standard
BEOL facts likely present in training data; `contamination_risk=low` on
those items is optimistic. A sixth *draft* item is grounded in Cheng et al.,
arXiv:2603.23341 (24 Mar 2026) and is not expert-reviewed.

### Real researcher workflow

Deep-research benches match “write me a report.” This project’s intended
workflow is “help with a specific scientific question under physical
constraints, and show the evidence.” The pilot is closer to the second
workflow, but it is five reviewed items plus one unreviewed draft.

## What we will not claim

- That this repository is the first research-capability benchmark.
- That the current scores measure model quality.
- That keyword-matching tasks are scientifically valid.
- That the name ResearchBench is available.
