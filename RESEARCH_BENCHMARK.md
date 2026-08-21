# RESEARCH_BENCHMARK.md

> **MANDATORY READING. Before doing any benchmark work, read this document.
> It defines the project's objective, validity requirements, evaluation
> protocol, and non-negotiable design principles. Do not redesign the benchmark
> without reconciling changes with this document.**

---

## 1. Benchmark purpose

This benchmark measures **how good an AI is at the actual intellectual work a
researcher needs** — not generic agent performance, not long-context retrieval,
not coding ability in isolation.

The central question it must answer:

> **"Which AI system is genuinely the better research assistant, in what
> research abilities, under what conditions, and how do we know?"**

Long-context, agentic, browsing, and tool-use capabilities are supporting
capabilities, not the benchmark's main identity. They are included only when
they are necessary for a research task.

---

## 2. Design philosophy: why should anyone trust the score?

The most important design problem is:

> **Why should anyone trust the benchmark score?**

For every dataset item, task, and evaluation method, the following must be
explicitly justified before implementation:

1. **What research ability does it measure?** — Name the specific capability
   from the taxonomy (Section 3).
2. **Why is the task representative of real research work?** — Cite the
   real-world research workflow it mirrors.
3. **What is the ground truth or reference evidence?** — Expert-written gold
   answer, later-published paper, known author-confirmed limitation, etc.
4. **How do we distinguish a genuinely correct answer from a plausible-sounding
   one?** — This is the hardest problem. Keyword matching does NOT solve it.
5. **How do we evaluate citations and evidence?** — Verify that cited sources
   exist, are relevant, and actually support the claim.
6. **Can multiple reasonable answers exist?** — If yes, define the acceptable
   answer space and how partial credit is assigned.
7. **How do we detect hallucinations, unsupported claims, missed
   counter-evidence, or incorrect causal conclusions?** — Negative cases,
   adversarial checks, and evidence-tracing rubrics.
8. **Could the task have leaked into model training data?** — Use recent or
   hidden papers; rotate items; flag contamination risk per item.
9. **Is the benchmark testing memorization, retrieval, reasoning, synthesis,
   or all of them?** — State which combination and why.
10. **What existing benchmarks already test something similar, and why is our
    design better or meaningfully different?** — Cite the competitor and the
    specific improvement (stronger ground truth, better evidence tracing,
    harder negatives, temporal robustness, expert rubrics, reproducibility).

**Do not claim our dataset is "better" merely because it is more complicated.**
Superiority must come from: stronger ground truth, better evidence tracing,
realistic research workflows, harder negative cases, temporal robustness,
expert-designed rubrics, reproducibility, and better separation of different
research abilities.

---

## 3. Capability taxonomy

The benchmark must measure these capabilities **independently**. Do not collapse
everything into a single subjective score too early. Per-capability scores are
required; an aggregate is optional and only if defensible.

| # | Capability | What it means | How to test it |
|---|---|---|---|
| C1 | **Factual correctness** | Are the stated facts about papers, methods, or results accurate? | Verify against the source paper or a trusted secondary source. |
| C2 | **Citation correctness** | Do cited papers exist? Are they cited accurately? | Verify against a paper database (Semantic Scholar / arXiv API). |
| C3 | **Evidence completeness** | Did the model find the key relevant evidence, or miss important papers/results? | Compare against an expert-curated evidence set. |
| C4 | **Source quality** | Are the cited sources authoritative and appropriate? | Rate source venue, recency, relevance. |
| C5 | **Paper comprehension** | Does the model correctly identify the core claim, methodology, limitations? | Expert-graded rubric with specific sub-questions. |
| C6 | **Cross-paper synthesis** | Can the model identify trends, contradictions, and gaps across multiple papers? | Multi-paper tasks with expert gold synthesis. |
| C7 | **Temporal / literature comparison** | Can the model track how a research problem evolved over time? | Historical snapshots with later-known-answer validation. |
| C8 | **Research-gap identification** | Can the model identify a real, unsolved gap? | Validate against later papers that addressed (or failed to address) the gap. |
| C9 | **Causal reasoning** | Does the model correctly distinguish correlation from causation? | Tasks with confounded and unconfounded evidence. |
| C10 | **Uncertainty calibration** | Does the model appropriately hedge or express uncertainty? | Compare confidence statements to actual correctness. |
| C11 | **Detection of alternative explanations** | Does the model identify competing hypotheses? | Tasks with multiple plausible interpretations. |
| C12 | **Technical explanation quality** | Can the model explain a difficult concept clearly and accurately? | Expert-graded explanation rubric. |
| C13 | **Novelty of proposed ideas** | Is a generated hypothesis genuinely new? | Check against literature; expert novelty rating. |
| C14 | **Scientific usefulness / actionability** | Is the proposed idea testable and useful? | Expert feasibility + testability rubric. |
| C15 | **Experimental testability** | Can the model design an experiment that would actually test the hypothesis? | Expert-graded experimental-design rubric. |
| C16 | **Robustness against misleading or conflicting literature** | Can the model handle contradictory evidence without overclaiming? | Tasks with deliberately conflicting sources. |

