"""Tests for the dataset item schema (RESEARCH_BENCHMARK.md §4.2)."""

from researchbench.dataset_schema import DatasetItem, Provenance, validate_item


def _valid_item(**overrides) -> DatasetItem:
    base = {
        "id": "paper_comprehension/attention-2017/q1",
        "capability_tags": ["C5", "C1"],
        "ground_truth": "The Transformer uses self-attention.",
        "ground_truth_source": "expert: verified against arXiv:1706.03762",
        "scoring_method": "rubric",
        "provenance": Provenance(
            source_id="arXiv:1706.03762",
            source_type="paper",
            license="MIT",
            author_role="benchmark_author",
            reviewer_role="professor",
            review_status="reviewed",
        ),
        "contamination_risk": "high",
    }
    base.update(overrides)
    return DatasetItem(**base)


class TestValidateItem:
    def test_valid_item(self):
        errors = validate_item(_valid_item())
        assert not errors

    def test_missing_id(self):
        errors = validate_item(_valid_item(id=""))
        assert any("id is required" in e for e in errors)

    def test_missing_capability_tags(self):
        errors = validate_item(_valid_item(capability_tags=[]))
        assert any("capability_tags" in e for e in errors)

    def test_invalid_capability_tag(self):
        errors = validate_item(_valid_item(capability_tags=["C99"]))
        assert any("invalid capability_tags" in e for e in errors)

    def test_missing_ground_truth(self):
        errors = validate_item(_valid_item(ground_truth=""))
        assert any("ground_truth is required" in e for e in errors)

    def test_missing_ground_truth_source(self):
        errors = validate_item(_valid_item(ground_truth_source=""))
        assert any("ground_truth_source" in e for e in errors)

    def test_invalid_scoring_method(self):
        errors = validate_item(_valid_item(scoring_method="vibes"))
        assert any("invalid scoring_method" in e for e in errors)

    def test_placeholder_scoring_method(self):
        """keyword_match_placeholder is valid for the current v0.1.0 items."""
        errors = validate_item(_valid_item(scoring_method="keyword_match_placeholder"))
        assert not errors

    def test_invalid_contamination_risk(self):
        errors = validate_item(_valid_item(contamination_risk="maybe"))
        assert any("contamination_risk" in e for e in errors)

    def test_hard_negatives_default_empty(self):
        item = _valid_item()
        assert item.hard_negatives == []

    def test_version_default(self):
        item = _valid_item()
        assert item.version == "1.0"
