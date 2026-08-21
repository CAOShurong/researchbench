# Decision Log

This file is append-only. Supersede an entry explicitly rather than silently
rewriting history.

# Decisions

## D-20260821-093000-rb001

### Use deterministic keyword scoring, not LLM-as-judge, as the default
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The initial scaffold used keyword-based scoring. The RESEARCH.md proposed
LLM-as-judge as an alternative for open-ended tasks.

### Decision

Keep deterministic keyword scoring as the default (and only) mode for v0.1.0.
The scoring is reproducible, testable, and does not require API keys. LLM-as-
judge is deferred to ROADMAP as an optionally gated future feature.

### Consequences

- All 7 tasks have testable, deterministic scoring formulas documented in
  TASK_DEFINITIONS.md.
- Mock mode provides reliable smoke tests without API keys.
- LLM-as-judge remains a proposed feature, not a commitment.

## D-20260821-093001-rb002

### Drop unused runtime dependencies
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The initial pyproject.toml declared `pydantic`, `pyyaml`, `rich`, and `click`
as runtime dependencies. A full grep of the codebase (src, tests, examples)
found zero imports of `pydantic`, `pyyaml`, or `rich`.

### Decision

Remove the three unused dependencies. Keep only `click` as the runtime
dependency. `openai` and `anthropic` remain in the optional `[judge]` extra.

### Consequences

- Wheel declares only `click>=8.0` as a runtime dependency.
- A fresh venv installs only `click` + `researchbench`.
- All 162 tests pass against the installed wheel.
- Verified by `pip check` in the clean venv.

## D-20260821-093002-rb003

### Bundle report-schema.json inside the package
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

The `schema` command initially read the JSON Schema from `docs/`. This path
resolution failed when the package was installed from a wheel (no `docs/` in
site-packages).

### Decision

Move the schema file into `src/researchbench/report-schema.json` and add it to
`[tool.setuptools.package-data]`. The `schema` command reads from
`Path(__file__).parent / "report-schema.json"`.

### Consequences

- `researchbench schema --save <path>` works from an installed wheel.
- A copy remains at `docs/report-schema.json` for browser access.
- Verified: built wheel, installed in clean venv, schema command produces valid JSON.

## D-20260821-093003-rb004

### Use monkeypatching for --save-responses and --parallel instead of changing task module interface
- Status: accepted
- Date: 2026-08-21
- Deciders: build session
- Supersedes: none

### Context

Adding `--save-responses` (save raw model responses to disk) and `--parallel`
(concurrent task evaluation) would normally require changing the `evaluate()`
interface across all 7 task modules.

### Decision

- `--parallel`: uses `concurrent.futures.ThreadPoolExecutor` in the CLI's `run`
  command, calling `task.evaluate()` per task. No task module changes.
- `--save-responses`: monkeypatches each task module's `_call_model` at runtime
  via `setattr(mod, "_call_model", wrapper)`. The wrapper saves the response
  and delegates to the original. No task module changes.

### Consequences

- All 7 task modules remain unchanged.
- The features are opt-in CLI flags.
- Verified by tests (`test_run_parallel`, `test_run_save_responses`).