"""Detailed unit tests for the PeerReview task."""
import pytest

from researchbench.tasks import peer_review as pr
from researchbench.tasks.peer_review import PeerReview, MOCK_SUBMISSIONS, _flaw_in_response


def _perfect_response() -> str:
    """All known flaws verbatim + all keywords + a recommendation word.

    _flaw_in_response requires >=2 words of each flaw to appear; embedding each
    flaw verbatim guarantees flaws_found == len(known_flaws) and a perfect score.
    """
    flaws = []
    for sub in MOCK_SUBMISSIONS:
        flaws.extend(sub["known_flaws"])
    kws = []
    for sub in MOCK_SUBMISSIONS:
        kws.extend(sub["keywords"])
    return " ".join(flaws) + " " + " ".join(kws) + " accept reject revision"


@pytest.fixture
def task():
    return PeerReview()


class TestFixtureStructure:
    def test_submissions_non_empty(self):
        assert len(MOCK_SUBMISSIONS) >= 1

    def test_each_submission_has_required_keys(self):
        for sub in MOCK_SUBMISSIONS:
            assert "id" in sub and sub["id"]
            assert "title" in sub and sub["title"]
            assert "abstract" in sub and sub["abstract"]
            assert "known_flaws" in sub and len(sub["known_flaws"]) >= 1
            assert "question" in sub and sub["question"]
            assert "keywords" in sub and len(sub["keywords"]) >= 1


class TestFlawMatching:
    def test_flaw_match_when_two_words_present(self):
        assert _flaw_in_response("No statistical significance testing", "statistical significance here")

    def test_flaw_no_match_when_one_word(self):
        assert not _flaw_in_response("No statistical significance testing", "only statistical here")

    def test_flaw_match_full_sentence(self):
        assert _flaw_in_response("the quick brown fox", "the quick brown fox jumps")


class TestScoringLogic:
    def test_perfect_response_scores_100(self, task, monkeypatch):
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: _perfect_response())
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(100.0)

    def test_empty_response_scores_baseline(self, task, monkeypatch):
        # No flaws/keywords/recommendation -> only the 0.3 rec baseline contributes.
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: "")
        score, _ = task.evaluate(model="gpt-4o")
        assert score == pytest.approx(6.0)

    def test_no_recommendation_lowers_score(self, task, monkeypatch):
        perfect = _perfect_response().replace("accept", "").replace("reject", "").replace("revision", "")
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: perfect)
        score, _ = task.evaluate(model="gpt-4o")
        assert score < 100.0

    def test_partial_response_partial_score(self, task, monkeypatch):
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: "statistical significance baseline accept")
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 < score < 100.0

    def test_flaw_score_capped(self, task, monkeypatch):
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        for sub in MOCK_SUBMISSIONS:
            entry = details["per_paper"][sub["id"]]
            assert entry["flaws_found"] == entry["total_flaws"]

    def test_details_structure(self, task, monkeypatch):
        monkeypatch.setattr(pr, "_call_model", lambda model, prompt: _perfect_response())
        _, details = task.evaluate(model="gpt-4o")
        assert "per_paper" in details and "average" in details
        for sub in MOCK_SUBMISSIONS:
            entry = details["per_paper"][sub["id"]]
            for key in ("score", "flaws_found", "total_flaws", "has_recommendation", "length"):
                assert key in entry


class TestMockMode:
    def test_gpt_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        out = pr._call_model("gpt-4o", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_claude_mock_without_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        out = pr._call_model("claude-3-opus", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_unknown_model_returns_mock(self):
        out = pr._call_model("some-unknown-model", "anything")
        assert isinstance(out, str) and len(out) > 0

    def test_mock_evaluation_in_range(self, task):
        score, _ = task.evaluate(model="gpt-4o")
        assert 0.0 <= score <= 100.0
