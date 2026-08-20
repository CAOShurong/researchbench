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
- CLI (`researchbench` / `python -m researchbench.cli`): `list`, `show`, `run`
  (with `--format text|json|html`, `--save PATH`, `--verbose`), and `compare`
  (multi-`--model`, text table / json / html).
- Documentation: `docs/TASK_DEFINITIONS.md`, `docs/USAGE.md`,
  `docs/CONTRIBUTING.md`, `docs/RESEARCH.md` (background research).
- Runnable examples in `examples/` (Python API + bash + PowerShell demos).
- 128 tests covering the shared task interface, per-task scoring formulas,
  report rendering, and the CLI; `ruff` (lint + format) and `mypy` clean.
- GitHub Actions CI: test matrix (Ubuntu/Windows x 3.9/3.11/3.13) with an 80%
  coverage gate, a `mypy` job, and a wheel build + clean-install smoke test.
- Packaging metadata: `[project.urls]`, SPDX `MIT` license expression, and a
  `py.typed` type marker.

[0.1.0]: https://github.com/CAOShurong/researchbench/releases/tag/v0.1.0