# Contributing to ResearchBench

Thanks for helping improve the AI academic/research capability benchmark.
Please read the task definitions in [TASK_DEFINITIONS.md](TASK_DEFINITIONS.md)
before changing behavior, and the research rationale in
[`RESEARCH.md`](https://github.com/CAOShurong/researchbench/blob/main/RESEARCH.md).

## Ground rules

- **No fabricated results.** Scores must always come from actually running the
  pipeline (mock mode is fine for tests, but it must be labeled mock).
- **Keep scores in `[0, 100]`** and keep the public `evaluate(model) ->
  (score, details)` interface stable.
- **Data provenance:** any new dataset must respect source licenses; synthetic
  items should be marked as such. Cite sources for real data.

## Setting up a development environment

```bash
git clone https://github.com/CAOShurong/researchbench
cd researchbench
python -m venv .venv
# Windows: .\.venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

The `dev` extra installs `pytest`, `pytest-cov`, `ruff`, and `mypy`.

## Running the checks

Everything must be green before submitting a PR.

```bash
ruff check src tests                    # lint
ruff format --check src tests           # formatting (run `ruff format` to fix)
mypy src                                # static types
pytest tests -v                         # test suite
pytest --cov=researchbench tests        # coverage (optional)
```

The GitHub Actions CI (`.github/workflows/ci.yml`) runs ruff check + format and
pytest on Ubuntu and Windows for Python 3.9, 3.11 and 3.13. It also verifies the
package installs with `pip install -e ".[dev]"`.

## Testing

- `tests/test_basic.py` asserts the shared task interface (evaluate returns
  `(score, details)`, scores in range, `Benchmark` wiring).
- `tests/test_<task>.py` files exercise each task's **scoring formula** with
  monkeypatched `_call_model` responses:
  - a *perfect* response (every reference keyword + required structure) scores
    exactly `100.0`;
  - an *empty* response hits the documented floor (see below);
  - partial responses land strictly between;
  - the mock fallback (no API key) returns a non-empty string and a score in range.
- `tests/test_core.py` and `tests/test_cli.py` cover report rendering, formats,
  `compare`, and CLI options/exit codes.

Baseline floors to keep tests correct:

| Task | Empty-response score | Why |
|---|---|---|
| `peer_review` | 6.0 | recommendation score floors at 0.3 |
| `reproduction` | 10.0 | diagnosis score floors at 0.5 |
| all others | 0.0 | no term contributes |

**Tip:** when patching `_call_model` in a loop, bind loop variables as lambda
defaults (`lambda model, prompt, w=word, r=resp: r`) to satisfy ruff's `B023`.

## Adding a new task

1. Create `src/researchbench/tasks/<your_task>.py` exposing a class with the
   exact signature:
   ```python
   class MyTask:
       def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict]:
   ```
   Mirror the `_call_model(model, prompt)` mock/live split used by existing tasks.
2. Register it in:
   - `src/researchbench/tasks/__init__.py` (re-export + `__all__`);
   - `src/researchbench/core.py` `Benchmark.__init__` and `available_tasks()`;
   - `src/researchbench/cli.py` `TASK_INFO` (description for `list`/`show`);
3. Document the exact scoring formula in `docs/TASK_DEFINITIONS.md` and update
   the task table in `README.md` and `docs/USAGE.md`.
4. Add `tests/test_<task>.py` with perfect/empty/partial fixture tests per the
   table above, and add the class to `ALL_TASK_CLASSES` if you extend the shared
   interface checks.
5. Run the full check set above.

## Pull request workflow

- Branch from `main`; keep the change focused and single-purpose.
- Commit with a descriptive message; conventional prefixes (`feat:`, `fix:`,
  `test:`, `docs:`, `style:`, `refactor:`) are welcome.
- Wait on the CI matrix; if a Python version fails, reproduce locally and fix
  before re-pushing.
- Reviewer-requested changes should be made on a new commit (or force-pushed to
  the feature branch only if already cleanly rebased and discussed).

## Reporting issues

Open an issue with a minimal reproduction. For a scoring concern, include the
`details` dict from `--verbose`/`--format json` and the model string you used
(mock vs. live matters).

## Code of conduct

Be respectful and constructive. This is a scientific benchmark: critiques of the
metrics belong in issues and reviews, and disagreements are resolved by evidence,
not volume.