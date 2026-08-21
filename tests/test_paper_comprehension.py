"""Detailed unit tests for the PaperComprehension task.

Covers: fixture structure, scoring logic with controlled model responses
(keyword coverage and the 1.5x weight cap), the empty-response floor, and the
no-API-key mock fallback path.
"""

import pytest

from researchbench.tasks import paper_comprehension as pc
from researchbench.tasks.paper_comprehension import DATASET, PaperComprehension


def _perfect_response() -> str:
    """A response containing every reference keyword from the authoritative DATASET."""
    kws = []
    for item in DATASET:
        kws.extend(item.task_data.get("reference_keywords", []))
    return " ".join(kws)


@pytest.fixture
def task():
    return PaperComprehension()


class TestFixtureStructure:
    def test_papers_non_empty(self):
        assert len(DATASET) >= 1

    def test_each_paper_has_required_keys(self):
        for item in DATASET:
            assert item.id
            assert item.task_data.get("title")
            assert item.task_data.get("abstract")
            assert item.task_data.get("question")
            assert item.task_data.get("reference_keywords")

    def test_each_question_has_keywords(self):
        for item in DATASET:
            kws = item.task_data.get("reference_keywords", [])
            assert isinstance(kws, list)
            assert len(kws) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_partial_response_scores_between(self, task, monkeypatch):
        # Only the first item's keywords -> score should be < 100 (not all keywords).
        first_kws = DATASET[0].task_data["reference_keywords"][:2]
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: " ".join(first_kws))
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_correctness_capped_at_one(self, task, monkeypatch):
        """The 1.5x weight must never let a single item exceed 1.0."""
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        for item in DATASET:
            per = details["per_item"][item.id]
            assert per["score"] <= per["max"]

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_item" in details
        assert details["total_items"] == len(DATASET)
        for item in DATASET:
            entry = details["per_item"][item.id]
            assert "score" in entry and "max" in entry
            assert entry["max"] == 1

    def test_case_insensitive_keyword_match(self, task, monkeypatch):
        kw = DATASET[0].task_data["reference_keywords"][0]
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: kw.upper())
        score, _ = task.evaluate(model="gpt-4o")
        assert score > 0.0


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = pc._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = pc._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = pc._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
