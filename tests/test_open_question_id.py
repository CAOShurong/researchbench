"""Detailed unit tests for the OpenQuestionId task."""
import pytest

from researchbench.tasks import open_question_id as oq
from researchbench.tasks.open_question_id import OpenQuestionId, PAPER_SETS


def _perfect_response() -> str:
    """All keywords + importance/progress/future markers + >=400 chars."""
    kws = []
    for ps in PAPER_SETS:
        kws.extend(ps["keywords"])
    body = " ".join(kws) + " important progress future"
    # Pad well above 400 so substituting "important" with a shorter synonym
    # (e.g. "critical") cannot drop length_score below 1.0.
    if len(body) < 600:
        body += " " + "z" * (600 - len(body))
    return body


@pytest.fixture
def task():
    return OpenQuestionId()


class TestFixtureStructure:
    def test_paper_sets_non_empty(self):
        assert len(PAPER_SETS) >= 1

    def test_each_set_has_required_keys(self):
        for ps in PAPER_SETS:
            assert "id" in ps and ps["id"]
            assert "papers" in ps and len(ps["papers"]) >= 1
            assert "question" in ps and ps["question"]
            assert "keywords" in ps and len(ps["keywords"]) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(oq, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(oq, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_missing_quality_markers_lowers_score(self, task, monkeypatch):
        resp = " ".join(kw for ps in PAPER_SETS for kw in ps["keywords"]) + " " + "z" * 400
        monkeypatch.setattr(oq, "_call_model", lambda model, prompt: resp)
        score, _ = task.evaluate(model="gpt-4o")
        assert score < 100.0

    def test_importance_word_variants(self, task, monkeypatch):
        for word in ["critical", "key", "fundamental", "crucial"]:
            resp = _perfect_response().replace("important", word)
            monkeypatch.setattr(oq, "_call_model", lambda model, prompt, w=word: resp)
            score, _ = task.evaluate(model="gpt-4o")
            assert score == pytest.approx(100.0)

    def test_partial_response_partial_score(self, task, monkeypatch):
        monkeypatch.setattr(oq, "_call_model", lambda model, prompt: "benchmark important future")
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(oq, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_set" in details and "average" in details
        for ps in PAPER_SETS:
            entry = details["per_set"][ps["id"]]
            for key in ("score", "keyword_coverage", "has_importance", "has_future", "length"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = oq._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = oq._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = oq._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
