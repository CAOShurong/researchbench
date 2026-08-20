# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-20

### Added

- Benchmark for evaluating AI academic and research capabilities with 7 task
  categories: paper comprehension, idea generation, literature synthesis,
  experimental design, peer review, reproduction, and open question
  identification (`src/researchbench/tasks/`).
- Deterministic reference-keyword scoring for every task; scores are floats in
  `[0, 100]`, with per-task detail dicts (see `docs/TASK_DEFINITIONS.md`).
- Mock mode: running without `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` returns
  canned answers for smoke testing only (never real model results).
- `Benchmark` runner with task selection, `compute`-free honest scores,
  `compare(models)` for multi-model runs, and `available_tasks()`.
- `BenchmarkResult` report rendering: `summary()` / `to_text(verbose)` /
  `to_json()` / `to_html()` / `to_format()`.
- CLI (`researchbench` / `python -m researchbench.cli` **and** `python -m
  researchbench`): `list`, `show`, `run` (with `--format text|json|html`,
  `--save PATH`, `--verbose`, `--dry-run`, `--ignore`, `--benchmark`),
  `compare` (multi-`--model`, text table / json / html, `--dry-run` without
  requiring `--model`, `--ignore`), `report` (re-render saved JSON results),
  `tasks --format json` (machine-readable registry with dataset sizes),
  `sample <task_name>`, `data <task_name> --format json` (export dataset),
  `schema` (JSON Schema for the report format), and `verify` (mock-mode
  health check). `--tasks` supports fnmatch glob patterns (`paper_*`).
  `--save` reports a friendly error when the target cannot be written.
- Documentation: `docs/TASK_DEFINITIONS.md`, `docs/USAGE.md`,
  `docs/CONTRIBUTING.md`, `docs/RESEARCH.md` (background research),
  `docs/API.md` (Python API reference), `docs/ROADMAP.md` (proposed
  direction), and `docs/report-schema.json` (JSON Schema for the report
  format).
- Runnable examples in `examples/` (Python API + bash + PowerShell demos).
- 128 tests covering the shared task interface, per-task scoring formulas,
  report rendering, and the CLI; `ruff` (lint + format) and `mypy` clean.
- GitHub Actions CI: test matrix (Ubuntu/Windows x 3.9/3.11/3.13) with an 80%
  coverage gate, a `mypy` job, and a wheel build + clean-install smoke test;
  deprecation warnings fail the suite.
- Packaging metadata: `[project.urls]`, SPDX `MIT` license expression, a
  `py.typed` type marker, and a minimal runtime dependency set (`click` only).
- Repository hygiene: `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`,
  `CHANGELOG`, `docs/ROADMAP.md`, `pre-commit`, Dependabot, and issue/PR
  templates.

[0.1.0]: https://github.com/CAOShurong/researchbench/releases/tag/v0.1.0