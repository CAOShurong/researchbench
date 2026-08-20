"""Tests for ResearchBench."""
import pytest
from researchbench import Benchmark
from researchbench.tasks.paper_comprehension import PaperComprehension
from researchbench.tasks.idea_generation import IdeaGeneration
from researchbench.tasks.literature_synthesis import LiteratureSynthesis
from researchbench.tasks.experimental_design import ExperimentalDesign
from researchbench.tasks.peer_review import PeerReview
from researchbench.tasks.reproduction import Reproduction
from researchbench.tasks.open_question_id import OpenQuestionId

ALL_TASK_CLASSES = [
    PaperComprehension, IdeaGeneration, LiteratureSynthesis,
    ExperimentalDesign, PeerReview, Reproduction, OpenQuestionId,
]

class TestTaskInterface:
    def test_all_tasks_have_evaluate(self):
        for cls in ALL_TASK_CLASSES:
            task = cls()
            assert hasattr(task, "evaluate"), f"{cls.__name__} missing evaluate method"
            assert callable(task.evaluate), f"{cls.__name__}.evaluate not callable"

    def test_all_tasks_evaluate_returns_tuple(self):
        for cls in ALL_TASK_CLASSES:
            task = cls()
            result = task.evaluate(model="mock")
            assert isinstance(result, tuple), f"{cls.__name__} evaluate must return tuple"
            assert len(result) == 2, f"{cls.__name__} evaluate must return (score, dict)"
            score, details = result
            assert isinstance(score, (int, float)), f"{cls.__name__} score must be numeric"
            assert isinstance(details, dict), f"{cls.__name__} details must be dict"

    def test_all_tasks_score_range(self):
        for cls in ALL_TASK_CLASSES:
            task = cls()
            score, _ = task.evaluate(model="mock")
            assert 0.0 <= score <= 100.0, f"{cls.__name__} score {score} outside [0, 100]"

class TestBenchmark:
    def test_benchmark_creates_tasks(self):
        bench = Benchmark()
        assert len(bench.tasks) == 7, "Should have all 7 tasks"

    def test_benchmark_selective_tasks(self):
        bench = Benchmark(tasks=["paper_comprehension", "idea_generation"])
        assert len(bench.tasks) == 2, "Should only have 2 tasks"

    def test_benchmark_run(self):
        bench = Benchmark()
        result = bench.run(model="mock")
        assert len(result.results) == 7
        for r in result.results:
            assert 0.0 <= r.score <= 100.0

    def test_benchmark_summary(self):
        bench = Benchmark()
        result = bench.run(model="mock")
        summary = result.summary()
        assert "ResearchBench" in summary
        assert "AVERAGE" in summary

    def test_benchmark_to_json(self):
        bench = Benchmark()
        result = bench.run(model="mock")
        js = result.to_json()
        assert '"model"' in js
        assert '"results"' in js