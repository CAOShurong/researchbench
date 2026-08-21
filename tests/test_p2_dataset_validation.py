"""Phase 2 tests: DatasetItem validation in the execution path (Issue #5).

Tests that:
- The pilot item in paper_comprehension is a valid DatasetItem
- validate_item() catches invalid items (missing/empty fields, bad tags)
- `researchbench data paper_comprehension --validate` exits 0 for valid items
- `researchbench data paper_comprehension --format json` exports DatasetItem metadata
- Provenance has structured source_id, license, review_status
"""

import json
import subprocess
import sys

from researchbench.dataset_schema import (
    DatasetItem,
    Provenance,
    validate_item,
)
from researchbench.tasks.paper_comprehension import PILOT_ITEMS


class TestPilotItemValid:
    def test_pilot_item_exists(self):
        assert len(PILOT_ITEMS) >= 1

    def test_pilot_item_is_valid(self):
        for item in PILOT_ITEMS:
            errors = validate_item(item)
            assert not errors, f"{item.id} has validation errors: {errors}"

    def test_pilot_item_has_provenance(self):
        for item in PILOT_ITEMS:
            assert item.provenance is not None, f"{item.id} has no provenance"

    def test_pilot_item_provenance_has_source_id(self):
        for item in PILOT_ITEMS:
            assert item.provenance.source_id, "provenance.source_id must be non-empty"

    def test_pilot_item_provenance_has_license(self):
        for item in PILOT_ITEMS:
            assert item.provenance.license, "provenance.license must be non-empty"

    def test_pilot_item_has_capability_tags(self):
        for item in PILOT_ITEMS:
            assert len(item.capability_tags) >= 1
            for tag in item.capability_tags:
                assert tag.startswith("C"), f"invalid tag: {tag}"

    def test_pilot_item_review_status_is_draft(self):
        """Pilot items are draft — not yet expert-reviewed."""
        for item in PILOT_ITEMS:
            assert item.provenance.review_status == "draft"

    def test_pilot_item_contamination_risk_is_high(self):
        """Attention Is All You Need is a classic paper — high contamination."""
        for item in PILOT_ITEMS:
            assert item.contamination_risk == "high"


class TestValidateItemRejects:
    def test_missing_id(self):
        item = DatasetItem(
            id="",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
        )
        errors = validate_item(item)
        assert any("id is required" in e for e in errors)

    def test_missing_capability_tags(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=[],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
        )
        errors = validate_item(item)
        assert any("capability_tags" in e for e in errors)

    def test_invalid_capability_tag(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C99"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
        )
        errors = validate_item(item)
        assert any("invalid capability_tags" in e for e in errors)

    def test_invalid_scoring_method(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="vibes",
        )
        errors = validate_item(item)
        assert any("invalid scoring_method" in e for e in errors)

    def test_invalid_contamination_risk(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
            contamination_risk="maybe",
        )
        errors = validate_item(item)
        assert any("contamination_risk" in e for e in errors)

    def test_missing_ground_truth(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="",
            ground_truth_source="paper",
            scoring_method="rubric",
        )
        errors = validate_item(item)
        assert any("ground_truth is required" in e for e in errors)

    def test_missing_ground_truth_source(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="",
            scoring_method="rubric",
        )
        errors = validate_item(item)
        assert any("ground_truth_source" in e for e in errors)

    def test_invalid_provenance_source_type(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
            provenance=Provenance(source_id="x", source_type="guess"),
        )
        errors = validate_item(item)
        assert any("provenance.source_type" in e for e in errors)

    def test_invalid_provenance_review_status(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
            provenance=Provenance(source_id="x", source_type="paper", review_status="maybe"),
        )
        errors = validate_item(item)
        assert any("provenance.review_status" in e for e in errors)

    def test_missing_provenance_source_id(self):
        item = DatasetItem(
            id="test/1",
            capability_tags=["C5"],
            ground_truth="answer",
            ground_truth_source="paper",
            scoring_method="rubric",
            provenance=Provenance(source_id="", source_type="paper"),
        )
        errors = validate_item(item)
        assert any("provenance.source_id" in e for e in errors)


class TestDataExportWithValidation:
    def test_data_validate_exits_zero_for_valid_pilot(self):
        proc = subprocess.run(
            [sys.executable, "-m", "researchbench", "data", "paper_comprehension", "--validate"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode == 0
        assert "Validation passed" in proc.stdout

    def test_data_json_exports_dataset_item_metadata(self):
        """data --format json must export DatasetItem.to_dict() with provenance."""
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "researchbench",
                "data",
                "paper_comprehension",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1
        item = data[0]
        assert "id" in item
        assert "capability_tags" in item
        assert "ground_truth" in item
        assert "provenance" in item
        assert item["provenance"]["source_id"] == "arXiv:1706.03762"
        assert item["provenance"]["license"] != "unknown"
        assert item["provenance"]["review_status"] == "draft"
        assert item["contamination_risk"] == "high"
        assert "task_data" in item

    def test_data_json_exports_task_data_with_question(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "researchbench",
                "data",
                "paper_comprehension",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        item = data[0]
        assert "task_data" in item
        assert "question" in item["task_data"]
        assert "abstract" in item["task_data"]
        assert "reference_keywords" in item["task_data"]
