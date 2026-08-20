"""Detailed unit tests for the ExperimentalDesign task."""

import pytest

from researchbench.tasks import experimental_design as ed
from researchbench.tasks.experimental_design import HYPOTHESES, ExperimentalDesign

SECTION_WORDS = ["control", "sample", "statistical", "confound", "interpret"]


def _perfect_response() -> str:
    """All keywords across hypotheses + all section words + >=600 chars."""
    kws = []
    for h in HYPOTHESES:
        kws.extend(h["keywords"])
    body = " ".join(kws) + " " + " ".join(SECTION_WORDS)
    if len(body) < 600:
        body += " " + "z" * (600 - len(body))
    return body


@pytest.fixture
def task():
    return ExperimentalDesign()


class TestFixtureStructure:
    def test_hypotheses_non_empty(self):
        assert len(HYPOTHESES) >= 1

    def test_each_hypothesis_has_required_keys(self):
        for h in HYPOTHESES:
            assert h.get("id")
            assert h.get("hypothesis")
            assert h.get("question")
            assert "keywords" in h and len(h["keywords"]) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_sections_drive_completeness(self, task, monkeypatch):
        # Keywords present but no section words -> completeness 0.
        kws = []
        for h in HYPOTHESES:
            kws.extend(h["keywords"])
        long_resp = " ".join(kws) + " " + "z" * 600
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: long_resp)
        score_no_sections, _ = task.evaluate(model="gpt-4o")
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: _perfect_response())
        score_full, _ = task.evaluate(model="gpt-4o")
        assert score_no_sections < score_full

    def test_partial_response_partial_score(self, task, monkeypatch):
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: "control sample statistical")
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(ed, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_hypothesis" in details and "average" in details
        for h in HYPOTHESES:
            entry = details["per_hypothesis"][h["id"]]
            for key in ("score", "keyword_coverage", "sections", "length"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = ed._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = ed._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = ed._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
