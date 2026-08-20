# ResearchBench core: benchmark runner, task result, and scoring framework
from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskResult:
    task_name: str
    model: str
    score: float
    details: dict[str, Any] = field(default_factory=dict)
    raw_output: str = ""


@dataclass
class BenchmarkResult:
    results: list[TaskResult] = field(default_factory=list)
    model: str = ""

    def summary(self) -> str:
        """Short human-readable text summary (no per-task details)."""
        return self.to_text(verbose=False)

    def average(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    def to_text(self, verbose: bool = False) -> str:
        """Human-readable report.

        When ``verbose`` is True, each task's ``details`` dict is rendered so a
        reader can inspect keyword coverage, flaws found, etc.
        """
        lines = [f"ResearchBench Results: {self.model}"]
        lines.append("=" * 60)
        for r in self.results:
            lines.append(f"  {r.task_name:25s}: {r.score:6.2f}")
            if verbose and r.details:
                for k, v in r.details.items():
                    lines.append(f"      {k}: {v}")
        if self.results:
            lines.append("-" * 60)
            lines.append(f"  {'AVERAGE':25s}: {self.average():6.2f}")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "model": self.model,
                "average": round(self.average(), 4),
                "n_tasks": len(self.results),
                "results": [
                    {
                        "task": r.task_name,
                        "score": r.score,
                        "details": r.details,
                    }
                    for r in self.results
                ],
            },
            indent=2,
        )

    def to_html(self) -> str:
        """Self-contained HTML report with a results table."""
        rows = []
        for r in self.results:
            det = html.escape(json.dumps(r.details, default=str))
            rows.append(
                "<tr>"
                f"<td>{html.escape(r.task_name)}</td>"
                f"<td style='text-align:right'>{r.score:.2f}</td>"
                f"<td><details><summary>details</summary><pre>{det}</pre></details></td>"
                "</tr>"
            )
        rows_html = "\n".join(rows)
        avg = self.average()
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ResearchBench Report &mdash; {html.escape(self.model)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; color: #1f2933; }}
  h1 {{ margin-bottom: 0.25rem; }}
  .avg {{ font-size: 1.25rem; font-weight: 600; color: #0a6; margin: 0.5rem 0 1rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d2d6dc; padding: 0.45rem 0.6rem; text-align: left; vertical-align: top; }}
  th {{ background: #f4f6f9; }}
  pre {{ white-space: pre-wrap; margin: 0; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>ResearchBench Report</h1>
<p>Model: <code>{html.escape(self.model)}</code> &middot; Tasks: {len(self.results)}</p>
<p class="avg">Average score: {avg:.2f}</p>
<table>
<thead><tr><th>Task</th><th style="text-align:right">Score</th><th>Details</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>"""

    def to_format(self, fmt: str, verbose: bool = False) -> str:
        """Render the result in ``text``, ``json`` or ``html`` format."""
        if fmt == "json":
            return self.to_json()
        if fmt == "html":
            return self.to_html()
        return self.to_text(verbose=verbose)


class Benchmark:
    """Main benchmark runner."""

    def __init__(self, tasks: list | None = None):
        import researchbench.tasks as t

        all_tasks: dict[str, Any] = {
            "paper_comprehension": t.PaperComprehension(),
            "idea_generation": t.IdeaGeneration(),
            "literature_synthesis": t.LiteratureSynthesis(),
            "experimental_design": t.ExperimentalDesign(),
            "peer_review": t.PeerReview(),
            "reproduction": t.Reproduction(),
            "open_question_id": t.OpenQuestionId(),
        }
        self.tasks: dict[str, Any] = {
            k: all_tasks[k] for k in (tasks or list(all_tasks)) if k in all_tasks
        }

    def run(self, model: str = "gpt-4o", **kwargs) -> BenchmarkResult:
        result = BenchmarkResult(model=model)
        for name, task in self.tasks.items():
            score, details = task.evaluate(model=model, **kwargs)
            result.results.append(
                TaskResult(task_name=name, model=model, score=score, details=details)
            )
        return result

    @staticmethod
    def available_tasks() -> list[str]:
        """Names of every task this benchmark can run, in canonical order."""
        return [
            "paper_comprehension",
            "idea_generation",
            "literature_synthesis",
            "experimental_design",
            "peer_review",
            "reproduction",
            "open_question_id",
        ]

    def compare(self, models: list[str], **kwargs) -> list[BenchmarkResult]:
        """Run the same tasks against each model in ``models``.

        Returns one :class:`BenchmarkResult` per model, preserving input order.
        """
        return [self.run(model=m, **kwargs) for m in models]
