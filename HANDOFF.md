---
schema_version: portable-project-memory/v1
handoff_revision: 8
updated_at: "2026-08-21T21:26:37+08:00"
updated_by: "Codex independent audit"
base_revision: git:ecedf56a9ff37579da23d1e50dae4ca4e4c8432c
workspace_fingerprint: sha256:3f01bae0bdccc90f2365f6d540bcc688584e5e083c89c31b912555de499f8641
context_fingerprint: sha256:27846abba75b153341b21dd871fb41c7cacaed64276f4075dde21112faf9bf22
status: active
---

# Project Handoff

## Current objective

`RESEARCH_BENCHMARK.md` remains the authoritative scientific design document.
The current package is an **evaluation-framework prototype**, not a validated
benchmark. The next work must close end-to-end integrity gaps before adding
more framework surface, then build a small defensible scientific pilot.

The benchmark's central question is: *Which AI system is genuinely the better
research assistant, in what research abilities, under what conditions, and how
do we know?*

## Confirmed state

- Local repository: `E:\Codex\Projects\caoshurong\researchbench`.
- Public repository: `https://github.com/CAOShurong/researchbench`.
- Default branch: `master`; local HEAD and `origin/master` both equal
  `ecedf56a9ff37579da23d1e50dae4ca4e4c8432c`; the tracked worktree was clean
  before this handoff-only update.
- Latest public CI run `32485549359` completed successfully at that exact head:
  six Ubuntu/Windows Python 3.9/3.11/3.13 test jobs, one mypy job, and one
  build/clean-install smoke job all passed.
- Public Profile PR `CAOShurong/CAOShurong#90` merged as
  `981f9ecbb0d9ad1411c2a0804702d4e403b340a7`; PR and post-merge Profile link
  workflows passed. The public wording now calls ResearchBench a prototype.

## Changed artifacts

The latest round changed these substantive areas:

- `src/researchbench/core.py` now adds timestamp, benchmark version, run config,
  task duration, evaluator version, and captured raw responses to the **Python
  API path** `Benchmark.run()`.
- `src/researchbench/subscription.py` defines serializable `SubscriptionRun`,
  `APIRun`, and `RunRecord` data classes and prevents mixing API and
  subscription records in one `RunRecord`.
- `src/researchbench/dataset_schema.py` defines `DatasetItem` plus a manual
  `validate_item()` function for C1-C16 tags, scoring method, contamination
  risk, provenance text, and related metadata.
- The Python 3.9 Click stderr compatibility regression was fixed.
- README/Profile novelty overclaims were reduced, and the existing 2025
  ResearchBench name collision is now disclosed.
- All latest commits are pushed; the old handoff claim of three unpushed commits
  was stale.

## Verification evidence

| Check | Result | Exact basis |
|---|---|---|
| Python 3.9 full suite | PASS | 216 passed; 88.25% coverage; exit 0 in fresh `E:\Codex\Scratch\researchbench-round2-audit-20260821\venv39` |
| Python 3.13 full suite | PASS | 216 passed; 88.25% coverage; exit 0 in fresh `E:\Codex\Scratch\researchbench-round2-audit-20260821\venv313` |
| Ruff lint + format | PASS | `ruff check src tests` and `ruff format --check src tests`; exit 0 |
| mypy | PASS | `mypy src`; 14 source files; exit 0 |
| sdist/wheel build | PASS | `researchbench-0.1.0.tar.gz` and `researchbench-0.1.0-py3-none-any.whl`; exit 0; hashes in the independent audit |
| Clean Python 3.13 wheel install | PASS | installed from wheel outside the checkout; `--version`, `verify`, data validation, real run/save/raw-response, and invalid-run paths observed |
| CLI invalid-task path | PASS | unknown task exits 2 with a Click validation error |
| Latest public CI | PASS | GitHub Actions run `32485549359`, eight jobs at exact head `ecedf56...` |
| Portable memory structure | PASS | `project_memory.py check`; semantic contradictions required this manual audit and revision |

Detailed evidence: `E:\Codex\Workspaces\Dated\2026-08-21\researchbench-round2-audit\outputs\AUDIT.md`.

## Decisions referenced

- `D-20260821-093000-rb001`: keyword matching is a deterministic v0.1.0
  placeholder; it is not scientifically valid.
- `D-20260821-110000-rb006`: reposition publicly as a prototype, disclose the
  name collision, and correct false novelty claims.
- `E:\Codex\Projects\caoshurong\github-sources-program\DECISIONS.md` contains
  parent-program decision `D-20260820-030000-c018` for creating this project.

## Risks and unknowns

The following defects and unknowns are material to the next implementation:

### P0 Phase 1 is closed; Phase 2 is only partially closed

- **Issue #3 / PR #4**: CLI `run` now routes through `Benchmark.run()` with
  full provenance (timestamp, version, raw_output, duration, evaluator_version).
  Parallel preserves canonical order. `--save-responses` appends. `try/finally`
  restores monkeypatches. `report --from` round-trips all fields. Merge `0e39c16`.
