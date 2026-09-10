---
schema_version: portable-project-memory/v1
handoff_revision: 13
updated_at: "2026-09-10T18:40:00+08:00"
updated_by: "grok-build-session"
base_revision: git:5c657d5f9fdc460368e2e87f6e588fd883da406e
workspace_fingerprint: sha256:c00e9b1a419b7bba7d4befc60403abaa1cffe97c1093ace78af843dc8554ee20
context_fingerprint: sha256:69dbc861260a875cbd7a6a8fccc7c63753f6a2048a5269316056e92cac49c972
status: active
---

# Project Handoff

## Current objective

`RESEARCH_BENCHMARK.md` remains the authoritative scientific design document.
The package is an **evaluation-framework prototype**, not a validated
benchmark. The BEOL / heterogeneous-integration scientific pilot is reachable
from the CLI. The agent-doable contamination-resistant draft item is now in
the dataset; remaining work is human (expert review, name, release).

## Confirmed state

- GitHub: `https://github.com/CAOShurong/researchbench` (private).
- Default branch: `master`; parent commit before this work =
  `5c657d5f9fdc460368e2e87f6e588fd883da406e`.
- 277 tests passed on this checkout (`pytest tests`, `pythonpath = src`).
- ruff check + format + mypy (16 source files) passed after the draft item.
- PROJECT_CONTEXT forbids pushing until the user asks. This work is local.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `src/researchbench/tasks/heterogeneous_pilot.py` | Draft q6 (arXiv:2603.23341); skip drafts unless `allow_draft` | Local, uncommitted |
| `src/researchbench/core.py` | Mixed datasets run reviewed items; draft-only still blocked | Local, uncommitted |
| `tests/test_heterogeneous_pilot.py` | 6-item schema; default run=5; `--allow-draft`=6 | Local, uncommitted |
| `docs/BENCHMARK_COMPARISON.md` | Contamination section notes the 2026 draft item | Local, uncommitted |
| `CHANGELOG.md`, `DECISIONS.md` | q6 + D-20260910-180000-rb015 | Local, uncommitted |

## Risks and unknowns

- Another `researchbench` install on this machine can shadow `python -m researchbench` unless PYTHONPATH/src is set.
- Rubric regexes can be gamed; human calibration is still missing.
- Five reviewed items still have optimistic `contamination_risk=low` for textbook BEOL facts.
- q6 facts are from the Cheng et al. 2026 *abstract* only; full-paper expert check is pending.
- Name collision with Liu et al. is unresolved.

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| Full suite | PASS | 277 passed |
| ruff check + format | PASS | exit 0 after format |
| mypy src | PASS | 16 files, no issues |
| `run --tasks heterogeneous_pilot` without `--allow-draft` | PASS | 5 reviewed items; q6 skipped |
| `run --tasks heterogeneous_pilot --allow-draft` | PASS | 6 items |
| `data heterogeneous_pilot --validate` | PASS | 6 items OK |

## Scientific validity remains the main product gap

- Seven legacy scorers still use keyword/substring matching.
- No expert-validated human agreement on the five reviewed pilot items.
- q6 is a post-cutoff *draft*; do not claim it is validated.
- No real model results; do not publish a leaderboard.
- Name collision with Liu et al. ResearchBench (ACL 2026 Findings) unresolved.

## Decisions referenced

- `D-20260910-180000-rb015`: mixed reviewed+draft datasets skip drafts unless `--allow-draft`.
- `D-20260910-160000-rb014`: wire the BEOL pilot into Benchmark and CLI.
- `D-20260821-093000-rb001`: keyword matching is a placeholder.
- `D-20260821-110000-rb006`: reposition as prototype; disclose name collision.

## Next actions

Agent-doable: none remaining without a human. Agent queue is idle until expert
review of q6, a public name, or an explicit push request.

Human-only (do not fake):

1. Human calibration study with the blinded pack.
2. Expert review of draft item `heterogeneous_pilot/igzo_in2o3_channel_capping/q6`
   (Cheng et al., arXiv:2603.23341) against the full paper.
3. Choose a public name from `docs/NAME_CANDIDATES.md` (or reject all three).
4. Do not release a new version until the scientific pilot is validated.
5. Do not publish a leaderboard or model-capability conclusions.

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
- Do not claim q6 is expert-reviewed or contamination-proof in production.

## User decisions required

- A new public name before stable promotion.
- Expert review of a small calibration sample, including q6.
- Whether to push this local commit.
