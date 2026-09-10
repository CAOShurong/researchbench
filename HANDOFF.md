---
schema_version: portable-project-memory/v1
handoff_revision: 16
updated_at: "2026-09-10T21:15:00+08:00"
updated_by: "loop-5m"
base_revision: git:a070247626738cd120ee69257c170b5d64f0c34b
workspace_fingerprint: sha256:a070247626738cd120ee69257c170b5d64f0c34b
context_fingerprint: sha256:a070247626738cd120ee69257c170b5d64f0c34b
status: active
---

# Project Handoff

## Current objective

Keep `researchbench` an **honest, agent-shippable evaluation-framework
prototype**. The user will not review, approve, or calibrate. Do not create
work that needs them later.

## Confirmed state

- GitHub: `https://github.com/CAOShurong/researchbench` (private).
- Default branch: `master` (this fire: `a070247`).
- Package version **0.4.1** (v0.4.0 tag remains at 372ef51, before CLI
  wiring and q6).
- 281 tests passed (pytest), ruff and mypy clean on this fire.
- 5-minute loop ID `01a08bab-693b-77a3-b80a-c1f65ca459e4` with skip-if-busy.
- Package/repo name stays `researchbench`. Collision with Liu et al. is
  disclosed, not resolved by rename.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `pyproject.toml`, `src/researchbench/__init__.py` | version 0.4.1 | This fire |
| `README.md`, `docs/USAGE.md`, `docs/FAQ.md`, `docs/API.md`, `docs/CONTRIBUTING.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` | CLI/docs honesty; 281 tests | This fire |
| `src/researchbench/cli.py` | `--allow-draft` examples in `--help` | This fire |

## Risks and unknowns

- Prototype is not a validated benchmark and never will be without humans.
- q6 stays draft. That is the end state, not a queue.
- Overlapping loops must use the lock or they will race.
- GitHub MCP list_releases 404'd; releases are cut with local `gh`.

## Verification evidence

| Check | Result | Basis |
|---|---|---|
| pytest tests | PASS | 281 passed |
| ruff check/format | PASS | src + tests |
| mypy src | PASS | 16 files |

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