---

## 4. Dataset validity requirements

Do not simply collect random research questions. The dataset must be defensible.

### 4.1 Item types under investigation

| Type | Description | Ground truth source |
|---|---|---|
| Expert-written research questions | Questions authored by domain researchers with known answers. | Expert gold answer. |
| Paper-derived questions requiring external evidence | Questions based on a target paper but answerable only with evidence from other papers. | Expert-curated evidence set. |
| Multi-paper synthesis tasks | Given N papers, identify trends, contradictions, gaps. | Expert gold synthesis. |
| "What does this paper prove / not prove?" | Separate proven claims from suggested ones. | Author-confirmed or expert-validated. |
| Historical literature snapshots | Give papers up to year Y; ask how the problem evolved. | Later papers (year > Y) validate the answer. |
| Deliberately conflicting literature | Two papers with contradictory findings; model must reason about the conflict. | Expert analysis of why the conflict exists. |
| Research-gap identification with later validation | Ask "what is the most important open question?"; check against later papers. | Later literature. |
| Hypothesis generation with later validation | Generate a hypothesis; check if it was later addressed/published. | Later literature or expert evaluation. |
| Hidden / recent papers | Use papers published after a model's training cutoff to reduce contamination. | The paper itself (if the model cannot access it). |
| Hard negative evidence | Evidence that looks relevant but does not support the conclusion. | Expert-designed trap. |

### 4.2 Mandatory per-item metadata

Every dataset item must carry:

- `id`: unique, collision-resistant.
- `capability_tags`: which of C1–C16 it measures (at least one).
- `ground_truth`: the reference answer or evidence set.
- `ground_truth_source`: who produced it and how (expert name/role, later
  paper DOI, author confirmation, etc.).
- `scoring_method`: `exact_match`, `rubric`, `llm_judge`, `human_panel`,
  `later_paper_validation`, or a combination.
- `contamination_risk`: `low` (recent/hidden paper), `medium` (well-known but
  requires synthesis), `high` (classic paper, single-hop question).
- `hard_negatives`: any deliberately misleading or conflicting evidence
  included in the item.
- `expert_notes`: free-text notes from the item author for scorer reference.
- `version`: item schema version, for forward compatibility.

### 4.3 Automatic scoring vs expert rubrics

Where automatic scoring is unreliable (which is most research tasks), design
**structured expert rubrics** instead of pretending an LLM judge or a keyword
matcher is objective.

