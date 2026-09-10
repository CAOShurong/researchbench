# Python API Reference

This document describes the public classes and methods in `researchbench`.
All public types are importable from the top-level package:

```python
from researchbench import Benchmark, BenchmarkResult, TaskResult
```

---

## `Benchmark`

The main entry point for running evaluations.

```python
class Benchmark(tasks: list[str] | None = None)
```

- **`tasks`** — list of task names to include, or `None` (all 8). Valid names:
  `paper_comprehension`, `idea_generation`, `literature_synthesis`,
  `experimental_design`, `peer_review`, `reproduction`, `open_question_id`,
  `heterogeneous_pilot`.

### `run(model, **kwargs) -> BenchmarkResult`

Evaluate every active task against the given model.

- **`model`** — a model identifier string (default `"gpt-4o"`). The task's
  `_call_model` decides, based on the prefix, whether to call the live
  `openai`/`anthropic` API or return a mock answer.
- **`capture_raw`** — store raw model text on each `TaskResult` (default True).
- **`parallel`** — run tasks concurrently (default False).
- **`benchmark`** — print per-task timing to stderr (default False).
- **`save_responses_dir`** — append raw responses under this directory.
- **`allow_draft`** — include draft-status dataset items (default False).
- **`**kwargs`** — forwarded to each task's `evaluate()` method.

Returns a `BenchmarkResult` with one `TaskResult` per task. Draft-only tasks
raise `ValueError` unless `allow_draft=True`.

### `compare(models, **kwargs) -> list[BenchmarkResult]`

Run the same task subset against each model in `models`.

- **`models`** — list of model identifier strings.
- **`**kwargs`** — passed through to `run()`.

Returns one `BenchmarkResult` per model, preserving input order.

### `available_tasks() -> list[str]` *(static)*

Return the canonical task ordering. Used internally by the CLI.

---

## `BenchmarkResult`

Holds the evaluation results for one model.

```python
@dataclass
class BenchmarkResult:
    results: list[TaskResult]   # one per task
    model: str                  # the model identifier
    timestamp: str = ""
    benchmark_version: str = ""
    run_config: dict = {}                   # allow_draft, parallel, etc.
```

### `average() -> float`

Simple mean of all task scores. Returns `0.0` when `results` is empty.

### `summary() -> str`

Short text report (alias for `to_text(verbose=False)`). Backward-compatible
with the initial v0.1.0 API.

### `to_text(verbose=False, quiet=False) -> str`

Human-readable report. When `verbose=True`, each task's `details` dict is
printed so you can inspect keyword coverage, flaw counts, etc. When
`quiet=True` the header banner is omitted.

### `to_json() -> str`

JSON document with the structure:

```json
{
  "model": "gpt-4o",
  "average": 56.72,
  "n_tasks": 8,
  "results": [
    {"task": "paper_comprehension", "score": 27.5, "details": {...}},
    ...
  ]
}
```

### `to_html() -> str`

Self-contained HTML page with a score table and expandable detail views for
each task. Inline CSS — no external assets.

### `to_format(fmt, verbose=False) -> str`

Dispatch to `to_text`, `to_json` or `to_html` based on `fmt` (`"text"`,
`"json"`, `"html"`). Unknown formats fall back to `to_text(verbose=False)`.

---

## `TaskResult`

```python
@dataclass
class TaskResult:
    task_name: str
    model: str
    score: float          # in [0, 100]
    details: dict         # task-specific breakdown (keys documented in
                          # TASK_DEFINITIONS.md)
    raw_output: str = ""
    duration_seconds: float = 0.0
    evaluator_version: str = ""
```

---

## Task classes

Each task module in `src/researchbench/tasks/` exposes a class with a single
public method:

```python
class PaperComprehension:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict]:
        ...
```

The same pattern holds for `IdeaGeneration`, `LiteratureSynthesis`,
`ExperimentalDesign`, `PeerReview`, `Reproduction`, `OpenQuestionId`, and
`HeterogeneousPilot` (rubric scorer, not keyword matching).

- **Return value**: `(score, details)` where `score` is a float in `[0, 100]`
  and `details` is a dict whose structure is documented per-task in
  [`docs/TASK_DEFINITIONS.md`](TASK_DEFINITIONS.md).
- **Mock mode**: when `model` starts with `"gpt"`/`"openai"` and no
  `OPENAI_API_KEY` is set, or contains `"claude"` and no `ANTHROPIC_API_KEY`
  is set, `_call_model` returns a canned answer. Any other model string also
  returns a mock. See [`docs/USAGE.md`](USAGE.md#evaluating-real-models).

---

## Convenience top-level functions

```python
from researchbench import __version__  # semantic version string
```

The `__init__.py` re-exports `Benchmark`, `BenchmarkResult`, and `TaskResult`.

---

## CLI module

The `researchbench` package also exposes a `click`-based CLI through
`researchbench.cli:main`. This is the entry point for both the `researchbench`
console script and `python -m researchbench`. See [`docs/USAGE.md`](USAGE.md)
for the command-line reference.

## RunRecord contract (RESEARCH_BENCHMARK.md ?6-7)

The `run-record` CLI command supports:
- `import --from <file>`: validate and load a RunRecord
- `validate --from <file>`: check mandatory fields
- `export --from <file> --save <out>`: validate and re-export

Subscription and API runs are separate conditions (cannot mix in one record).
