"""Tests for the core benchmark runner: result rendering and compare()."""

import json

import pytest

from researchbench import Benchmark
from researchbench.core import BenchmarkResult, TaskResult


@pytest.fixture
def bench():
    return Benchmark()


@pytest.fixture
def result(bench):
    return bench.run(model="mock", allow_draft=True)


class TestBenchmarkResult:
    def test_average(self, result):
        assert 0.0 <= result.average() <= 100.0
        assert result.average() == sum(r.score for r in result.results) / len(result.results)

    def test_summary_is_text_alias(self, result):
        # summary() must remain a short text report (backward compatible).
        assert "ResearchBench" in result.summary()
        assert "AVERAGE" in result.summary()

    def test_to_text_non_verbose(self, result):
        text = result.to_text(verbose=False)
        assert "ResearchBench" in text
        for r in result.results:
            assert r.task_name in text
        # details should NOT leak into the non-verbose report
        assert "details" not in text.lower()

    def test_to_text_verbose_includes_details(self, result):
        text = result.to_text(verbose=True)
        for r in result.results:
            # the details dict keys appear in verbose mode
            for key in r.details:
                assert str(key) in text

    def test_to_json_structure(self, result):
        data = json.loads(result.to_json())
        assert data["model"] == "mock"
        assert data["n_tasks"] == len(result.results)
        assert "average" in data
        assert isinstance(data["results"], list)
        assert {"task", "score", "details"} <= set(data["results"][0])

    def test_run_record_metadata(self, bench):
        """RESEARCH_BENCHMARK.md Section 7.1: run records must capture metadata."""
        result = bench.run(model="gpt-4o", allow_draft=True)
        assert result.timestamp  # ISO 8601 string
        assert result.benchmark_version  # e.g. "0.1.0"
        assert result.run_config["model"] == "gpt-4o"
        assert "paper_comprehension" in result.run_config["tasks"]
        for r in result.results:
            assert r.duration_seconds >= 0.0
            assert r.evaluator_version  # e.g. "keyword-matching-v0.1"

    def test_raw_output_captured(self, bench):
        """RESEARCH_BENCHMARK.md Section 7.2: raw outputs must not be discarded."""
        result = bench.run(model="gpt-4o", capture_raw=True, allow_draft=True)
        for r in result.results:
            assert r.raw_output != "", f"{r.task_name} raw_output is empty"

    def test_raw_output_disabled(self, bench):
        result = bench.run(model="gpt-4o", capture_raw=False, allow_draft=True)
        for r in result.results:
            assert r.raw_output == ""

    def test_to_html_structure(self, result):
        html = result.to_html()
        assert html.startswith("<!doctype html>")
        assert "<table>" in html
        for r in result.results:
            assert r.task_name in html
        assert "ResearchBench Report" in html

    def test_to_html_escapes_special_chars(self):
        res = BenchmarkResult(model="<x>")
        res.results.append(TaskResult(task_name="a&b", model="<x>", score=50.0, details={"k": "v"}))
        h = res.to_html()
        assert "<x>" not in h  # escaped
        assert "&lt;x&gt;" in h
        assert "a&b" not in h

    def test_to_format_dispatch(self, result):
        assert result.to_format("text") == result.to_text(verbose=False)
        assert result.to_format("json") == result.to_json()
        assert result.to_format("html") == result.to_html()
        # unknown format falls back to text
        assert result.to_format("weird") == result.to_text(verbose=False)

    def test_to_format_verbose_text(self, result):
        assert result.to_format("text", verbose=True) == result.to_text(verbose=True)

    def test_empty_result_average(self):
        assert BenchmarkResult(model="x").average() == 0.0


class TestBenchmarkRunner:
    def test_available_tasks_canonical_order(self):
        tasks = Benchmark.available_tasks()
        assert tasks == [
            "paper_comprehension",
            "idea_generation",
            "literature_synthesis",
            "experimental_design",
            "peer_review",
            "reproduction",
            "open_question_id",
        ]

    def test_compare_returns_one_result_per_model(self, bench):
        results = bench.compare(
            allow_draft=True, models=["gpt-4o", "claude-3-opus", "unknown-model"]
        )
        assert len(results) == 3
        assert [r.model for r in results] == ["gpt-4o", "claude-3-opus", "unknown-model"]
        for r in results:
            assert len(r.results) == len(bench.tasks)
            assert 0.0 <= r.average() <= 100.0

    def test_compare_preserves_task_subset(self):
        bench = Benchmark(tasks=["paper_comprehension", "open_question_id"])
        results = bench.compare(allow_draft=True, models=["gpt-4o", "claude-3-opus"])
        for r in results:
            assert {x.task_name for x in r.results} == {"paper_comprehension", "open_question_id"}
