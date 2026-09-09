---
schema_version: portable-project-memory/v1
handoff_revision: 11
updated_at: "2026-09-09T22:45:00+08:00"
updated_by: "agent-session"
base_revision: git:d78a47a5f8c48202b35a9080f2958c66aff0d630
status: active
---

# Project Handoff

## Current objective

`RESEARCH_BENCHMARK.md` remains the authoritative scientific design document.
The current package is an **evaluation-framework prototype**, not a validated
benchmark. Engineering phases 1-4 are merged. The next work must build a small
scientifically defensible pilot for heterogeneous integration / BEOL materials.

The benchmark's central question is: *Which AI system is genuinely the better
research assistant, in what research abilities, under what conditions, and how
do we know?*

## Confirmed state

- Local repository: `E:\Codex\Projects\caoshurong\researchbench`.
- Public repository: `https://github.com/CAOShurong/researchbench`.
- Default branch: `master`; HEAD = `d78a47a5f8c48202b35a9080f2958c66aff0d630`.
- Latest public CI run `32525629723` succeeded: 6 test jobs (3.9/3.11/3.13
  Ubuntu+Windows), mypy, build+clean-install smoke — all passed.
- Profile PR `CAOShurong/CAOShurong#90` merged; public wording calls it a prototype.

## P0 fixes merged (Phases 1-4)

- **Issue #3 / PR #4**: CLI `run` routes through `Benchmark.run()` with full provenance. Merge `0e39c16`.
- **Issue #5 / PR #8**: Authoritative `DATASET` for paper_comprehension; validate before model call; reject draft without `--allow-draft`; provenance required; `data unknown_task` exits 1. Merge `cc61bc0`.
- **Issue #7 / PR #9**: `RunRecord` CLI with import/validate/export; mandatory field validation; no hardcoded model names. Merge `49bea45`.
- **PR #10**: Doc sync (pyproject description, schema $id, RESEARCH_BENCHMARK status, RESULT.md, HANDOFF rev 9). Merge `d78a47a`.
- 260 tests pass on Python 3.9 and 3.13. ruff + mypy + format clean.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `src/researchbench/core.py` | Run-record metadata, raw-output capture, try/finally, parallel canonical order | Merged |
| `src/researchbench/dataset_schema.py` | Provenance required, validate_item enforces all fields, is_runnable | Merged |
| `src/researchbench/tasks/paper_comprehension.py` | Authoritative DATASET, validate before model call, draft rejection | Merged |
| `src/researchbench/subscription.py` | from_dict/from_json, validate_run_record, mandatory fields | Merged |
| `src/researchbench/cli.py` | --allow-draft, run-record command, data unknown_task exits 1 | Merged |
| `pyproject.toml`, `README.md`, `docs/` | Honest prototype positioning, schema $id fix | Merged |

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| Python 3.9 full suite | PASS | 260 passed; CI Ubuntu+Windows |
| Python 3.13 full suite | PASS | 260 passed; CI Ubuntu+Windows |
| ruff check + format | PASS | exit 0 |
| mypy | PASS | 14 files, no issues |
| Wheel build + clean install | PASS | sdist + wheel; installed CLI verified |
| Latest public CI | PASS | Run `32525629723`, 8 jobs at `d78a47a` |
| project_memory.py check | PASS | 0 errors, 0 warnings (this revision fixes the stale fingerprint) |

## Scientific validity remains the main product gap

## Risks and unknowns

- All 7 scorers still use keyword/substring matching (placeholder).
- No expert-validated items, gold rubrics, or human agreement measurements.
- No contamination-resistant pilots, real model results, or leaderboard.
- Pilot DatasetItem has review_status=draft (no expert review yet).
- Name collision with 2025 ResearchBench unresolved.
- v0.1.0 tag is stale; no new release until scientific pilot.

## Decisions referenced

- `D-20260821-093000-rb001`: keyword matching is a placeholder, not scientifically valid.
- `D-20260821-110000-rb006`: reposition as prototype, disclose name collision.
- Parent program `D-20260820-030000-c018` authorized creating this project.

## Phase 4 scientific pilot implemented (Issue #13)

- **Pilot dataset**: 5 domain-specific items for heterogeneous integration & BEOL-compatible
  materials/devices (`src/researchbench/tasks/heterogeneous_pilot.py`). Provenance, hard negatives,
  contamination risk, and structured rubrics verified.
- **Rubric evaluator**: Evidence-based criteria scoring with required patterns and negative indicator
  penalties (`src/researchbench/rubric.py`).
- **Human calibration pack**: `export_blinded_calibration_pack` with anonymized model IDs and randomized
  variant ordering for bias-free expert calibration.
- **Verification**: 270 unit tests passing cleanly; `ruff check`, `ruff format`, and `mypy` passing.

## Next actions

1. Human calibration study: recruit domain reviewers using blinded calibration pack.
2. Research existing benchmarks and name collision; propose 3 non-conflicting names.
3. Do not publish a leaderboard or model capability conclusions.
4. Do not release a new version until scientific pilot is validated.

## Coordination boundary

ResearchBench owns task definitions, datasets, rubrics, evaluator logic, and
the versioned run-record contract. SciModelMatrix owns running model/config
conditions and analyzing effort/model comparisons. Do not duplicate.

## Claims that remain prohibited

- Do not call the project a validated or comprehensive benchmark.
- Do not present keyword scores as model capability results.
- Do not claim current master is the released v0.1.0 artifact.
- Do not claim subscription/API execution or enforced dataset metadata beyond
  what the installed CLI proves.

## User decisions required

- A new public name is required before stable promotion (2025 ResearchBench collision).
- The release boundary after the scientific pilot is a user/product decision.
- Expert review of a small calibration sample is needed before claiming validity.