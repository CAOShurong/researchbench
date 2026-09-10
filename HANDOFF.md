---
schema_version: portable-project-memory/v1
handoff_revision: 15
updated_at: "2026-09-10T20:30:00+08:00"
updated_by: "grok-build-session"
base_revision: git:fd9cb057e31cb33b9e2ccc143806ba55562c771a
workspace_fingerprint: sha256:eb420656af466c6d6dfd7151bacc680d5b55144451f510aacb19ca36a4cf0ed9
context_fingerprint: sha256:0c7290d5efb4327a1173eae0d3a2d61d17f80176ef88fdc360336ff900f816b6
status: active
---

# Project Handoff

## Current objective

Keep `researchbench` an **honest, agent-shippable evaluation-framework
prototype**. The user will not review, approve, or calibrate. Do not create
work that needs them later.

## Confirmed state

- GitHub: `https://github.com/CAOShurong/researchbench` (private).
- Default branch: `master` (pushed through `fd9cb05` before this revision).
- 281 tests passed on the last full run.
- 5-minute loop ID `01a08bab-693b-77a3-b80a-c1f65ca459e4` with skip-if-busy.
- Package/repo name stays `researchbench`. Collision with Liu et al. is
  disclosed, not resolved by rename.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `PROJECT_CONTEXT.md`, `DECISIONS.md`, this file | No human follow-up; agent-complete only | This commit |
| 5-minute loop prompt | Same constraint; skip if lock BUSY | Updated in scheduler |

## Risks and unknowns

- Prototype is not a validated benchmark and never will be without humans.
- q6 stays draft. That is the end state, not a queue.
- Overlapping loops must use the lock or they will race.

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| Last full suite | PASS | 281 passed at fd9cb05 |
| origin/master | PUSHED | fd9cb05 |

## Decisions referenced

- `D-20260910-203000-rb017`: no human follow-up; agent-complete work only.
- `D-20260910-200000-rb016`: push allowed; overlapping agents skip.
- `D-20260910-180000-rb015`: drafts skipped unless `--allow-draft`.
- `D-20260910-160000-rb014`: pilot wired into CLI.
- `D-20260821-093000-rb001`: keyword matching is a placeholder.

## Next actions

Agent-finishable only (then commit + push):

1. Keep CI/tests/docs matching the CLI.
2. Cut GitHub releases yourself when a version bump is justified by code.
3. If tests fail, fix them.
4. If lock BUSY, skip.

Do **not**: add paper items for later review; ask for a name; ask for
calibration; assign the user any task.

## Coordination boundary

This repository only. No upstream PRs. No new product repos.

## Claims that remain prohibited

- Do not call this a validated or comprehensive benchmark.
- Do not present keyword scores as model capability.
- Do not claim q6 is expert-reviewed.
- Do not claim this is the first ResearchBench.

## User decisions required

None. The user will not make further decisions. Proceed without them.
