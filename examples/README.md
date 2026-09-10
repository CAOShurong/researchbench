# Examples

Runnable demos. All work in **mock mode** with no API key.

| File | What you click |
|---|---|
| `demo.ipynb` | Binder / Jupyter: `heterogeneous_pilot` in 30 seconds |
| `evaluate_model.py` | Python API: same BEOL pilot |
| `run_cli_demo.sh` | CLI flow (bash) |
| `run_cli_demo.ps1` | CLI flow (Windows PowerShell) |

## Mock vs real

Without `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`, answers are canned. Scores are a
smoke test, not a model ranking.

```bash
# 30-second demo (same command as the README)
researchbench run --tasks heterogeneous_pilot --model gpt-4o

python examples/evaluate_model.py --model gpt-4o
bash examples/run_cli_demo.sh
# Windows:
powershell -ExecutionPolicy Bypass -File examples/run_cli_demo.ps1
```

The other seven tasks are keyword-matching placeholders. They need
`--allow-draft` and must not be quoted as model quality.