LLM-as-a-judge may be used, but:
- Its agreement with human/expert judgment must be **validated and reported**
  (Cohen's kappa or equivalent).
- The judge prompt, model, and settings must be **recorded** with every run.
- The judge must be **different from the model being evaluated**.
- LLM-judge scores must be **labeled as such**, never presented as ground truth.

---

## 5. Evaluation principles

1. **No keyword matching as the primary scoring method.** Keyword presence
   does not demonstrate comprehension, synthesis, or reasoning. The current
   v0.1.0 implementation uses keyword matching as a **placeholder** — it is
   explicitly not scientifically valid and must be replaced.

2. **Per-capability scores first.** Report C1–C16 independently. An aggregate
   is optional and must be weighted transparently.

3. **Adversarial design.** Every task should include hard negatives —
   plausible but wrong answers, misleading citations, or conflicting evidence.

4. **Evidence tracing.** For any claim a model makes, the evaluation should
   check whether the supporting evidence is real, relevant, and correctly
   interpreted.

5. **No silent repair.** Do not silently fix bad model outputs. Record
   failures, timeouts, and refusals as-is.

6. **Separate memorization from reasoning.** Use recent/hidden papers and
   multi-hop tasks to distinguish retrieval from genuine synthesis.

---

## 6. Subscription / API evaluation protocol

This benchmark must treat **subscription-based AI systems as first-class
targets.** Real usage is often ChatGPT / Claude / Codex subscriptions, not only
raw APIs. Do not design a benchmark that can only be run through an API.

### 6.1 Subscription / product mode

| Field | Description |
|---|---|
| `product` | Exact product name (e.g. "ChatGPT (GPT-4o)", "Claude (Sonnet 4)", "Codex CLI"). |
| `reasoning_mode` | Whether extended thinking/reasoning was on, off, or auto. |
| `browsing` | Whether web search was available and used. |
| `tool_access` | What tools were available (code execution, file access, browsing). |
| `context_supplied` | What context was provided (full paper text, abstract only, nothing). |
| `session_policy` | Fresh conversation vs. continuing; number of prior turns. |
| `prompt` | The exact prompt(s) used. |
| `max_interactions` | How many back-and-forth turns were allowed. |
| `time_limit` | Wall-clock or session duration limit. |
| `human_intervention` | Whether a human intervened, and if so, what they did. |
| `run_date` | Date of the run (ISO 8601). |
| `full_output` | Complete model output, including any reasoning/thinking traces. |
| `cited_sources` | All sources cited by the model, as URLs or paper identifiers. |
| `observable_metrics` | Any resource metrics the product exposes (do NOT invent token counts). |

### 6.2 API mode

| Field | Description |
|---|---|
| `provider` | openai, anthropic, google, etc. |
| `model_id` | Exact API model identifier. |
| `api_params` | temperature, max_tokens, top_p, system prompt, etc. |
| `context_supplied` | What context was provided. |
| `prompt` | The exact prompt(s) used. |
| `full_output` | Complete model output. |
| `cited_sources` | All sources cited. |
| `cost` | API cost if available. |
| `run_date` | Date of the run. |

### 6.3 Separation

A ChatGPT subscription run and a raw OpenAI API run are **not automatically
equivalent** even when the model name appears similar. They must be recorded
as separate experimental conditions and never silently mixed.

---

## 7. Reproducibility requirements

Every benchmark run must save enough information that another person can
understand exactly what happened.

### 7.1 Run record (mandatory)

Every run must produce a run record containing at minimum:

- `benchmark_version`: semantic version of the benchmark suite.
- `task_id`: which dataset item was evaluated.
- `model_or_product`: per Section 6.
- `model_mode_settings`: reasoning mode, browsing, tools, etc.
- `system_prompt`: the system prompt used (or "none").
- `task_prompt`: the task-specific prompt.
- `supplied_context`: what context was given (paper text, abstract, nothing).
- `tool_search_availability`: whether tools/search were available.
- `timestamp`: ISO 8601 timestamp of the run.
- `full_answer`: the complete model output.
- `cited_sources`: all sources cited by the model.
- `evaluation_result`: score(s) per capability.
- `evaluator_version`: which scorer/rubric/judge version was used.
- `failures_or_timeouts`: any errors or timeouts.
- `human_intervention`: description if any.

### 7.2 Raw output preservation

The raw model response must be saved for every run. The current v0.1.0 code has
a `TaskResult.raw_output` field that is **never populated** — this must be
fixed. Without raw outputs, post-hoc re-scoring, error analysis, and auditing
are impossible.

### 7.3 No silent repair

Do not silently fix, truncate, or paraphrase bad model outputs. If a model
hallucinated, produced an error, or timed out, the raw output and the failure
must be recorded as-is.

---

## 8. Comparison with existing benchmarks

Before finalizing any task design, research the strongest existing benchmarks
related to:

- Deep research / research agents
- Scientific/research QA
- Literature synthesis
- Paper understanding
- Browsing and evidence-based QA
- Long-context research
- Hypothesis generation / scientific discovery

For each benchmark, determine:

| Question | Must answer |
|---|---|
| What does it actually measure? | |
| What does it fail to measure? | |
| How is its ground truth constructed? | |
| How reliable is its evaluation? | |
| Can models game it? | |
| Is contamination likely? | |
| Does it resemble real researcher workflows? | |

Our benchmark should be built only after this comparison is complete. Do not
create novelty by renaming existing tasks.

### Known competitors (preliminary, requires deeper research)

| Benchmark | What it measures | Our differentiation (proposed) |
|---|---|---|
| PaperQA / PaperQA2 | AI paper QA system (not a benchmark) | We are a benchmark, not a system. |
| SciCode | Science code problems | We measure the full research pipeline, not just coding. |
| MLAgentBench | ML experiment agent | We measure academic research broadly, not just ML experimentation. |
| MMLU / GPQA | Knowledge (MCQ) | We measure process skills, not factual recall. |
| SWE-bench | GitHub issue fixing | We measure research reasoning, not software engineering. |
| (others to be researched) | | |

---

## 9. Self-challenge questions

For every major design decision, explicitly ask **before** deciding:

- What if this metric rewards verbosity instead of research quality?
- What if citation count is high but the citations do not support the claims?
- What if an answer is scientifically reasonable but differs from the reference?
- What if the "research gap" is only a gap because we failed to find the paper?
- What if the proposed idea already exists?
- What if an LLM judge prefers fluent writing rather than scientific correctness?
- What if the task is already in the model's training data?
- What if browsing quality dominates reasoning quality?
- What if subscription products have different hidden tools or compute budgets?
- What evidence would falsify our assumption that this benchmark is valid?

---

## 10. Current project status (as of 2026-08-21)

### What exists (v0.1.0)

- **7 task modules** with a `evaluate(model) -> (score, details)` interface.
- **10 CLI commands**: `list`, `show`, `run`, `compare`, `tasks`, `sample`,
  `data`, `report`, `schema`, `verify`.
- **162 tests** (88% coverage) — but the tests verify the **keyword-matching
  mechanics**, not scientific validity.
- **CI**: ruff + mypy + pytest with 80% coverage gate + wheel build smoke test.
- **Packaging**: clean (click-only runtime dep, py.typed, SPDX license).
- **Docs**: 8+ documentation files.
- **Wheel**: builds and installs cleanly in a fresh venv.

### What is fundamentally weak

1. **All 7 tasks use keyword substring matching as their sole scoring method.**
   This is a placeholder, not a scientifically valid evaluation. It cannot:
   - distinguish a correct answer from a plausible-sounding one;
   - detect hallucinations or unsupported claims;
   - evaluate citation correctness or evidence completeness;
   - measure anything beyond keyword density.

2. **No ground truth beyond keyword lists.** The `reference_keywords` and
   `key_causes` are answer keys for keyword matching, not research-grade
   ground truth.

3. **No reproducibility metadata.** Run records contain only the model name.
   No timestamp, no model settings, no raw outputs, no cited sources.

4. **No subscription-model protocol.** Only API calls are supported.

5. **No contamination prevention.** All papers are well-known classics likely
   in training data.

6. **No expert rubrics or human validation.** The scoring is fully automatic
   and unvalidated.

7. **No capability taxonomy.** The 7 tasks collapse into a single score per
   task, with no mapping to the 16 capabilities in Section 3.

8. **RESEARCH.md's own prescription was not followed.** The background
   research explicitly diagnosed that "research capability resists simple
   metrics" and prescribed LLM-as-judge + human validation + real data. The
   code chose the opposite.

### What should be retained

- CLI infrastructure (commands, options, report formats).
- Packaging / build / CI infrastructure.
- Test infrastructure (the test framework, not the keyword-matching assertions).
- Documentation structure.
- Project memory files (HANDOFF.md, DECISIONS.md, etc.).
- The mock-mode concept (clearly labeled).

### What needs to be redesigned

1. **Scoring methodology**: replace keyword matching with evidence-based
   evaluation (expert rubrics, LLM-judge-validated, later-paper validation).
2. **Dataset design**: real ground truth, per-item metadata, contamination
   risk assessment, hard negatives.
3. **Task definitions**: align with the C1–C16 capability taxonomy.
4. **Evaluation protocol**: support subscription models, record full run
   metadata, preserve raw outputs.
5. **Report format**: capture run records per Section 7.1.

---

## 11. Next steps (in priority order)

1. **Research existing benchmarks** (Section 8): complete the comparison table
   with real findings for PaperQA2, SciCode, MLAgentBench, and others.
2. **Design the dataset schema** (Section 4.2): define the per-item metadata
   structure and implement a validation layer.
3. **Design the run-record format** (Section 7.1): implement run-record
   capture in `BenchmarkResult` and `TaskResult`.
4. **Design expert rubrics** for at least 2 tasks (paper comprehension + peer
   review) as a pilot.
5. **Implement subscription-mode protocol** (Section 6.1): a structured
   protocol file for recording ChatGPT/Claude/Codex runs.
6. **Pilot a contamination-resistant item** using a recent/hidden paper.
7. **Validate LLM-as-judge** against human ratings on the pilot items.
8. **Only then** replace the keyword-matching scorers with the new evaluation
   methods, task by task.

---

## 12. Unresolved questions

- How many expert reviewers are needed per item for a defensible gold standard?
- How do we handle items where the "correct" answer changes over time (later
  papers overturn earlier conclusions)?
- How do we evaluate a subscription product that does not expose its internal
  reasoning or token counts?
- How do we prevent the benchmark itself from leaking into model training data
  once published?
- What is the minimum dataset size per capability for a statistically
  meaningful score?
- Should the benchmark support interactive (multi-turn) evaluation, or only
  single-shot?
- How do we weight the 16 capabilities into an aggregate without obscuring
  weaknesses?

These questions must be answered before claiming the benchmark is valid.