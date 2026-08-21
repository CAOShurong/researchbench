---
schema_version: portable-project-memory/v1
handoff_revision: 7
updated_at: "2026-08-21T15:30:00+08:00"
updated_by: "agent-session"
base_revision: git:8c6efc285f9384caa35a62ddfd0ca0ff6a3da663
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
  `37147770e0f346c21e564484af2864c82d009ac4`; worktree was clean at audit.
- Latest public CI run `32449901989` completed successfully at that exact head:
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
| Python 3.9 full suite | PASS | 184 passed; 90.23% coverage; exit 0 in `E:\Codex\Scratch\researchbench-audit-20260821\venv39` |
| Python 3.13 full suite | PASS | 184 passed; 90.23% coverage; exit 0 in `E:\Codex\Scratch\researchbench-audit-20260821\venv313` |
| Ruff lint + format | PASS | `ruff check src tests` and `ruff format --check src tests`; exit 0 |
| mypy | PASS | `mypy src`; 14 source files; exit 0 |
| sdist/wheel build | PASS | `researchbench-0.1.0.tar.gz` and `researchbench-0.1.0-py3-none-any.whl`; exit 0 |
| Clean Python 3.9 wheel install | PASS | `pip check`, `--version`, `list`, and `verify`; exit 0 |
| CLI invalid-task path | PASS | unknown task exits 2 with a Click validation error |
| Latest public CI | PASS | GitHub Actions run `32449901989`, eight jobs at exact head `37147770...` |
| Portable memory check before this rewrite | FAIL | stale recorded workspace fingerprint; this handoff was contradictory |

## Decisions referenced

- `D-20260821-093000-rb001`: keyword matching is a deterministic v0.1.0
  placeholder; it is not scientifically valid.
- `D-20260821-110000-rb006`: reposition publicly as a prototype, disclose the
  name collision, and correct false novelty claims.
- `E:\Codex\Projects\caoshurong\github-sources-program\DECISIONS.md` contains
  parent-program decision `D-20260820-030000-c018` for creating this project.

## Risks and unknowns

The following defects and unknowns are material to the next implementation:

### P0 fixes merged (Phases 1-2)

- **Issue #3 / PR #4**: CLI `run` now routes through `Benchmark.run()` with
  full provenance (timestamp, version, raw_output, duration, evaluator_version).
  Parallel preserves canonical order. `--save-responses` appends. `try/finally`
  restores monkeypatches. `report --from` round-trips all fields. Merge `0e39c16`.
- **Issue #5 / PR #6**: One pilot `DatasetItem` with structured `Provenance`
  (source_id, license, review_status) migrated in `paper_comprehension`. CLI
  `data --validate` calls `validate_item()` and exits 1 on invalid. `data --format
  json` exports full metadata. Merge `8c6efc2`.
- 216 tests pass. CI green on all 8 jobs (3.9/3.11/3.13 Ubuntu+Windows, mypy, build).

## Remaining P0/P1

- Subscription/API records not yet connected to runner/CLI (Phase 3).
- Docs still say "no reproducibility" etc. — need sync (Phase 4).
- No scientific pilot yet (Phase 5).
- v0.1.0 tag is stale; no new release until P0 closed.

## Scientific validity remains the main product gap

- All seven scorers still use keyword/substring matching. The 184 tests prove
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

1. **Close the end-to-end CLI integrity gap.** Route sequential CLI execution
   through one shared runner; preserve timestamp/version/config/raw output/
   duration/evaluator; retain all responses; preserve canonical order in
   parallel mode; restore monkeypatches with `try/finally`; make `report --from`
   round-trip every provenance field. Add installed-CLI success/failure and
   sequential/parallel regression tests.
2. **Integrate dataset validation.** Convert one pilot task to versioned
   `DatasetItem` records, validate on load/run/export, reject missing/invalid
   metadata with a non-zero CLI exit, and keep the legacy placeholder clearly
   labeled. Do not convert all seven tasks before the pilot schema is proven.
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
