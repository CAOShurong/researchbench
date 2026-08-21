# Decision Log

This file is append-only. Supersede an entry explicitly rather than silently
rewriting history.

# Decisions

## D-20260821-093000-rb001

### Use deterministic keyword scoring, not LLM-as-judge, as the default
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The initial scaffold used keyword-based scoring. The RESEARCH.md proposed
LLM-as-judge as an alternative for open-ended tasks.

### Decision

Keep deterministic keyword scoring as the default (and only) mode for v0.1.0.
The scoring is reproducible, testable, and does not require API keys. LLM-as-
judge is deferred to ROADMAP as an optionally gated future feature.

### Consequences

- All 7 tasks have testable, deterministic scoring formulas documented in
  TASK_DEFINITIONS.md.
- Mock mode provides reliable smoke tests without API keys.
- LLM-as-judge remains a proposed feature, not a commitment.

## D-20260821-093001-rb002

### Drop unused runtime dependencies
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The initial pyproject.toml declared `pydantic`, `pyyaml`, `rich`, and `click`
as runtime dependencies. A full grep of the codebase (src, tests, examples)
found zero imports of `pydantic`, `pyyaml`, or `rich`.

### Decision

Remove the three unused dependencies. Keep only `click` as the runtime
dependency. `openai` and `anthropic` remain in the optional `[judge]` extra.

### Consequences

- Wheel declares only `click>=8.0` as a runtime dependency.
- A fresh venv installs only `click` + `researchbench`.
- All 162 tests pass against the installed wheel.
- Verified by `pip check` in the clean venv.

## D-20260821-093002-rb003

### Bundle report-schema.json inside the package
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The `schema` command initially read the JSON Schema from `docs/`. This path
resolution failed when the package was installed from a wheel (no `docs/` in
site-packages).

### Decision

Move the schema file into `src/researchbench/report-schema.json` and add it to
`[tool.setuptools.package-data]`. The `schema` command reads from
`Path(__file__).parent / "report-schema.json"`.

### Consequences

- `researchbench schema --save <path>` works from an installed wheel.
- A copy remains at `docs/report-schema.json` for browser access.
- Verified: built wheel, installed in clean venv, schema command produces valid JSON.

## D-20260821-110000-rb006

### Reposition as prototype; fix false novelty claims; fix CI on Python 3.9
- Status: accepted
- Date: 2026-08-21
- Deciders: user (direct directive), build session
- Supersedes: none

### Context

The user identified that:
1. A 2025 "ResearchBench" paper and code repo already exists (scientific
   discovery, idea retrieval, hypothesis generation) — direct name collision.
2. ResearcherBench, DeepResearch Bench, and RPC-Bench (ACL 2026) also cover
   overlapping territory.
3. The public README and RESEARCH.md claimed "no existing benchmark covers this
   gap" — this was false.
4. The project has no expert-validated data, gold answers, model results, or
   leaderboard — it is a prototype, not a "comprehensive benchmark."
5. CI was red on Python 3.9 (`test_run_benchmark` failing due to click stderr
   capture differences between click 8.1.x and 8.2+).
6. PyPI project does not exist; GitHub Release has no assets.

### Decision

1. **Reposition**: update README, RESEARCH_BENCHMARK.md, RESEARCH.md,
   HANDOFF.md to honestly describe the project as a "research-capability
   evaluation framework prototype," not a validated benchmark.
2. **Correct false claims**: remove "fills a gap no existing benchmark covers"
   and "no existing benchmark tests this" from all public-facing docs.
   Acknowledge the 2025 ResearchBench and other competitors by name.
3. **Fix CI**: `test_run_benchmark` now checks `result.output +
   getattr(result, "stderr", "")` for cross-click-version safety.
4. **Naming**: flag the name collision as a risk; a rename is a user decision.

### Consequences

- The project cannot claim to be the first or only benchmark in this space.
- All marketing/profile claims must be updated to reflect prototype status.
- The CI should now pass on Python 3.9 (the test fix is cross-version safe).
- A rename may be necessary before any public promotion.

### Write RESEARCH_BENCHMARK.md and freeze keyword-matching as a known-invalid placeholder
- Status: accepted
- Date: 2026-08-21
- Deciders: user (direct directive), build session
- Supersedes: none (extends D-20260821-093000-rb001)

### Context

A full audit of all 7 task modules revealed that every task uses keyword
substring matching as its sole scoring method. This is scientifically
indefensible: keyword stuffing scores 100, correct paraphrases that use
different vocabulary score 0, hallucinations are undetectable, citations are
unevaluated, and verbosity is rewarded. RESEARCH.md itself diagnosed that
"research capability resists simple metrics" and prescribed LLM-as-judge +
human validation + real data — the code chose the opposite.

### Decision

1. Write `RESEARCH_BENCHMARK.md` as the authoritative design document. It
   defines purpose, philosophy, a 16-capability taxonomy, dataset validity
   requirements, evaluation principles, subscription/API protocol,
   reproducibility requirements, and next steps.
2. Explicitly label the current v0.1.0 keyword-matching scoring as a
   **placeholder** that is not scientifically valid. Do not present
   keyword-matching scores as real model evaluations.
3. Add a mandatory reading notice to `AI_START_HERE.md` and `HANDOFF.md`
   pointing to `RESEARCH_BENCHMARK.md`.
4. Retain the CLI/packaging/CI/test infrastructure but redesign the scoring
   methodology, dataset design, and evaluation protocol per
   RESEARCH_BENCHMARK.md Section 11.

### Consequences

- No new keyword-matching tasks should be added. The existing 7 tasks' scoring
  must be replaced with evidence-based evaluation.
- The 162 existing tests verify the keyword-matching mechanics, not scientific
  validity. They remain valid as regression tests for the placeholder, but new
  tests must validate the new evaluation methods.
- The benchmark cannot claim to measure research capability until the
  replacement is complete and validated.
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

Adding `--save-responses` (save raw model responses to disk) and `--parallel`
(concurrent task evaluation) would normally require changing the `evaluate()`
interface across all 7 task modules.

### Decision

- `--parallel`: uses `concurrent.futures.ThreadPoolExecutor` in the CLI's `run`
  command, calling `task.evaluate()` per task. No task module changes.
- `--save-responses`: monkeypatches each task module's `_call_model` at runtime
  via `setattr(mod, "_call_model", wrapper)`. The wrapper saves the response
  and delegates to the original. No task module changes.

### Consequences

- All 7 task modules remain unchanged.
- The features are opt-in CLI flags.
- Verified by tests (`test_run_parallel`, `test_run_save_responses`).