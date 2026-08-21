---
schema_version: portable-project-memory/v1
handoff_revision: 2
updated_at: "2026-08-21T09:48:00+08:00"
updated_by: "agent-session"
base_revision: git:d38fa44bf0466f74d554ad0225086f7a203b75a5
workspace_fingerprint: sha256:0d906c19e56197d660944731fba8e5aa667cf3f0eb18fbfa9a473d390ae22d59
context_fingerprint: sha256:d57d4481f2ba5110f49e1ab87e6500cd1b9b734a2dab98c0a87acf9a18b3b6d7
status: active
---

# Project Handoff

## Current objective

ResearchBench (v0.1.0) is feature-complete: 162 tests, 10 CLI commands, 7 task
modules, full docs, CI green, wheel builds and installs cleanly. The next agent
should continue on the ROADMAP items (LLM-as-judge mode, expert-validated data,
cross-lingual packs) or address any user-requested features/bugs.

## Confirmed state

### Completed

- **7 task modules** with deterministic keyword scoring (paper_comprehension,
  idea_generation, literature_synthesis, experimental_design, peer_review,
  reproduction, open_question_id). Each has `evaluate(model) -> (score, details)`.
- **CLI** (10 commands): `list`, `show`, `run`, `compare`, `tasks`, `sample`,
  `data`, `report`, `schema`, `verify`. Options: `--format text|json|html`,
  `--save`, `--verbose`, `--dry-run`, `--ignore`, `--benchmark`, `--quiet`,
  `--parallel`, `--save-responses`. Glob patterns in `--tasks`.
- **Core**: `Benchmark`, `BenchmarkResult`, `TaskResult`. `to_text()`/`to_json()`/
  `to_html()`/`to_format()`. `compare(models)`.
- **Tests**: 162 tests covering per-task scoring logic, CLI commands, report
  rendering, mock mode, error paths. Coverage: 88% (the ~12% gap is live-SDK
  branches that require API keys).
- **CI**: 3 jobs (test matrix Ubuntu/Windows x 3.9/3.11/3.13 with 80% coverage
  gate + ruff, mypy on 3.11, wheel build + clean-venv smoke test).
- **Docs**: TASK_DEFINITIONS.md, USAGE.md, CONTRIBUTING.md, RESEARCH.md,
  API.md, ROADMAP.md, FAQ.md, report-schema.json.
- **Examples**: evaluate_model.py, run_cli_demo.sh, run_cli_demo.ps1, README.md.
- **Packaging**: SPDX license, py.typed, minimal deps (click only), verified
  wheel build + install.
- **Repo hygiene**: .gitattributes, CHANGELOG, CODE_OF_CONDUCT, SECURITY,
  dependabot, pre-commit, issue/PR templates, .gitignore.

### In progress

- Project memory files (this handoff) are being initialized for the first time.

### Blocked

- Nothing blocked. The repo is in a known-good state.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `src/researchbench/` | All modules completed | Clean, committed |
| `tests/` | 162 tests | Clean, committed |
| `docs/` | 8+ documentation files | Clean, committed |
| `examples/` | 4 demo files | Clean, committed |
| `.github/workflows/ci.yml` | 3-job CI | Clean, committed |
| `pyproject.toml` | Full metadata, SPDX, minimal deps | Clean, committed |
| `.ai/` + memory files | First-time initialization | Just created, needs review |

## Verification evidence

| Check | Result | Executed at / artifact version | Basis / exit code | Evidence or command |
|---|---|---|---|---|---|
| `pytest tests` | PASS | 2026-08-21 | exit 0, 88.1% | `--cov --cov-fail-under=80` |
| `ruff check src tests` | PASS | 2026-08-21 | exit 0 | `ruff check` |
| `ruff format --check src tests` | PASS | 2026-08-21 | exit 0 | `ruff format --check` |
| `mypy src` | PASS | 2026-08-21 | exit 0 | `mypy src` |
| `pre-commit run --all-files` | PASS | 2026-08-21 | exit 0 | `pre-commit run --all-files` |
| `python -m build` | PASS | 2026-08-21 | exit 0 | sdist + wheel created |
| Fresh-venv wheel install + smoke | PASS | 2026-08-21 | exit 0 each | `--version`, `list`, `verify`, `run`, `compare`, `schema`, `tasks` |
| `python -m researchbench` | PASS | 2026-08-21 | exit 0 | `--version` shows 0.1.0 |

## Decisions referenced

- `docs/ROADMAP.md` lists proposed future directions (non-binding).
- The CAOShurong GitHub Sources program has a `D-20260820-030000-c018` decision
  authorizing the build of this benchmark. See
  `E:\Codex\Projects\caoshurong\github-sources-program\DECISIONS.md`.

## Risks and unknowns

- **No fabricated data.** All task data is from the initial scaffold; adding
  new items requires expert validation.
- **Known coverage gap.** The ~12% uncovered lines are the live SDK branches
  (openai/anthropic), which cannot be tested without API keys.
- **No independent adoption yet.** The repo has been built and polished but not
  published or promoted. This is the second decisive gap for the parent program.
- The `examples/demo.ipynb` was added by an external agent; its content has not
  been reviewed by this session.

## Next actions

1. Verify the documentation links in memory files (PROJECT_CONTEXT, HANDOFF)
   point to real paths.
2. Run `python .ai/project_memory.py check .` to validate memory integrity.
3. Continue with ROADMAP items or user-requested features.
4. Do NOT push to GitHub unless the user explicitly requests it.

## User decisions required

- Whether to continue with ROADMAP features (LLM-as-judge, expert data) or
  publish and promote the current version first.
- Whether to push committed changes to GitHub.