- **Issue #5 / PR #6**: One pilot `DatasetItem` with structured `Provenance`
  (source_id, license, review_status) migrated in `paper_comprehension`. CLI
  `data --validate` calls `validate_item()` and exits 1 on invalid. `data --format
  json` exports full metadata. Merge `8c6efc2`.
- **Critical limit found by the independent audit:** PR #6 did not integrate
  `DatasetItem` validation into `Benchmark.run()`. The runner still evaluates
  legacy `PAPERS`. An in-memory invalid pilot item failed `validate_item()` but
  the benchmark still ran successfully. Text data reports two legacy items,
  while JSON exports one pilot item. Phase 2 is not end-to-end complete.
- `DatasetItem.provenance` remains optional, and `RunRecord` accepts empty
  required-looking identifiers. `researchbench data does_not_exist` also exits
  0 despite reporting an unknown task.
- 216 tests pass. CI is green on all 8 jobs (3.9/3.11/3.13 Ubuntu+Windows, mypy,
  build), but those tests do not cover the enforcement failures above.

## Remaining P0/P1

- Dataset records are not the authoritative run input and are not validated on
  run/load; text, JSON, and runner paths expose different collections.
- Runnable-item provenance and subscription/API record fields are not enforced.
- Subscription/API records not yet connected to runner/CLI (Phase 3).
- Docs still say "no reproducibility" etc. — need sync (Phase 4).
- No scientific pilot yet (Phase 5).
- v0.1.0 tag is stale; no new release until P0 closed.

## Scientific validity remains the main product gap

- All seven scorers still use keyword/substring matching. The 216 tests prove
  those mechanics and software reliability; they do not validate scientific
  measurement.
- There are no expert-validated items, evidence sets, gold rubrics, human
  agreement measurements, contamination-resistant pilots, real model results,
  or leaderboard.
- `DatasetItem` currently permits free-text provenance such as an unsupported
  claim that an expert verified an item. A defensible pilot needs real source
  identifiers, licensing, item-author/reviewer roles, and an auditable review
  record.
- The project name collides with a published 2025 ResearchBench. A rename is
  still unresolved and should be settled before promotion or a stable release.

## Next actions

1. **Finish Phase 2 with one authoritative dataset path.** Make the versioned
   `DatasetItem` collection the source used by `sample`, text/JSON `data`, and
   `Benchmark.run()` for `paper_comprehension`; remove or explicitly quarantine
   the legacy split. Validate before sequential and parallel execution and fail
   nonzero before any model call when metadata is invalid.
2. **Enforce a runnable-item contract.** Require structured provenance,
   non-unknown licensing, source identity, author/reviewer roles, and an
   explicit eligible review state. Keep draft items exportable only under an
   explicit draft path. Make unknown `data` tasks nonzero and add installed-CLI
   success/failure tests.
3. **Integrate subscription/API records.** Add a model/config-driven import and
   export contract that both ResearchBench and the separate SciModelMatrix
   project can consume. Validate mandatory fields and keep subscription/API
   runs as distinct conditions. Do not hard-code current model names.
4. **Synchronize truthful metadata.** Fix the schema `$id`, Profile fragment,
   package description, README/API/design status sections, and project-memory
   contradictions. Run link checks and `project_memory.py check`.
5. **Resolve release identity only after P0 fixes.** Choose a new development
   version and release boundary; do not retag v0.1.0 or create version churn.
   A future release must have assets, hashes/attestation where supported, and a
   clean public download/install/behavior verification. PyPI remains absent.
6. **Then build a scientific pilot, not more scaffolding.** Complete the
   evidence-backed competitor table; create a small licensed pilot for paper
   comprehension and peer review; include hard negatives, exact source
   provenance, task-specific rubrics, contamination assessment, and blinded
   human scoring instructions. Validate any LLM judge against human ratings
   before using it for benchmark claims.

## Coordination boundary

ResearchBench owns task definitions, datasets, rubrics, evaluator logic, and
the versioned run-record contract. SciModelMatrix owns running model/config
conditions and analyzing effort/model comparisons. The general OSS task owns
portfolio evidence, upstream contributions, maintainership, and independent
adoption. Do not duplicate these responsibilities across agents.

## Claims that remain prohibited

- Do not call the project a validated or comprehensive benchmark.
- Do not present keyword scores as model capability results.
- Do not call owner tests, mock runs, downloads, or Profile links independent
  adoption.
- Do not claim current master is the released v0.1.0 artifact.
- Do not claim subscription/API execution or enforced dataset metadata until
  the installed CLI proves those paths.

## User decisions required

- A new public name is required before stable promotion because the current
  name collides with the published 2025 ResearchBench. No rename is authorized
  by this audit.
- The release boundary/version after the P0 integrity fixes is a user/product
  decision. Do not retag or overwrite public v0.1.0.
