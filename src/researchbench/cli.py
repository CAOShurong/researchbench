"""ResearchBench CLI - run, list, show, and compare benchmark evaluations."""

from __future__ import annotations

import fnmatch
import json

import click

from researchbench import Benchmark
from researchbench.core import BenchmarkResult
from researchbench.tasks import (
    ExperimentalDesign,
    IdeaGeneration,
    LiteratureSynthesis,
    OpenQuestionId,
    PaperComprehension,
    PeerReview,
    Reproduction,
)

TASK_INFO = {
    "paper_comprehension": {
        "class": PaperComprehension,
        "desc": "Test deep understanding of research papers, methodology critique, "
        "and limitation identification.",
    },
    "idea_generation": {
        "class": IdeaGeneration,
        "desc": "Test ability to generate novel research hypotheses from gap analysis.",
    },
    "literature_synthesis": {
        "class": LiteratureSynthesis,
        "desc": "Test ability to synthesize multiple papers and identify trends.",
    },
    "experimental_design": {
        "class": ExperimentalDesign,
        "desc": "Test ability to design valid experiments with controls and statistics.",
    },
    "peer_review": {
        "class": PeerReview,
        "desc": "Test ability to provide constructive, technically sound peer review.",
    },
    "reproduction": {
        "class": Reproduction,
        "desc": "Test ability to diagnose and fix reproduction failures.",
    },
    "open_question_id": {
        "class": OpenQuestionId,
        "desc": "Test ability to identify important open research questions.",
    },
}

FORMATS = ["text", "json", "html"]

# Mapping from task name to a nested-data path for extracting the first prompt.
# The first element is the module-level attribute name; subsequent elements are
# keys / indices to traverse: e.g. PAPERS[0]["questions"][0]["q"].
_TASK_SAMPLE_PATH: dict[str, tuple[str | int, ...]] = {
    "paper_comprehension": ("PAPERS", "questions", 0, "q"),
    "idea_generation": ("CONTEXTS", "question"),
    "literature_synthesis": ("SYNTHESIS_SETS", "question"),
    "experimental_design": ("HYPOTHESES", "question"),
    "peer_review": ("MOCK_SUBMISSIONS", "question"),
    "reproduction": ("SCENARIOS", "question"),
    "open_question_id": ("PAPER_SETS", "question"),
}


def _resolve_tasks(tasks: str, ignore: str = "") -> list[str]:
    if tasks == "all":
        selected = list(TASK_INFO.keys())
    else:
        raw = [t.strip() for t in tasks.split(",") if t.strip()]
        selected = []
        for pattern in raw:
            matched = fnmatch.filter(TASK_INFO.keys(), pattern)
            if not matched:
                raise click.BadParameter(
                    f"Unknown task(s): '{pattern}' does not match any task. "
                    f"Available: {', '.join(TASK_INFO.keys())}"
                )
            selected.extend(matched)
    if ignore:
        excluded = [t.strip() for t in ignore.split(",") if t.strip()]
        unknown_ex = [t for t in excluded if t not in TASK_INFO]
        if unknown_ex:
            raise click.BadParameter(f"Unknown task(s) in --ignore: {', '.join(unknown_ex)}")
        selected = [t for t in selected if t not in excluded]
    return selected


def _get_task_data(task_name: str) -> tuple[list | None, int]:
    """Return ``(data_list, len)`` for the given task's dataset."""
    path = _TASK_SAMPLE_PATH.get(task_name)
    if not path:
        return None, 0
    attr = path[0]
    assert isinstance(attr, str), "First element of sample path must be a str"
    import importlib

    mod = importlib.import_module(f"researchbench.tasks.{task_name}")
    data = getattr(mod, attr, None)
    if data is None:
        return None, 0
    return data, len(data)


def _emit(report: str, fmt: str, save_path: str | None) -> None:
    """Print the report, or write it to ``save_path``."""
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
        except OSError as exc:
            raise click.FileError(save_path, hint=str(exc)) from exc
        click.echo(f"Report saved to {save_path} ({fmt})")
    else:
        click.echo(report)


@click.group()
@click.version_option(package_name="researchbench", prog_name="researchbench")
def main() -> None:
    """ResearchBench: a benchmark for AI academic and research capabilities."""


@main.command("list")
def list_cmd() -> None:
    """List all available tasks."""
    click.echo("ResearchBench Tasks:")
    click.echo("=" * 70)
    for name, info in TASK_INFO.items():
        click.echo(f"  {name:25s} {info['desc']}")


@main.command()
@click.argument("task_name")
def show(task_name: str) -> None:
    """Show a task's description and dataset size."""
    if task_name not in TASK_INFO:
        click.echo(f"Unknown task: {task_name}")
        click.echo("Available: " + ", ".join(TASK_INFO.keys()))
        return
    info = TASK_INFO[task_name]
    click.echo(f"Task: {task_name}")
    click.echo(f"Description: {info['desc']}")
    path = _TASK_SAMPLE_PATH.get(task_name)
    if path:
        assert isinstance(path[0], str)
        attr = path[0]
        _, size = _get_task_data(task_name)
        if size > 0:
            click.echo(f"\nDataset ({attr}): {size} item(s)")


