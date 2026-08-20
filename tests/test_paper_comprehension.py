"""Detailed unit tests for the PaperComprehension task.

Covers: fixture structure, scoring logic with controlled model responses
(keyword coverage and the 1.5x weight cap), the empty-response floor, and the
no-API-key mock fallback path.
"""
import pytest

from researchbench.tasks import paper_comprehension as pc
from researchbench.tasks.paper_comprehension import PaperComprehension, PAPERS


def _perfect_response() -> str:
    """A response containing every reference keyword across all papers/questions.

    With this input every question's match_count equals its reference keyword
    count, so correctness caps at 1.0 and the aggregate score is exactly 100.
    """
    kws = []
    for paper in PAPERS:
        for q in paper["questions"]:
            kws.extend(q["reference_keywords"])
    return " ".join(kws)


@pytest.fixture
def task():
    return PaperComprehension()


class TestFixtureStructure:
    def test_papers_non_empty(self):
        assert len(PAPERS) >= 1

    def test_each_paper_has_required_keys(self):
        for paper in PAPERS:
            assert "id" in paper and isinstance(paper["id"], str) and paper["id"]
            assert "title" in paper and paper["title"]
            assert "abstract" in paper and paper["abstract"]
            assert "questions" in paper and len(paper["questions"]) >= 1

    def test_each_question_has_keywords(self):
        for paper in PAPERS:
            for q in paper["questions"]:
                assert "q" in q and q["q"]
                assert "reference_keywords" in q
                assert isinstance(q["reference_keywords"], list)
                assert len(q["reference_keywords"]) >= 1


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        score, details = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_zero(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(0.0)

    def test_partial_response_scores_between(self, task, monkeypatch):
        # Only the first paper's first-question keywords -> low but nonzero.
        first_kws = PAPERS[0]["questions"][0]["reference_keywords"]
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: " ".join(first_kws))
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_correctness_capped_at_one(self, task, monkeypatch):
        """The 1.5x weight must never let a single question exceed 1.0."""
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        score, details = task.evaluate(model="gpt-4o")
        for paper in PAPERS:
            per = details["per_paper"][paper["id"]]
            assert per["score"] <= per["max"]

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(pc, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_paper" in details
        assert details["total_questions"] == len(PAPERS) * 3
        for paper in PAPERS:
            entry = details["per_paper"][paper["id"]]
            assert "score" in entry and "max" in entry
            assert entry["max"] == len(paper["questions"])

    def test_case_insensitive_keyword_match(self, task, monkeypatch):
        kw = PAPERS[0]["questions"][0]["reference_keywords"][0]
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
