# Background Research: AI Academic/Research Capability Benchmark

> Reproduced from `E:\Codex\Outputs\ai-academic-benchmark\RESEARCH.md`
> (2026-08-20). This research was the required prerequisite for building the
> benchmark (project decision `D-20260820-030000-c018`).

## Date: 2026-08-20
## Status: COMPLETE (prerequisite for code)

## 1. Existing AI Benchmarks — Full Landscape

| Benchmark | Stars | What it measures | Academic/research? | Gap |
|-----------|-------|-----------------|-------------------|-----|
| MMLU | ~26k | 57-subject multiple-choice knowledge (undergrad) | Partial (knowledge) | No research skills |
| HumanEval | ~9k | 164 coding problems (pass@k) | No | Not academic |
| SWE-bench | ~16k | 2294 real GitHub issue fixes | No | Software engineering |
| BIG-bench | ~3k | 200+ diverse tasks | Partial | Not research-focused |
| HELM | Framework | Holistic LLM eval across many metrics | Partial | General, not academic |
| GPQA | 530 | Graduate-level Google-proof Q&A (bio/phys/chem) | Partial (domain knowledge) | Only MCQ, no research process |
| AGIEval | 777 | Admission exams (Gaokao, SAT, LSAT) | Partial (exam skills) | Not research capability |
| SciCode | ~200 | Science code problems | Partial (coding in science) | Not full research pipeline |
| SciQ | ~600 | Science MCQ (elementary) | No | Too basic |

## 2. Capabilities NOT Covered by Any Existing Benchmark

> **Update 2026-08-21:** This section's original claim ("No existing benchmark
> tests this") is **no longer accurate**. Multiple benchmarks now cover
> overlapping territory, including a 2025 "ResearchBench" paper (scientific
> discovery, idea retrieval), ResearcherBench (open research questions),
> DeepResearch Bench (research reports), and RPC-Bench (ACL 2026, paper
> understanding). The gaps below remain partially uncovered, but we must not
> claim to be the first or only benchmark in this space. See
> `RESEARCH_BENCHMARK.md` Section 8 for the updated comparison.

### CONFIRMED GAPS (no benchmark exists):

1. **Paper reading comprehension** — Can AI deeply understand a research paper:
   - Identify the core claim and contribution?
   - Critique the methodology and experimental design?
   - Identify limitations and threats to validity?
   - Summarize for different audiences (peer, student, funder)?
   - *No existing benchmark tests this beyond simple QA.*

2. **Novel idea generation** — Can AI generate genuinely novel research hypotheses:
   - Propose a new research question from a gap analysis?
   - Design a feasible experiment to test it?
   - *No existing benchmark evaluates creative research thinking.*

3. **Literature synthesis** — Can AI synthesize multiple papers:
   - Identify trends, contradictions, and gaps across papers?
   - Write a coherent literature review?
   - *No benchmark tests this open-ended capability.*

4. **Experimental design** — Can AI design a valid experiment:
   - Choose appropriate controls and sample sizes?
   - Identify confounders?
   - Select appropriate statistical methods?
   - *No benchmark exists for this.*

5. **Peer review** — Can AI provide constructive, technically sound peer review:
   - Identify methodological flaws in a submission?
   - Suggest specific improvements?
   - Distinguish strong from weak claims?
   - *No benchmark exists.*

6. **Research code reproduction** — Can AI reproduce results from a paper:
   - Run the author's code and verify key claims?
   - Debug reproduction failures?
   - *SWE-bench tests bug fixing, not scientific reproduction.*

7. **Research question formulation** — Can AI identify important open questions:
   - From a set of papers, identify the most promising next step?
   - *No benchmark tests this.*

## 3. Why This Gap Exists

- Academic research skills are **open-ended** and hard to score automatically
- Most benchmarks focus on **closed-form answers** (MCQ, code pass/fail)
- Research capability requires **judgment, creativity, and domain expertise** that resist simple metrics
- Data is hard to source (need real papers, real reviews, real experiments)

## 4. Proposed Benchmark Design

### Name: `ResearchBench`

### Dimensions (7 task categories):
1. **Paper Comprehension** — Given a real arXiv paper, answer deep understanding questions (not factual QA but methodology critique, limitation identification, contribution summarization)
2. **Idea Generation** — Given a research context, generate a novel hypothesis; scored by human raters or LLM-as-judge with novelty/feasibility rubric
3. **Literature Synthesis** — Given N papers, produce a structured review identifying gaps
4. **Experimental Design** — Given a hypothesis, design an experiment with controls, sample size, and analysis plan
5. **Peer Review** — Given a mock submission, write a review identifying strengths/weaknesses
6. **Reproduction** — Given a paper + code repo, identify why reproduction fails
7. **Open Question Identification** — Given papers, identify the most important open question

### Scoring:
- Closed tasks (comprehension, reproduction): exact match / code execution
- Open tasks (idea, synthesis, design, review): LLM-as-judge with structured rubric + human validation subset
- All tasks have a human-validated gold standard

### Data sources:
- arXiv papers (CC-BY or arXiv license)
- Open access review data (OpenReview)
- Existing reproduction studies (PapersWithCode)
- Synthetic but expert-validated scenarios

### License: MIT for code; data follows source licenses

## 5. Competitive Analysis

No direct competitor exists. Closest:
- **PaperQA** (Future-House): AI paper QA system, not a benchmark
- **SciCode**: science coding, not full research pipeline
- **MLAgentBench**: ML experiment agent, not academic research broadly

## 6. Conclusion

The gap is real and significant. A comprehensive AI academic/research capability benchmark would be genuinely novel and useful for AI researchers, educators, and evaluators. The main challenge is scoring open-ended tasks, which can be addressed with LLM-as-judge + human validation.

## 7. Next Step

Build `ResearchBench` as a substantial Python package with:
- Task definitions and data loaders
- Scoring framework (exact + LLM-judge)
- CLI for running evaluations
- Comprehensive tests
- CI/CD
- Documentation and examples

> Implementation status: this repository now implements the 7 task categories
> with deterministic reference-keyword scoring (see `docs/TASK_DEFINITIONS.md`),
> a CLI (`run`/`list`/`show`/`compare`), report formats (text/json/html),
> 127 tests and GitHub Actions CI.