@main.command()
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format.",
)
@click.option("--save", "save_path", default=None, help="Write to file.")
def tasks(fmt: str, save_path: str | None) -> None:
    """List available tasks with metadata (dataset size, prompt key)."""
    entries = []
    for name, info in TASK_INFO.items():
        _, dataset_size = _get_task_data(name)
        entries.append({"name": name, "description": info["desc"], "dataset_size": dataset_size})

    if fmt == "json":
        import json

        _emit(json.dumps(entries, indent=2), fmt, save_path)
        return

    click.echo("ResearchBench Tasks:")
    click.echo("=" * 70)
    for e in entries:
        click.echo(f"  {e['name']:25s} {e['description']}")
        click.echo(f"  {'':25s} dataset: {e['dataset_size']} item(s)")


@main.command()
@click.argument("task_name")
@click.option(
    "--format", "fmt", type=click.Choice(["text", "json"], case_sensitive=False), default="text"
)
def sample(task_name: str, fmt: str) -> None:
    """Show the first prompt in a task's dataset."""
    if task_name not in TASK_INFO:
        click.echo(f"Unknown task: {task_name}")
        click.echo("Available: " + ", ".join(TASK_INFO.keys()))
        return
    path = _TASK_SAMPLE_PATH.get(task_name)
    if not path:
        click.echo(f"No dataset attribute mapping for {task_name}")
        return
    import importlib

    mod = importlib.import_module(f"researchbench.tasks.{task_name}")
    assert isinstance(path[0], str)
    attr = path[0]
    data = getattr(mod, attr, None)
    if not data:
        click.echo(f"No dataset found for {task_name}")
        return
    # Walk the nested path to extract the first prompt from the first item.
    obj = data[0]
    for key in path[1:]:
        if isinstance(key, int):
            obj = obj[key]
        else:
            obj = obj.get(key, "")
    prompt = str(obj) if isinstance(obj, str) else ""
    if fmt == "json":
        import json

        click.echo(json.dumps({"task": task_name, "sample": prompt}, indent=2))
    else:
        click.echo(f"Sample prompt for {task_name}:\n")
        for line in prompt.split("\n"):
            click.echo(f"  {line}")


def _show_dry_run(task_list: list[str]) -> None:
    """Print tasks and item counts without evaluating."""
    click.echo(f"Dry run: {len(task_list)} task(s) selected")
    click.echo("=" * 50)
    for name in task_list:
        _, size = _get_task_data(name)
        click.echo(f"  {name:25s} {size} item(s)")


@main.command()
@click.option("--tasks", default="all", help="Comma-separated task names or 'all'.")
@click.option("--ignore", default="", help="Comma-separated task names to exclude from --tasks.")
@click.option("--model", default="gpt-4o", help="Model to evaluate.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="text",
    help="Report format.",
)
@click.option("--save", "save_path", default=None, help="Write the report to this file path.")
@click.option("--verbose", is_flag=True, default=False, help="Show per-task detail breakdown.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show tasks and data sizes without evaluating."
)
@click.option("--benchmark", is_flag=True, default=False, help="Print per-task timing (stderr).")
def run(
    tasks: str,
    ignore: str,
    model: str,
    fmt: str,
    save_path: str | None,
    verbose: bool,
    dry_run: bool,
    benchmark: bool,
) -> None:
    """Run the benchmark against a single model."""
    task_list = _resolve_tasks(tasks, ignore=ignore)
    if dry_run:
        _show_dry_run(task_list)
        return
    import time

    from researchbench.core import TaskResult

    bench = Benchmark(tasks=task_list)
    result = BenchmarkResult(model=model)
    for name, task in bench.tasks.items():
        t0 = time.perf_counter()
        score, details = task.evaluate(model=model)
        elapsed = time.perf_counter() - t0
        result.results.append(TaskResult(task_name=name, model=model, score=score, details=details))
        if benchmark:
            click.echo(f"  [{name}] {elapsed:.3f}s", err=True)
    _emit(result.to_format(fmt, verbose=verbose), fmt, save_path)


