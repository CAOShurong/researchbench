"""Detailed unit tests for the Reproduction task."""
import pytest

from researchbench.tasks import reproduction as rp
from researchbench.tasks.reproduction import Reproduction, SCENARIOS


def _perfect_response() -> str:
    """All key causes + all keywords + a diagnosis word -> score 100."""
    causes = []
    for sc in SCENARIOS:
        causes.extend(sc["key_causes"])
    kws = []
    for sc in SCENARIOS:
        kws.extend(sc["keywords"])
    return " ".join(causes) + " " + " ".join(kws) + " diagnose"


@pytest.fixture
def task():
    return Reproduction()


class TestFixtureStructure:
    def test_scenarios_non_empty(self):
        assert len(SCENARIOS) >= 1

    def test_each_scenario_has_required_keys(self):
        for sc in SCENARIOS:
            assert "id" in sc and sc["id"]
            assert "description" in sc and sc["description"]
            assert "question" in sc and sc["question"]
            assert "keywords" in sc and len(sc["keywords"]) >= 1
            assert "key_causes" in sc and len(sc["key_causes"]) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_baseline(self, task, monkeypatch):
        # No causes/keywords/diagnosis -> only the 0.5 diagnosis baseline.
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(10.0)

    def test_diagnosis_word_raises_score(self, task, monkeypatch):
        # A bare diagnosis word matches no key causes and no keywords, cleanly
        # isolating the diagnosis_score component (0.5 baseline vs 1.0 when a
        # trigger word is present). Empty -> 10.0, "diagnose" -> 20.0.
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: "")
        score_no_diag, _ = task.evaluate(model="gpt-4o")
        assert score_no_diag == pytest.approx(10.0)
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: "diagnose")
        score_diag, _ = task.evaluate(model="gpt-4o")
        assert score_diag == pytest.approx(20.0)
        assert score_diag > score_no_diag

    def test_diagnosis_word_variants(self, task, monkeypatch):
        for word in ["check", "compare", "investigate", "test"]:
            resp = _perfect_response().replace("diagnose", word)
            monkeypatch.setattr(rp, "_call_model", lambda model, prompt, w=word: resp)
            score, _ = task.evaluate(model="gpt-4o")
            assert score == pytest.approx(100.0)

    def test_partial_response_partial_score(self, task, monkeypatch):
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: "seed random diagnose")
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(rp, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_scenario" in details and "average" in details
        for sc in SCENARIOS:
            entry = details["per_scenario"][sc["id"]]
            for key in ("score", "causes_found", "keyword_coverage", "length"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = rp._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = rp._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = rp._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
