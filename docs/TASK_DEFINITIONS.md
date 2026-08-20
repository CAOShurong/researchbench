# Task Definitions & Scoring

This document specifies exactly what each of the 7 ResearchBench task categories
measures, what data it uses, and the precise scoring formula implemented in
`src/researchbench/tasks/`. The formulas below are normative: unit tests in
`tests/` assert their behavior (perfect responses score 100.0, see
[Testing](CONTRIBUTING.md#testing)).

## Common conventions

- **Scores** are always a float in `[0, 100]`.
- **Keyword matching** is case-insensitive substring matching: a model response
  containing `"Transformer"` counts as matching the reference keyword
  `"transformer"` and also any other reference phrase that is a substring.
- **Mock mode**: when no `OPENAI_API_KEY` (for models starting with `gpt`/`openai`)
  or `ANTHROPIC_API_KEY` (for models containing `claude`) is set, the task's
  `_call_model` returns a canned answer. Scores produced in mock mode are only
  useful for smoke testing the pipeline; **they are not model evaluations**.
- Each task returns `(score, details)` from `evaluate(model=...)` where `details`
  is a dict that `--verbose` and `--format json` reports expose.

---

## 1. Paper Comprehension `paper_comprehension`

**What it measures.** Deep understanding of a research paper: the core
contribution, known limitations, and supporting experimental evidence — as
opposed to surface factual recall.

**Data.** `PAPERS` in `src/researchbench/tasks/paper_comprehension.py`: two
classic papers (Attention Is All You Need; Deep Residual Learning for Image
Recognition), each with an abstract and 3 methodology-focused questions.

**Scoring.** For each question `q` with reference keywords `mn`:

1. `match_count` = number of `q["reference_keywords"]` found in the response.
2. `correctness = min(match_count / len(mn) * 1.5, 1.0)` — the 1.5× coefficient
   lets a near-perfect answer reach 1.0, but never exceed it.
3. Aggregate `score = sum(correctness) / n_questions * 100`.

`details`: `{"per_paper": {paper_id: {"score", "max"}}, "total_questions"}`.

**Perfect answer:** one that contains every reference keyword for every question
→ 100.0. An empty answer → 0.0.

---

## 2. Idea Generation `idea_generation`

**What it measures.** Generating novel, coherent research hypotheses from a gap
analysis, including a concrete way to test them.

**Data.** `CONTEXTS`: two research contexts (few-shot learning mechanism in LLMs;
RLHF alignment limitations).

**Scoring.** For each context, from the response `raw`:

1. `novelty` = count of hits against `NOVELTY_KEYWORDS`
   (`novel, hypothesis, propose, framework, approach, method, mechanism, theory, insight`).
2. `feasibility` = count of hits against `FEASIBILITY_KEYWORDS`
   (`experiment, evaluate, test, measure, dataset, baseline, control, metric, ablation`).
3. `length_score = min(len(raw) / 500, 1.0)`.
4. `generic_penalty` starts at 1.0; reduce by 0.15 for each of
   `"further research is needed"`, `"it depends"`, `"more studies"`; floor 0.3.
5. `score = (min(novelty,5)/5*0.4 + min(feasibility,5)/5*0.3 + length_score*0.3) * generic_penalty * 100`.

Final score is the mean over contexts. `details`: `{"per_context": {id:
{"score", "length", "novelty_terms", "feasibility_terms"}}, "average"}`.

**Perfect answer:** contains all novelty + feasibility keywords, is ≥ 500 chars,
and avoids the generic phrases → 100.0. Empty → 0.0.

---

## 3. Literature Synthesis `literature_synthesis`

**What it measures.** Synthesizing multiple papers into a coherent review: the
key trend, tensions between findings, and remaining open questions.

**Data.** `SYNTHESIS_SETS`: two sets of 3 papers (chain-of-thought prompting;
scaling laws), each with per-set keywords.

**Scoring.** For each set:

1. `kw_count` = hits against the set's `keywords`.
2. `coverage = min(kw_count / len(keywords) * 2, 1.0)`.
3. `length_score = min(len(raw) / 400, 1.0)`.
4. `score = (coverage * 0.6 + length_score * 0.4) * 100`.

Final score is the mean over sets. `details`: `{"per_set": {id: {"score",
"keyword_coverage", "length"}}, "average"}`.

**Perfect answer:** contains all keywords and is ≥ 400 chars → 100.0.

---

## 4. Experimental Design `experimental_design`

**What it measures.** Designing a rigorous, valid experiment: controls, sample
size/power, variables, confounders, and a statistical analysis plan.

**Data.** `HYPOTHESES`: two hypotheses (drug efficacy; adaptive-sparsity
attention for long-document summarization), each with per-hypothesis keywords.

**Scoring.** For each hypothesis:

1. `coverage = min(kw_count / len(keywords) * 2, 1.0)`.
2. `length_score = min(len(raw) / 600, 1.0)`.
3. `sections` = how many of `["control", "sample", "statistical", "confound",
   "interpret"]` occur in the response; `completeness = sections / 5`.
4. `score = (coverage * 0.35 + length_score * 0.25 + completeness * 0.4) * 100`.

Final score is the mean over hypotheses. `details`: `{"per_hypothesis": {id:
{"score", "keyword_coverage", "sections", "length"}}, "average"}`.

**Perfect answer:** all keywords + all five section terms + ≥ 600 chars → 100.0.
The `completeness` term is why mentioning the experiment *structure* matters
even when many keywords are already present.

---

## 5. Peer Review `peer_review`

**What it measures.** Writing a constructive, technically sound review: finding
specific methodological weaknesses, suggesting concrete improvements, and giving
a recommendation.

**Data.** `MOCK_SUBMISSIONS`: two fabricated submissions, each with 6 recorded
`known_flaws` and keywords.

**Scoring.** For each submission, from response `raw`:

1. `flaws_found` = number of `known_flaws` detected by
   `_flaw_in_response(flaw, raw)`: a flaw is detected when ≥ 2 of its
   whitespace-separated words appear anywhere in the response.
2. `flaw_score = min(flaws_found / len(known_flaws) * 1.5, 1.0)`.
3. `kw_count` against the submission keywords;
   `kw_score = min(kw_count / len(keywords) * 1.5, 1.0)`.
4. `has_recommendation` = the response contains `accept` / `reject` / `revision` /
   `revise`; `rec_score = 1.0` if so else `0.3`.
5. `score = (flaw_score * 0.5 + kw_score * 0.3 + rec_score * 0.2) * 100`.

Final score is the mean over submissions. `details`: `{"per_paper": {id:
{"score", "flaws_found", "total_flaws", "has_recommendation", "length"}},
"average"}`.

**Baseline note.** Because `rec_score` is 0.3 even without a recommendation, an
empty response scores 6.0, not 0.0. A perfect response only needs all flaws
recognized, all keywords, and a recommendation → 100.0.

---

## 6. Reproduction `reproduction`

**What it measures.** Diagnosing why a paper's reported result does not
reproduce: listing plausible causes, a diagnostic plan, and a fix.

**Data.** `SCENARIOS`: two scenarios (CUDA/mismatch; GLUE RTE drift), each with
`key_causes` and keywords.

**Scoring.** For each scenario, from response `raw`:

1. `causes_found` = number of `key_causes` found as substrings.
2. `cause_score = min(causes_found / len(key_causes) * 1.5, 1.0)`.
3. `kw_count` against keywords; `kw_score = min(kw_count / len(keywords) * 1.5, 1.0)`.
4. `has_diagnosis` = the response contains `diagnose` / `check` / `compare` /
   `investigate` / `test`; `diagnosis_score = 1.0` if so else `0.5`.
5. `score = (cause_score * 0.5 + kw_score * 0.3 + diagnosis_score * 0.2) * 100`.

Final score is the mean over scenarios. `details`: `{"per_scenario": {id:
{"score", "causes_found", "keyword_coverage", "length"}}, "average"}`.

**Baseline note.** `diagnosis_score` floors at 0.5, so an empty response scores
10.0 (not 0.0). `has_diagnosis` coincidentally becomes true whenever keywords
like `test set` or `checkpoint` appear, so it typically reads 1.0 in keyword-rich
answers.

---

## 7. Open Question Identification `open_question_id`

**What it measures.** Identifying the single most important open question from a
body of work and arguing why it matters, what progress exists and what would be
needed to answer it.

**Data.** `PAPER_SETS`: two sets of 4 short paper summaries (LLM evaluation;
model interpretability).

**Scoring.** For each set, from response `raw`:

1. `coverage = min(kw_count / len(keywords) * 2, 1.0)`.
2. `has_importance` — contains one of `important, critical, key, fundamental,
   crucial`; `has_progress` — one of `progress, work, known, existing, current`;
   `has_future` — one of `future, next, would, could, need, direction`.
3. `quality = (has_importance + has_progress + has_future) / 3`.
4. `length_score = min(len(raw) / 400, 1.0)`.
5. `score = (coverage * 0.35 + quality * 0.4 + length_score * 0.25) * 100`.

Final score is the mean over sets. `details`: `{"per_set": {id: {"score",
"keyword_coverage", "has_importance", "has_future", "length"}}, "average"}`.

**Perfect answer:** all keywords + importance, progress and future signals +
≥ 400 chars → 100.0. Empty → 0.0.