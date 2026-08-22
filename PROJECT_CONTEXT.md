---
schema_version: portable-project-memory/v1
project_name: "ResearchBench"
updated_at: "2026-08-21T09:45:00+08:00"
---

# Project Context

## Objective

Build `researchbench`, an open-source benchmark for measuring AI academic and
research capabilities. **The authoritative design document is
`RESEARCH_BENCHMARK.md`** — read it before any benchmark work. The benchmark
answers: *"Which AI system is genuinely the better research assistant, in what
research abilities, under what conditions, and how do we know?"*

The current v0.1.0 implementation uses keyword-matching scoring as a
**placeholder**. It is not scientifically valid and must be replaced per the
roadmap in RESEARCH_BENCHMARK.md Section 11.

## Deliverables

- A pip-installable Python package (`researchbench`) with 7 task modules,
  deterministic keyword-based scoring, and a CLI.
- 160+ tests with 88% coverage, CI (ruff, mypy, pytest with coverage gate,
  wheel build + clean-install smoke test).
- Full documentation: task definitions, usage guide, contributing guide, API
  reference, FAQ, roadmap, JSON report schema.
- Runnable CLI/Python API examples in mock mode (no API key required).
- Packaging: wheel builds, SPDX license, py.typed type marker, minimal deps.

## Scope and non-goals

### In scope

- Deterministic keyword-scoring for all 7 tasks (scores in [0, 100]).
- CLI commands: `list`, `show`, `run`, `compare`, `tasks`, `sample`, `data`,
  `report`, `schema`, `verify`.
- Report formats: `text`, `json`, `html`.
- Mock mode (no API key) for smoke testing the pipeline.
- Real-model evaluation via OpenAI / Anthropic SDKs (optional `[judge]` extra).
- Cross-platform support (Windows + Ubuntu CI matrix for Python 3.9, 3.11, 3.13).

### Out of scope

- LLM-as-judge scoring mode (proposed in ROADMAP, not yet implemented).
- Expert-validated task data (requires domain expert review).
- Cross-lingual / domain-specific task packs.
- Public leaderboard hosting.
- Real-model evaluation results (must be produced by the user with their own API key).

## Project map

| Path or component | Purpose | Source of truth |
|---|---|---|
| `src/researchbench/` | Package source | The code |
| `src/researchbench/tasks/` | 7 task modules (PaperComprehension, IdeaGeneration, etc.) | TASK_DEFINITIONS.md + code |
| `src/researchbench/core.py` | Benchmark runner, BenchmarkResult, TaskResult | The code |
| `src/researchbench/cli.py` | Click-based CLI (10 commands) | The code |
| `tests/` | 260 tests (task scoring, CLI, core, report rendering) | test files |
| `docs/` | Documentation (8 files) | docs/ |
| `examples/` | Runnable demos | examples/ |
| `.github/workflows/ci.yml` | CI: test matrix, typecheck, build | ci.yml |
| `pyproject.toml` | Package metadata, build config | pyproject.toml |

## Commands and verification

| Purpose | Command or method | Expected result |
|---|---|---|
| Full test suite | `pytest tests -v` | 260 passed |
| With coverage gate | `pytest tests --cov=researchbench --cov-fail-under=80` | 88%+ coverage |
| Lint | `ruff check src tests` | All checks passed |
| Format | `ruff format --check src tests` | 22 files already formatted |
| Type check | `mypy src` | Success, no issues in 12 files |
| Pre-commit | `pre-commit run --all-files` | All hooks passed |
| Build wheel | `python -m build` | sdist + wheel created |
| Install + smoke | `pip install dist/*.whl && researchbench --version` | version 0.1.0 |
| CLI list | `researchbench list` | 7 tasks listed |
| Verify | `researchbench verify` | All 7 PASS |

## Constraints

- Python >= 3.9 required.
- Only `click` is a runtime dependency; `openai` and `anthropic` are optional.
- No fabricated data or evaluation results. Mock mode must be clearly labeled.
- All work is in `E:\Codex\Projects\caoshurong\researchbench`.
- No pushing to GitHub until the user explicitly requests it.
- The CAOShurong GitHub Sources program memory files
  (`E:\Codex\Projects\caoshurong\github-sources-program\`) must not be modified.

## Data and provenance

- Task data is built-in (small, synthetic, or derived from public sources).
- See `docs/RESEARCH.md` for the background research and gap analysis.
- See `docs/report-schema.json` for the JSON report format schema.

## Runtime and capability dependencies

- Python 3.9+ with `click`.
- For real-model evaluation: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` + `[judge]` extra.
- Windows PowerShell 5.1+ or bash for the demo scripts.
- `ruff`, `mypy`, `pytest`, `pytest-cov` for development (dev extra).

## Definition of done

- All 260 tests pass (`pytest tests -v`).
- `ruff check` and `ruff format --check` pass.
- `mypy src` passes.
- Wheel builds and installs in a clean venv.
- `researchbench list` and `researchbench verify` work from the installed wheel.

## Glossary

| Term | Meaning |
|---|---|
| ResearchBench | The benchmark suite itself |
| Mock mode | Running without API key → canned answers for smoke testing |
| Deterministic scoring | Same input → same score (keyword matching, no randomness) |
| CAOShurong program | The parent GitHub Sources program for the OpenAI Codex application |
| [judge] extra | Optional pip install of openai + anthropic SDKs |