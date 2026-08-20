"""Detailed unit tests for the IdeaGeneration task.

Covers: fixture structure, the novelty/feasibility/length weighted scoring,
generic-phrase penalty, empty floor, and the no-API-key mock fallback.
"""
import pytest

from researchbench.tasks import idea_generation as ig
from researchbench.tasks.idea_generation import (
    IdeaGeneration,
    CONTEXTS,
    NOVELTY_KEYWORDS,
    FEASIBILITY_KEYWORDS,
)


def _perfect_response() -> str:
    """Contains all novelty + feasibility keywords and is >=500 chars.

    Generic phrases are deliberately absent so the penalty stays at 1.0 and the
    weighted score equals 100.0.
    """
    kws = list(NOVELTY_KEYWORDS) + list(FEASIBILITY_KEYWORDS)
    body = " ".join(kws)
    if len(body) < 500:
        body += " " + "z" * (500 - len(body))
    return body


@pytest.fixture
def task():
    return IdeaGeneration()


class TestFixtureStructure:
    def test_contexts_non_empty(self):
        assert len(CONTEXTS) >= 1

    def test_each_context_has_required_keys(self):
        for ctx in CONTEXTS:
            assert "id" in ctx and ctx["id"]
            assert "description" in ctx and ctx["description"]
            assert "question" in ctx and ctx["question"]

    def test_keyword_lists_non_empty(self):
        assert len(NOVELTY_KEYWORDS) >= 1
        assert len(FEASIBILITY_KEYWORDS) >= 1
        assert all(isinstance(k, str) for k in NOVELTY_KEYWORDS)
        assert all(isinstance(k, str) for k in FEASIBILITY_KEYWORDS)


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_novelty_only_partial(self, task, monkeypatch):
        resp = " ".join(NOVELTY_KEYWORDS)
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: resp)
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_generic_phrase_lowers_score(self, task, monkeypatch):
        perfect = _perfect_response()
        penalized = perfect + " further research is needed"
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: perfect)
        score_clean, _ = task.evaluate(model="gpt-4o")
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: penalized)
        score_penalized, _ = task.evaluate(model="gpt-4o")
        assert score_penalized < score_clean

    def test_generic_penalty_floor(self, task, monkeypatch):
        """Penalty cannot drop below 0.3."""
        resp = _perfect_response() + " further research is needed it depends more studies"
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: resp)
        score, _ = task.evaluate(model="gpt-4o")
        assert score > 0.0

    def test_length_capped_at_one(self, task, monkeypatch):
        # Very long response should not inflate length_score beyond its weight.
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: _perfect_response() + " " * 5000)
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(ig, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_context" in details and "average" in details
        for ctx in CONTEXTS:
            entry = details["per_context"][ctx["id"]]
            for key in ("score", "length", "novelty_terms", "feasibility_terms"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = ig._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = ig._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = ig._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
