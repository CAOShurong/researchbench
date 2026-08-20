"""Detailed unit tests for the LiteratureSynthesis task."""

import pytest

from researchbench.tasks import literature_synthesis as ls
from researchbench.tasks.literature_synthesis import SYNTHESIS_SETS, LiteratureSynthesis


def _perfect_response() -> str:
    """Contains all keywords across all synthesis sets and is >=400 chars."""
    kws = []
    for sset in SYNTHESIS_SETS:
        kws.extend(sset["keywords"])
    body = " ".join(kws)
    if len(body) < 400:
        body += " " + "z" * (400 - len(body))
    return body


@pytest.fixture
def task():
    return LiteratureSynthesis()


class TestFixtureStructure:
    def test_sets_non_empty(self):
        assert len(SYNTHESIS_SETS) >= 1

    def test_each_set_has_required_keys(self):
        for sset in SYNTHESIS_SETS:
            assert sset.get("id")
            assert "papers" in sset and len(sset["papers"]) >= 1
            assert sset.get("question")
            assert "keywords" in sset and len(sset["keywords"]) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(ls, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(ls, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_partial_keywords_partial_score(self, task, monkeypatch):
        kws = SYNTHESIS_SETS[0]["keywords"][:3]
        monkeypatch.setattr(ls, "_call_model", lambda model, prompt: " ".join(kws))
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_coverage_cap(self, task, monkeypatch):
        # 2x weight must cap coverage at 1.0 even with all keywords present.
        monkeypatch.setattr(ls, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(ls, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_set" in details and "average" in details
        for sset in SYNTHESIS_SETS:
            entry = details["per_set"][sset["id"]]
            for key in ("score", "keyword_coverage", "length"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = ls._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = ls._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = ls._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
