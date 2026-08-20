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

- **`tasks`** — list of task names to include, or `None` (all 7). Valid names:
  `paper_comprehension`, `idea_generation`, `literature_synthesis`,
  `experimental_design`, `peer_review`, `reproduction`, `open_question_id`.

### `run(model, **kwargs) -> BenchmarkResult`

Evaluate every active task against the given model.

- **`model`** — a model identifier string (default `"gpt-4o"`). The task's
  `_call_model` decides, based on the prefix, whether to call the live
  `openai`/`anthropic` API or return a mock answer.
- **`**kwargs`** — forwarded to each task's `evaluate()` method for future
  extension (currently unused by the built-in tasks).

Returns a `BenchmarkResult` with one `TaskResult` per task.

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
```

### `average() -> float`

Simple mean of all task scores. Returns `0.0` when `results` is empty.

### `summary() -> str`

Short text report (alias for `to_text(verbose=False)`). Backward-compatible
with the initial v0.1.0 API.

### `to_text(verbose=False) -> str`

Human-readable report. When `verbose=True`, each task's `details` dict is
printed so you can inspect keyword coverage, flaw counts, etc.

### `to_json() -> str`

JSON document with the structure:

```json
{
  "model": "gpt-4o",
  "average": 56.72,
  "n_tasks": 7,
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
    raw_output: str = ""  # reserved for future use (not yet populated)
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
`ExperimentalDesign`, `PeerReview`, `Reproduction`, and `OpenQuestionId`.

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