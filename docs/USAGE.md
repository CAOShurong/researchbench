# Usage Guide

ResearchBench evaluates an AI model's academic and research capabilities across
8 tasks (7 keyword-matching placeholders plus the BEOL `heterogeneous_pilot`).
This guide covers the CLI, the Python API, report formats, and how to evaluate
a real model. Scores are not a validated benchmark.

## Installation

```bash
# From PyPI (once published)
pip install researchbench

# From a local checkout (editable, for development)
pip install -e .

# LLM-as-judge/real-model extras are NOT required to run the CLI.
```

Runtime dependency: `click`. To call real
models you also need `openai` and/or `anthropic` (see
[Evaluating real models](#evaluating-real-models)).

## Quick start

```bash
researchbench list                          # list the 8 tasks
researchbench run --tasks heterogeneous_pilot --model gpt-4o
researchbench run --model gpt-4o --allow-draft   # include draft items
researchbench run --tasks idea_generation,peer_review --model claude-3-opus
researchbench compare --model gpt-4o --model claude-3-opus --tasks all --allow-draft
researchbench verify                        # mock-mode health check (includes drafts)
```

## Command reference

### `researchbench list`

Prints the task names and one-line descriptions.

### `researchbench show TASK`

Prints a task's description and the size of its built-in dataset.

### `researchbench run`

Run the suite (or a subset) against **one** model.

| Option | Default | Description |
|---|---|---|
| `--tasks` | `all` | Comma-separated names, fnmatch globs (`paper_*`), or `all`. |
| `--ignore` | empty | Comma-separated task names to exclude. |
| `--model` | `gpt-4o` | Model identifier. See mock-mode rules below. |
| `--format` | `text` | Report format: `text`, `json`, or `html`. |
| `--save PATH` | — | Write the report to a file instead of stdout. |
| `--verbose` | off | Include per-task `details` breakdown in text reports. |
| `--dry-run` | off | Print selected tasks and dataset sizes; do not evaluate. |
| `--benchmark` | off | Print per-task timing to stderr. |
| `--quiet` | off | Suppress the text-report banner. |
| `--parallel` | off | Run tasks concurrently. |
| `--save-responses DIR` | — | Append raw model responses (`<dir>/<task>.txt`). |
| `--allow-draft` | off | Include draft-status dataset items (e.g. q6). |

Default `run` skips draft items. Mixed tasks still run; a task with **only**
draft items is rejected unless `--allow-draft`.

```bash
# JSON report (machine-readable), printed to stdout
researchbench run --tasks all --model gpt-4o --format json

# Include draft items such as heterogeneous_pilot q6
researchbench run --tasks all --model gpt-4o --allow-draft --format json

# HTML report, saved to disk
researchbench run --tasks all --model gpt-4o --format html --save report.html

# Verbose text with per-task detail dicts
researchbench run --tasks all --model gpt-4o --verbose
```

### `researchbench compare`

Run the same task subset against **multiple** models. `--model` is repeatable
and required unless `--dry-run`. Also accepts `--tasks`, `--ignore`,
`--format`, `--save`, `--verbose`, `--dry-run`, and `--allow-draft`.

```bash
researchbench compare --model gpt-4o --model claude-3-opus --tasks all --allow-draft
researchbench compare --model gpt-4o --model gpt-4o-mini --format json --save cmp.json
researchbench compare --model gpt-4o --model claude-3-opus --format html --save cmp.html
researchbench compare --tasks all --dry-run
```

`--format text` renders a per-task score table plus an AVERAGE row. `--format
html` renders the same as a table page. `--format json` emits
`{tasks, models, results: [{model, average, per_task}]}`.

### `researchbench tasks`

List tasks with dataset sizes. `--format text|json`. `--save PATH` writes the
output.

### `researchbench sample TASK`

Print the first prompt in a task dataset. `--format text|json`.

### `researchbench data TASK`

Export a task dataset. `--format text|json`, `--save PATH`, `--validate`
(pilot `DatasetItem` schema; rejects invalid items).

### `researchbench report --from FILE`

Re-render a saved JSON results file as `--format text|json|html`. `--save PATH`,
`--verbose`.

### `researchbench schema`

Print the JSON Schema for the run report. `--save PATH` writes it to a file.

### `researchbench verify`

Mock-mode health check of all 8 tasks (includes draft items). Exit 0 if every
score is in `[0, 100]`.

### `researchbench run-record {import|export|validate}`

Import, re-export, or validate a subscription/API `RunRecord` JSON file.

```bash
researchbench run-record validate --from record.json
researchbench run-record import --from record.json --save out.json
researchbench run-record export --from record.json --save out.json
```

`--from` is required for all three actions. Invalid records exit 1.

### Exit codes

- `0` — success.
- `2` — CLI usage error (e.g. unknown task name, invalid format).

## Report formats

- **text**: human-readable, stable for diffs. With `--verbose`, appends each
  task's scoring `details` dict.
- **json**: `{model, average, n_tasks, results: [{task, score, details}]}`.
- **html**: self-contained report (inline CSS) with a score table and an
  expandable `details` node per task. Suitable for CI artifacts or sharing.

## Python API

```python
from researchbench import Benchmark

bench = Benchmark()                         # all 8 tasks
subset = Benchmark(tasks=["paper_comprehension", "reproduction"])

result = bench.run(model="gpt-4o")          # skips draft items
result = bench.run(model="gpt-4o", allow_draft=True)
result.average()                            # aggregate score
result.summary()                            # short text
result.to_json()                            # JSON string
result.to_html()                            # HTML string
result.to_text(verbose=True)                # verbose text

# Compare several models in one call
results = bench.compare(models=["gpt-4o", "claude-3-opus"])
for r in results:
    print(r.model, r.average())
```

## Evaluating real models

Every task's `_call_model` decides between a **mock path** and a **live path**:

- Model string starts with `gpt` or `openai` → lives OpenAI Chat Completions via
  `OPENAI_API_KEY`.
- Model string contains `claude` → live Anthropic Messages via
  `ANTHROPIC_API_KEY`.
- Any other model string → always the generic mock answer.

So:

```bash
# Mock mode: no API key required, deterministic; use only as a smoke test
researchbench run --model gpt-4o

# Real evaluation: set the key first
export OPENAI_API_KEY=sk-...
researchbench run --model gpt-4o --format json --save results.json

export ANTHROPIC_API_KEY=sk-ant-...
researchbench run --model claude-3-5-sonnet-latest
```

> **Do not treat mock-mode scores as real evaluations.** They are canned answers
> used to verify the pipeline. Always set an API key (and an extra `[judge]`
> package install) before reporting numbers for a model.

## Data and licensing

Built-in task data is small and synthetic or licensed per source (arXiv,
OpenReview, PapersWithCode style references are cited in `RESEARCH.md`).
ResearchBench is MIT-licensed; any third-party data keeps its own license. See
`LICENSE` and `RESEARCH.md`.

## Troubleshooting

- `Error: No such command 'cmp'` — the command is `compare`.
- `Unknown task` — run `researchbench list` for valid names; unknown names make
  the CLI exit with code 2.
- `OpenAIError`/`AuthenticationError` — the key is missing/invalid or `openai` is
  not installed; install the `[judge]` extra.
- Scores of exactly `6.0`/`10.0` on `peer_review`/`reproduction` — expected when
  the response contains no recommendation/diagnosis signal; see
  [TASK_DEFINITIONS.md](TASK_DEFINITIONS.md).