@main.command()
@click.option(
    "--model",
    "models",
    multiple=True,
    required=False,
    help="Model to evaluate (repeatable, e.g. --model gpt-4o --model claude-3-opus).",
)
@click.option("--tasks", default="all", help="Comma-separated task names or 'all'.")
@click.option("--ignore", default="", help="Comma-separated task names to exclude from --tasks.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="text",
    help="Report format (text shows a comparison table).",
)
@click.option("--save", "save_path", default=None, help="Write the report to this file path.")
@click.option(
    "--verbose", is_flag=True, default=False, help="Show per-task detail breakdown per model."
)
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show tasks and data sizes without evaluating."
)
def compare(
    models: tuple[str, ...],
    tasks: str,
    ignore: str,
    fmt: str,
    save_path: str | None,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Compare multiple models on the same tasks."""
    task_list = _resolve_tasks(tasks, ignore=ignore)
    if dry_run:
        _show_dry_run(task_list)
        return
    if not models:
        raise click.BadParameter("At least one --model is required unless --dry-run is used.")
    bench = Benchmark(tasks=task_list)
    results = bench.compare(models=list(models))

    if fmt == "json":
        payload = {
            "tasks": task_list,
            "models": [r.model for r in results],
            "results": [
                {
                    "model": r.model,
                    "average": round(r.average(), 4),
                    "per_task": {x.task_name: x.score for x in r.results},
                }
                for r in results
            ],
        }
        _emit(json.dumps(payload, indent=2), fmt, save_path)
        return

    if fmt == "html":
        _emit(_compare_html(results, task_list), fmt, save_path)
        return

    _emit(_compare_text(results, task_list, verbose=verbose), fmt, save_path)


@main.command()
@click.option("--from", "from_path", required=True, help="JSON results file to re-render.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="text",
    help="Output format.",
)
@click.option("--save", "save_path", default=None, help="Write the report to this file path.")
@click.option("--verbose", is_flag=True, default=False, help="Show per-task detail breakdown.")
def report(from_path: str, fmt: str, save_path: str | None, verbose: bool) -> None:
    """Re-render a saved JSON results file as text or HTML."""
    import json

    from researchbench import BenchmarkResult, TaskResult

    with open(from_path, encoding="utf-8") as f:
        data = json.load(f)
    result = BenchmarkResult(
        model=data["model"],
        results=[
            TaskResult(
                task_name=r["task"],
                model=data["model"],
                score=r["score"],
                details=r.get("details", {}),
            )
            for r in data["results"]
        ],
    )
    _emit(result.to_format(fmt, verbose=verbose), fmt, save_path)


@main.command()
@click.option("--save", "save_path", default=None, help="Write the schema to this file path.")
def schema(save_path: str | None) -> None:
    """Print the JSON Schema for the report format."""
    import pathlib

    schema_path = (
        pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "report-schema.json"
    )
    with open(schema_path, encoding="utf-8") as f:
        raw = f.read()
    _emit(raw, "json", save_path)


@main.command()
def verify() -> None:
    """Verify the installation by running all tasks in mock mode."""
    bench = Benchmark()
    result = bench.run(model="gpt-4o")
    all_ok = all(0.0 <= r.score <= 100.0 for r in result.results)
    click.echo("ResearchBench Verification")
    click.echo("=" * 50)
    for r in result.results:
        status = "PASS" if 0.0 <= r.score <= 100.0 else "FAIL"
        click.echo(f"  [{status}] {r.task_name:25s} {r.score:.2f}")
    click.echo("=" * 50)
    if all_ok:
        click.echo("All 7 tasks passed mock-mode verification. Installation is working.")
    else:
        raise SystemExit(1)


def _compare_text(results: list[BenchmarkResult], task_list: list[str], verbose: bool) -> str:
    header_models = [r.model for r in results]
    col = max(16, max((len(m) for m in header_models), default=0))
    lines = ["ResearchBench Comparison", "=" * 70]
    lines.append(f"  {'task':25s} " + " ".join(f"{m:>{col}s}" for m in header_models))
    lines.append("  " + "-" * (25 + (col + 1) * len(header_models)))
    for task in task_list:
        cells = []
        for r in results:
            match = next((x.score for x in r.results if x.task_name == task), float("nan"))
            cells.append(f"{match:>{col}.2f}")
        lines.append(f"  {task:25s} " + " ".join(cells))
    lines.append("  " + "-" * (25 + (col + 1) * len(header_models)))
    avg_cells = [f"{r.average():>{col}.2f}" for r in results]
    lines.append(f"  {'AVERAGE':25s} " + " ".join(avg_cells))
    if verbose:
        for r in results:
            lines.append("")
            lines.append(f"  [{r.model}] details:")
            for x in r.results:
                lines.append(f"    {x.task_name}: {x.details}")
    return "\n".join(lines)


def _compare_html(results: list[BenchmarkResult], task_list: list[str]) -> str:
    import html

    def cell(score: float) -> str:
        return f"<td style='text-align:right'>{score:.2f}</td>"

    head = "".join(f"<th>{html.escape(r.model)}</th>" for r in results)
    rows = []
    for task in task_list:
        cells = []
        for r in results:
            s = next((x.score for x in r.results if x.task_name == task), float("nan"))
            cells.append(cell(s))
        rows.append(f"<tr><td>{html.escape(task)}</td>{''.join(cells)}</tr>")
    avg_cells = "".join(cell(r.average()) for r in results)
    rows.append(f"<tr><td><b>AVERAGE</b></td>{avg_cells}</tr>")
    rows_html = "\n".join(rows)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ResearchBench Comparison</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; color: #1f2933; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d2d6dc; padding: 0.45rem 0.6rem; }}
  th {{ background: #f4f6f9; }}
</style>
</head>
<body>
<h1>ResearchBench Comparison</h1>
<table>
<thead><tr><th>Task</th>{head}</tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>"""


if __name__ == "__main__":
    main()
