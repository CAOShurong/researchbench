# Examples

Three working examples showing how to use ResearchBench, all runnable in **mock
mode** with no API key.

| File | What it shows |
|---|---|
| `evaluate_model.py` | The Python API: build a `Benchmark`, run one model, print verbose text + JSON. |
| `run_cli_demo.sh` | The `researchbench run` / `compare` / `list` CLI flow (bash). |
| `run_cli_demo.ps1` | The same CLI flow for Windows PowerShell. |

## Important: mock vs. real results

The task runners fall back to **canned answers** when no API key is present
(see `docs/USAGE.md` → *Evaluating real models*). The examples therefore
**never present mock scores as real model results** — `evaluate_model.py`
prints a warning banner when it is in mock mode, and the CLI demos similarly
point it out in their output.

### Run everything in mock mode (smoke test the pipeline)

```bash
bash examples/run_cli_demo.sh     # macOS/Linux
# or, Windows PowerShell
powershell -ExecutionPolicy Bypass -File examples/run_cli_demo.ps1

python examples/evaluate_model.py --model gpt-4o
```

### Evaluate a real model

```bash
export OPENAI_API_KEY=sk-...                      # bash
# PowerShell: $env:OPENAI_API_KEY = "sk-..."
pip install "researchbench[judge]"                # openai + anthropic clients

python examples/evaluate_model.py --model gpt-4o
researchbench run --model gpt-4o --format json --save results.json
researchbench compare --model gpt-4o --model claude-3-5-sonnet-latest --tasks all
```

CLI equivalents of `evaluate_model.py` above can be invoked with
`python -m researchbench.cli ...` if the `researchbench` entry point is not on
your `PATH`.