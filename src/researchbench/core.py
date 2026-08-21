# ResearchBench core: benchmark runner, task result, and scoring framework
from __future__ import annotations

import html
import importlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from researchbench import __version__


@dataclass
class TaskResult:
    task_name: str
    model: str
    score: float
    details: dict[str, Any] = field(default_factory=dict)
    raw_output: str = ""
    duration_seconds: float = 0.0
    evaluator_version: str = ""


@dataclass
class BenchmarkResult:
    results: list[TaskResult] = field(default_factory=list)
    model: str = ""
    timestamp: str = ""
    benchmark_version: str = ""
    run_config: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Short human-readable text summary (no per-task details)."""
        return self.to_text(verbose=False)

    def average(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    def to_text(self, verbose: bool = False, quiet: bool = False) -> str:
        """Human-readable report.

        When ``verbose`` is True, each task's ``details`` dict is rendered so a
        reader can inspect keyword coverage, flaws found, etc.
        When ``quiet`` is True the header banner is omitted (useful for scripting).
        """
        lines = [] if quiet else [f"ResearchBench Results: {self.model}"]
        if not quiet:
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
                "timestamp": self.timestamp,
                "benchmark_version": self.benchmark_version,
                "run_config": self.run_config,
                "average": round(self.average(), 4),
                "n_tasks": len(self.results),
                "results": [
                    {
                        "task": r.task_name,
                        "score": r.score,
                        "details": r.details,
                        "raw_output": r.raw_output,
                        "duration_seconds": round(r.duration_seconds, 6),
                        "evaluator_version": r.evaluator_version,
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

    def to_format(self, fmt: str, verbose: bool = False, quiet: bool = False) -> str:
        """Render the result in ``text``, ``json`` or ``html`` format."""
        if fmt == "json":
            return self.to_json()
        if fmt == "html":
            return self.to_html()
        return self.to_text(verbose=verbose, quiet=quiet)


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

    def run(
        self,
        model: str = "gpt-4o",
        capture_raw: bool = True,
        parallel: bool = False,
        benchmark: bool = False,
        save_responses_dir: str | None = None,
        allow_draft: bool = False,
        **kwargs,
    ) -> BenchmarkResult:
        """Run all tasks against *model* and return a fully-populated run record.

        When *parallel* is True, tasks run concurrently via ThreadPoolExecutor;
        results are sorted into canonical task order before return.
        When *benchmark* is True, per-task timing is printed to stderr.
        When *save_responses_dir* is set, every raw model response is appended
        (not overwritten) to ``<dir>/<task_name>.txt``.
        When *allow_draft* is False, tasks with draft-only dataset items are
        rejected before any model call.
        Monkeypatches on ``_call_model`` are always restored via try/finally.
        """
        import sys
        from pathlib import Path

        from researchbench.dataset_schema import is_runnable, validate_item

        timestamp = datetime.now(timezone.utc).isoformat()
        run_config: dict[str, Any] = {
            "model": model,
            "tasks": list(self.tasks.keys()),
            "capture_raw": capture_raw,
            "parallel": parallel,
        }
        if save_responses_dir:
            run_config["save_responses_dir"] = save_responses_dir

        result = BenchmarkResult(
            model=model,
            timestamp=timestamp,
            benchmark_version=__version__,
            run_config=run_config,
        )

        # Validate dataset items before any model call. If a task module has
        # a DATASET (or PILOT_ITEMS) collection of DatasetItem objects, every
        # item must pass validate_item() and must be runnable (reviewed or
        # validated) unless allow_draft is True.
        for name in self.tasks:
            mod = importlib.import_module(f"researchbench.tasks.{name}")
            ds = getattr(mod, "DATASET", None) or getattr(mod, "PILOT_ITEMS", None)
            if ds is None:
                continue  # task uses legacy data, no validation
            for item in ds:
                errs = validate_item(item)
                if errs:
                    raise ValueError(
                        f"Task '{name}' item '{item.id}' failed validation: {'; '.join(errs)}"
                    )
                if not allow_draft and not is_runnable(item):
                    raise ValueError(
                        f"Task '{name}' item '{item.id}' has review_status="
                        f"'{item.provenance.review_status}' (draft). "
                        f"Use --allow-draft to run draft items."
                    )

        # Set up per-task monkeypatch wrappers for raw-output capture and
        # --save-responses. ALL wrappers are installed before ANY evaluation
        # starts and ALL originals are restored in a single finally block.
        task_meta: dict[str, dict[str, Any]] = {}
        save_dir = Path(save_responses_dir) if save_responses_dir else None
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)

        try:
            for name in self.tasks:
                task_meta[name] = {"captured": [], "original_fn": None, "mod": None}
                if capture_raw or save_dir:
                    mod = importlib.import_module(f"researchbench.tasks.{name}")
                    original = getattr(mod, "_call_model", None)
                    task_meta[name]["original_fn"] = original
                    task_meta[name]["mod"] = mod
                    if original is not None:
                        cap_list = task_meta[name]["captured"]
                        t_name = name

                        def _make_wrapper(orig, cap, tn, sd):
                            def wrapped(m, p):
                                resp = orig(m, p)
                                cap.append(resp)
                                if sd:
                                    with open(sd / f"{tn}.txt", "a", encoding="utf-8") as f:
                                        f.write(resp + "\n---\n")
                                return resp

                            return wrapped

                        mod._call_model = _make_wrapper(original, cap_list, t_name, save_dir)  # type: ignore[attr-defined]

            def _eval(name_task: tuple[str, Any]) -> tuple[str, float, dict[str, Any], float]:
                n, t = name_task
                t0 = time.perf_counter()
                sc, det = t.evaluate(model=model, **kwargs)
                return n, sc, det, time.perf_counter() - t0

            if parallel:
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.tasks)) as pool:
                    futures = {pool.submit(_eval, (n, t)): n for n, t in self.tasks.items()}
                    raw_results: dict[str, tuple[float, dict[str, Any], float]] = {}
                    for future in concurrent.futures.as_completed(futures):
                        n, sc, det, dur = future.result()
                        raw_results[n] = (sc, det, dur)
                        if benchmark:
                            print(f"  [{n}] {dur:.3f}s", file=sys.stderr)
                # Sort into canonical task order
                for name in self.tasks:
                    if name in raw_results:
                        sc, det, dur = raw_results[name]
                        result.results.append(
                            self._make_task_result(name, model, sc, det, dur, task_meta)
                        )
            else:
                for name, task in self.tasks.items():
                    n, sc, det, dur = _eval((name, task))
                    if benchmark:
                        print(f"  [{n}] {dur:.3f}s", file=sys.stderr)
                    result.results.append(
                        self._make_task_result(name, model, sc, det, dur, task_meta)
                    )
        finally:
            # Restore ALL monkeypatches, even if one task threw
            for name, meta in task_meta.items():
                if meta["original_fn"] is not None and meta["mod"] is not None:
                    meta["mod"]._call_model = meta["original_fn"]

        return result

    @staticmethod
    def _make_task_result(
        name: str,
        model: str,
        score: float,
        details: dict[str, Any],
        duration: float,
        task_meta: dict[str, dict[str, Any]],
    ) -> TaskResult:
        captured = task_meta.get(name, {}).get("captured", [])
        return TaskResult(
            task_name=name,
            model=model,
            score=score,
            details=details,
            raw_output="\n---\n".join(captured) if captured else "",
            duration_seconds=duration,
            evaluator_version="keyword-matching-v0.1",
        )

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
