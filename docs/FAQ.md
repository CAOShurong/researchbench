# Frequently Asked Questions

## What is ResearchBench?

A benchmarking suite that measures AI models on 7 academic and research
capabilities: paper comprehension, idea generation, literature synthesis,
experimental design, peer review, reproduction diagnosis, and open question
identification. See [`docs/TASK_DEFINITIONS.md`](TASK_DEFINITIONS.md).

## Do I need an API key to use it?

No. Running without `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` triggers **mock
mode**: every task returns a canned answer that produces a deterministic score.
This is useful for smoke-testing the pipeline, but **mock scores are not real
model evaluations**. Set the appropriate API key to get real results.

## What models are supported?

Any model string that starts with `gpt`/`openai` (uses the OpenAI SDK) or
contains `claude` (uses the Anthropic SDK). Anything else returns the generic
mock. You need the `[judge]` extra (`pip install researchbench[judge]`) to
install the SDKs.

## What do the scores mean?

Each task returns a float in `[0, 100]`. The exact formula depends on the task
 — keyword coverage, number of flaws detected, section completeness, etc. See
[`docs/TASK_DEFINITIONS.md`](TASK_DEFINITIONS.md) for the exact weights and
caps. Scores are **deterministic**: re-running the same model produces the same
scores (mock → same mock, real → depends on model output).

## Why do some tasks return 6.0 or 10.0 for an empty answer?

The `peer_review` task has a recommendation score that floors at 0.3
(contributing 6.0 points); `reproduction` has a diagnosis score that floors at
0.5 (contributing 10.0 points). All other tasks return 0.0 for an empty
response. This is documented in the scoring formulas.

## How do I compare multiple models?

```bash
researchbench compare --model gpt-4o --model claude-3-opus --tasks all
```

Use `--format html --save cmp.html` for a self-contained comparison page, or
`--format json` for machine-readable output.

## Can I run only a subset of tasks?

```bash
researchbench run --tasks paper_comprehension,idea_generation --model gpt-4o
researchbench run --tasks "paper_*" --model gpt-4o           # glob patterns
researchbench run --tasks all --ignore peer_review --model gpt-4o
```

## The scores seem low — is that normal?

Mock-mode scores are deliberately low (the canned answers are short and only
match a fraction of keywords). Real-model scores will differ. The benchmark is
designed to be discriminative, not to produce high absolute numbers.

## Can I use the benchmark data in my own tool?

Yes. The MIT license covers the code; the bundled task data is small and
synthetic or licensed per source (arXiv, OpenReview-style references). Use
`researchbench data <task_name> --format json` to export a task's dataset.

## How do I report a bug or request a feature?

Open an issue via the templates in `.github/ISSUE_TEMPLATE/`. For security
issues, see `SECURITY.md`.

## Can I contribute a new task?

Yes. See [`docs/CONTRIBUTING.md`](CONTRIBUTING.md) for the checklist and
interface requirements. The key steps: create a class with `evaluate(model) ->
(score, details)`, register it in the task registry, add tests, and document
the scoring formula.

## How is this different from MMLU, SWE-bench, GPQA…?

See [`docs/RESEARCH.md`](RESEARCH.md) for a full landscape analysis. The short
answer: those benchmarks measure knowledge, coding, or exam skills, not
academic research capabilities (paper critique, idea generation, literature
synthesis, experimental design, peer review, reproduction, open question
identification). ResearchBench is the first to target this gap.

## Why is the runtime dependency only `click`?

The built-in tasks use only the Python standard library to evaluate responses
(keyword matching, substring search). The `openai` and `anthropic` SDKs are
optional (`[judge]` extra) because they are only needed to call real models.
The `pydantic`, `pyyaml`, and `rich` dependencies were present in the initial
scaffold but unused — they were removed to keep the footprint minimal.

## What is the coverage gap in the test suite?

The ~12% uncovered lines are the live `openai`/`anthropic` SDK calls inside
each task's `_call_model`. These branches cannot run in CI without API keys.
The mock path, the CLI, the scoring logic, and all report rendering are fully
covered.