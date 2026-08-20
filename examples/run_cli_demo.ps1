# ResearchBench CLI demo (Windows PowerShell).
#
# Real evaluation requires an API key for the model backend:
#   $env:OPENAI_API_KEY = "sk-..."        # for --model gpt-*
#   $env:ANTHROPIC_API_KEY = "sk-ant-..." # for --model claude-*
# Without a key the pipeline runs in MOCK mode: scores are canned smoke-test
# answers and must NOT be reported as real model results.

# Use the `researchbench` console script when available, otherwise fall back to
# `python -m researchbench.cli` (e.g. when the entry point is not on PATH).
if (Get-Command researchbench -ErrorAction SilentlyContinue) {
    $RB = "researchbench"
} else {
    $RB = "python -m researchbench.cli"
}

Write-Host "==> 1. List all tasks"
Invoke-Expression "$RB list"

Write-Host ""
Write-Host "==> 2. Evaluate a single model (paper_comprehension + idea_generation), text report"
Invoke-Expression "$RB run --model gpt-4o --tasks paper_comprehension,idea_generation"

Write-Host ""
Write-Host "==> 3. Evaluate everything, JSON report to a file"
Invoke-Expression "$RB run --model gpt-4o --tasks all --format json --save report.json"
Write-Host "    wrote report.json"

Write-Host ""
Write-Host "==> 4. Compare two models, text table"
Invoke-Expression "$RB compare --model gpt-4o --model claude-3-opus --tasks all"

Write-Host ""
Write-Host "==> 5. Compare two models, HTML report"
Invoke-Expression "$RB compare --model gpt-4o --model claude-3-opus --tasks all --format html --save comparison.html"
Write-Host "    wrote comparison.html"

Write-Host ""
Write-Host "When OPENAI_API_KEY/ANTHROPIC_API_KEY are set, these same commands"
Write-Host "evaluate real models instead of returning mock answers."