# ResearchBench core: benchmark runner, task result, and scoring framework
from dataclasses import dataclass, field
from typing import Any
import json

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
        lines = [f"ResearchBench Results: {self.model}"]
        lines.append("=" * 50)
        total = 0.0
        for r in self.results:
            lines.append(f"  {r.task_name:25s}: {r.score:.2f}")
            total += r.score
        if self.results:
            lines.append(f"  {'AVERAGE':25s}: {total / len(self.results):.2f}")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "model": self.model,
            "results": [{"task": r.task_name, "score": r.score, "details": r.details} for r in self.results],
        }, indent=2)

class Benchmark:
    """Main benchmark runner."""
    def __init__(self, tasks: list | None = None):
        import researchbench.tasks as t
        all_tasks = {
            "paper_comprehension": t.PaperComprehension(),
            "idea_generation": t.IdeaGeneration(),
            "literature_synthesis": t.LiteratureSynthesis(),
            "experimental_design": t.ExperimentalDesign(),
            "peer_review": t.PeerReview(),
            "reproduction": t.Reproduction(),
            "open_question_id": t.OpenQuestionId(),
        }
        self.tasks = {k: all_tasks[k] for k in (tasks or list(all_tasks)) if k in all_tasks}

    def run(self, model: str = "gpt-4o", **kwargs) -> BenchmarkResult:
        result = BenchmarkResult(model=model)
        for name, task in self.tasks.items():
            score, details = task.evaluate(model=model, **kwargs)
            result.results.append(TaskResult(task_name=name, model=model, score=score, details=details))
        return result