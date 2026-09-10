---
schema_version: portable-project-memory/v1
handoff_revision: 12
updated_at: "2026-09-10T16:20:00+08:00"
updated_by: "grok-build-session"
base_revision: git:d1924f5c683429968ec74abcaa8a0ed3e4e19560
workspace_fingerprint: sha256:465d8b6840b1a1538de95131bafa48b9031843d3b9cbe118cc7c26d423800160
context_fingerprint: sha256:5a7362dee182cc6bf6c5f6f7b453ef9ea6b19cf885bdc911a921622dc58b0f8d
status: active
---

# Project Handoff

## Current objective

`RESEARCH_BENCHMARK.md` remains the authoritative scientific design document.
The package is an **evaluation-framework prototype**, not a validated
benchmark. The BEOL / heterogeneous-integration scientific pilot is now
reachable from the CLI. Remaining work that an agent can do without a human
expert is listed below; expert calibration and the public name are not.

## Confirmed state

- GitHub: `https://github.com/CAOShurong/researchbench` (private).
- Default branch: `master`; parent commit before this work =
  `d1924f5c683429968ec74abcaa8a0ed3e4e19560`.
- 275 tests passed on this checkout (`pytest tests`, `pythonpath = src`).
- ruff check + format + mypy (16 source files) passed after the wiring
  change.
- PROJECT_CONTEXT forbids pushing until the user asks. This work is local.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `src/researchbench/core.py` | Canonical 8th task; per-task evaluator_version; dataset lookup helper | Local, uncommitted |
| `src/researchbench/cli.py` | TASK_INFO + sample path; dynamic verify count; dataset aliases | Local, uncommitted |
| `src/researchbench/tasks/heterogeneous_pilot.py` | `DATASET` / `PILOT_ITEMS` aliases | Local, uncommitted |
| `docs/BENCHMARK_COMPARISON.md` | §8 competitor comparison | Local, uncommitted |
| `docs/NAME_CANDIDATES.md` | Three rename options | Local, uncommitted |
| `tests/conftest.py`, `pyproject.toml` | Local src on PYTHONPATH for CLI subprocess tests | Local, uncommitted |

## Risks and unknowns

- Another `researchbench` install on this machine can shadow `python -m researchbench` unless PYTHONPATH/src is set.
- Rubric regexes can be gamed; human calibration is still missing.
- Pilot `contamination_risk=low` is optimistic for textbook BEOL facts.
- Name collision with Liu et al. is unresolved.

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| Full suite | PASS | 275 passed |
| ruff check + format | PASS | exit 0 after `--fix` |
| mypy src | PASS | 16 files, no issues |
| `run --tasks heterogeneous_pilot` without `--allow-draft` | PASS | CLI wiring test |
| `data heterogeneous_pilot --validate` | PASS | 5 items OK |

## Scientific validity remains the main product gap

- Seven legacy scorers still use keyword/substring matching.
- No expert-validated human agreement on the five pilot items.
- No contamination-resistant items from post-cutoff papers.
- No real model results; do not publish a leaderboard.
- Name collision with Liu et al. ResearchBench (ACL 2026 Findings) unresolved.

## Decisions referenced

- `D-20260910-160000-rb014`: wire the BEOL pilot into Benchmark and CLI.
- `D-20260821-093000-rb001`: keyword matching is a placeholder.
- `D-20260821-110000-rb006`: reposition as prototype; disclose name collision.

## Next actions

Agent-doable (continue without waiting):

1. Add one contamination-resistant pilot item grounded in a paper published
   after typical training cutoffs (cite arXiv/DOI in provenance; do not fake
   expert review — mark `review_status=draft` until a human reviews it).
2. Keep docs honest if more competitors appear.

Human-only (do not fake):

3. Human calibration study with the blinded pack.
4. Choose a public name from `docs/NAME_CANDIDATES.md` (or reject all three).
5. Do not release a new version until the scientific pilot is validated.
6. Do not publish a leaderboard or model-capability conclusions.

## Coordination boundary

ResearchBench owns task definitions, datasets, rubrics, evaluator logic, and
the versioned run-record contract. SciModelMatrix owns running model/config
conditions. Do not duplicate. Do not work on upstream GitHub PRs from this
handoff.

## Claims that remain prohibited

- Do not call the project a validated or comprehensive benchmark.
- Do not present keyword scores as model capability results.
- Do not claim current master is the released v0.1.0 artifact.
- Do not claim this project is the first "ResearchBench".

## User decisions required

- A new public name before stable promotion.
- Expert review of a small calibration sample.
- Whether to push this local commit.
