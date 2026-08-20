#!/usr/bin/env bash
# ResearchBench CLI demo: evaluate and compare models.
#
# Real evaluation requires an API key for the model backend:
#   export OPENAI_API_KEY=sk-...        # for --model gpt-*
#   export ANTHROPIC_API_KEY=sk-ant-... # for --model claude-*
# Without a key the pipeline runs in MOCK mode: scores are canned smoke-test
# answers and must NOT be reported as real model results.

set -euo pipefail

# Use the `researchbench` console script when available, otherwise fall back to
# `python -m researchbench.cli` (e.g. when the entry point is not on PATH).
if command -v researchbench >/dev/null 2>&1; then
  RB=(researchbench)
else
  RB=(python -m researchbench.cli)
fi

echo "==> 1. List all tasks"
"${RB[@]}" list

echo
echo "==> 2. Evaluate a single model (paper_comprehension + idea_generation), text report"
"${RB[@]}" run --model gpt-4o --tasks paper_comprehension,idea_generation

echo
echo "==> 3. Evaluate everything, JSON report to a file"
"${RB[@]}" run --model gpt-4o --tasks all --format json --save report.json
echo "    wrote report.json"

echo
echo "==> 4. Compare two models, text table"
"${RB[@]}" compare --model gpt-4o --model claude-3-opus --tasks all

echo
echo "==> 5. Compare two models, HTML report"
"${RB[@]}" compare --model gpt-4o --model claude-3-opus --tasks all --format html --save comparison.html
echo "    wrote comparison.html"

echo
echo "When OPENAI_API_KEY/ANTHROPIC_API_KEY are set, these same commands"
echo "evaluate real models instead of returning mock answers."