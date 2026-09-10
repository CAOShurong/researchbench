---
schema_version: portable-project-memory/v1
handoff_revision: 14
updated_at: "2026-09-10T20:10:00+08:00"
updated_by: "grok-build-session"
base_revision: git:7e0f81f52c78e844ddc89669e2151a9805f11512
workspace_fingerprint: sha256:eb420656af466c6d6dfd7151bacc680d5b55144451f510aacb19ca36a4cf0ed9
context_fingerprint: sha256:650222bc80736b8c6c8c5064d95a6b332b5d573316685afc0b94abf3e2a06af2
status: active
---

# Project Handoff

## Current objective

`RESEARCH_BENCHMARK.md` remains the authoritative scientific design document.
This is a prototype, not a validated benchmark. Push is allowed. Overlapping
agents must skip via `.ai/agent_lock.py`.

## Confirmed state

- GitHub: `https://github.com/CAOShurong/researchbench` (private).
- Default branch: `master`; last pushed parent of this uncommitted work =
  `7e0f81f52c78e844ddc89669e2151a9805f11512`.
- 281 tests passed (`pytest tests`).
- ruff + mypy passed.
- User 2026-09-10: push allowed; 5-minute continuation loop; skip if busy.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `.ai/agent_lock.py` | Skip-if-busy lock; stale after 12 min | Uncommitted |
| `.gitignore` | Ignore `agent.lock` | Uncommitted |
| `README.md`, `docs/USAGE.md`, `PROJECT_CONTEXT.md` | 8 tasks, 277→281 tests, honest prototype | Uncommitted |
| `heterogeneous_pilot.py` q6 notes | Grounded in paper PDF text as well as abstract; still draft | Uncommitted |

## Risks and unknowns

- Rubric regexes can be gamed; human calibration is missing.
- q6 is still `draft`.
- Name collision with Liu et al. ResearchBench is unresolved.
- A 5-minute loop that forgets to acquire the lock can still race.

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| Full suite | PASS | 281 passed |
| ruff check | PASS | src, tests, agent_lock |
| mypy src | PASS | 16 files |
| Lock tests | PASS | busy / release / stale steal |

## Scientific validity remains the main product gap

- Seven legacy scorers still use keyword matching.
- No human agreement measurements.
- Do not publish a leaderboard.

## Decisions referenced

- `D-20260910-200000-rb016`: push allowed; overlapping agents skip.
- `D-20260910-180000-rb015`: mixed reviewed+draft skip drafts unless `--allow-draft`.
- `D-20260910-160000-rb014`: wire the BEOL pilot into Benchmark and CLI.
- `D-20260821-093000-rb001`: keyword matching is a placeholder.
- `D-20260821-110000-rb006`: prototype positioning; name collision.

## Next actions

Agent-doable (loop, skip if lock BUSY):

1. More 2025/2026 paper-grounded **draft** items if they are real papers with
   DOI/arXiv. Never mark them reviewed.
2. Keep docs matched to the CLI.
3. Push after each material commit.

Human-only:

4. Expert review of q6 (Cheng et al., arXiv:2603.23341).
5. Blinded calibration study.
6. Public name (DeviceReason / AssistTrace / EEWorkEval). Do not rename
   the GitHub/Python package until chosen.

## Coordination boundary

ResearchBench owns tasks, datasets, rubrics, evaluator, run records.
Do not work on upstream GitHub PRs from this handoff.

## Claims that remain prohibited

- Do not call this a validated benchmark.
- Do not present keyword scores as model capability.
- Do not claim this is the first ResearchBench.
- Do not claim q6 is expert-reviewed.

## User decisions required

- Expert review / calibration.
- Public name (package rename still waiting).
