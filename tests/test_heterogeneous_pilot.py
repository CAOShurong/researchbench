"""Tests for the Heterogeneous Integration & BEOL scientific pilot (Issue #13).

Covers:
- Rubric and Criterion scoring mechanics (evidence patterns, negative indicator penalties, thresholds).
- Strict schema validation for 5 reviewed + 1 draft pilot items.
- Evaluation pipeline with audit detail breakdowns.
- Blinded human calibration pack export.
"""

import json

from researchbench.dataset_schema import is_runnable, validate_item
from researchbench.rubric import (
    Criterion,
    Rubric,
    export_blinded_calibration_pack,
)
from researchbench.tasks.heterogeneous_pilot import (
    PILOT_DATASET,
    RUBRIC_BEOL_THERMAL_BUDGET,
    HeterogeneousPilot,
)


class TestRubricEvaluator:
    def test_criterion_positive_evidence_scoring(self):
        crit = Criterion(
            name="test_temp",
            description="Checks thermal ceiling",
            weight=2.0,
            evidence_patterns=[r"400\s*°?c", r"thermal\s+budget"],
            negative_patterns=[r"1000\s*°?c"],
        )
        res = crit.evaluate("The thermal budget must strictly stay below 400 C for BEOL.")
        assert res.score == 2.0
        assert res.max_score == 2.0
        assert res.passed is True
        assert len(res.matched_evidence) == 2
        assert len(res.triggered_negatives) == 0

    def test_criterion_negative_penalty(self):
        crit = Criterion(
            name="test_temp",
            description="Checks thermal ceiling",
            weight=2.0,
            evidence_patterns=[r"400\s*°?c"],
            negative_patterns=[r"1000\s*°?c"],
        )
        # Contains positive evidence but also triggers hard negative penalty
        res = crit.evaluate("We can heat to 400 C or even 1000 C with RTA.")
        assert res.score < 2.0
        assert res.passed is False
        assert len(res.triggered_negatives) == 1

    def test_rubric_overall_evaluation(self):
        rubric = Rubric(
            passing_threshold=60.0,
            criteria=[
                Criterion(name="c1", description="c1", weight=1.0, evidence_patterns=[r"alpha"]),
                Criterion(name="c2", description="c2", weight=1.0, evidence_patterns=[r"beta"]),
            ],
        )
        res = rubric.evaluate("alpha is present here")
        assert res.total_score == 1.0
        assert res.max_score == 2.0
        assert res.normalized_score == 50.0
        assert res.passed is False  # Below 60% threshold

        res2 = rubric.evaluate("both alpha and beta are present")
        assert res2.total_score == 2.0
        assert res2.normalized_score == 100.0
        assert res2.passed is True

    def test_rubric_serialization(self):
        d = RUBRIC_BEOL_THERMAL_BUDGET.to_dict()
        assert "criteria" in d
        assert "passing_threshold" in d
        restored = Rubric.from_dict(d)
        assert len(restored.criteria) == len(RUBRIC_BEOL_THERMAL_BUDGET.criteria)
        assert restored.passing_threshold == RUBRIC_BEOL_THERMAL_BUDGET.passing_threshold


class TestPilotDatasetSchema:
    def test_dataset_contains_reviewed_and_one_draft_item(self):
        assert len(PILOT_DATASET) == 6
        reviewed = [
            it
            for it in PILOT_DATASET
            if it.provenance and it.provenance.review_status == "reviewed"
        ]
        drafts = [
            it for it in PILOT_DATASET if it.provenance and it.provenance.review_status == "draft"
        ]
        assert len(reviewed) == 5
        assert len(drafts) == 1
        draft = drafts[0]
        assert draft.id == "heterogeneous_pilot/igzo_in2o3_channel_capping/q6"
        assert draft.provenance.source_id == "arXiv:2603.23341"
        assert "10.48550/arXiv.2603.23341" in draft.ground_truth_source
        assert is_runnable(draft) is False
        assert draft.provenance.reviewer_role == ""

    def test_all_items_pass_strict_validation(self):
        for item in PILOT_DATASET:
            errors = validate_item(item)
            assert errors == [], f"Item {item.id} failed validation: {errors}"

    def test_reviewed_items_are_runnable_draft_is_not(self):
        for item in PILOT_DATASET:
            assert item.provenance is not None
            if item.provenance.review_status == "reviewed":
                assert is_runnable(item) is True
            else:
                assert is_runnable(item) is False

    def test_items_have_rubrics_and_hard_negatives(self):
        for item in PILOT_DATASET:
            assert "rubric" in item.task_data
            assert len(item.hard_negatives) >= 1
            assert item.provenance is not None
            assert item.contamination_risk == "low"
            if item.provenance.review_status == "reviewed":
                assert item.provenance.reviewer_role == "cao_shurong"


class TestHeterogeneousPilotExecution:
    def test_pilot_evaluate_runs_cleanly(self):
        pilot = HeterogeneousPilot()
        score, details = pilot.evaluate(model="gpt-4o")
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0
        assert details["total_items"] == 5
        assert len(details["per_item"]) == 5

        for report in details["per_item"].values():
            assert "score" in report
            assert "max" in report
            assert "criteria" in report
            assert report["review_status"] == "reviewed"
        assert (
            "heterogeneous_pilot/igzo_in2o3_channel_capping/q6" in details["skipped_draft_item_ids"]
        )

    def test_evaluate_includes_draft_with_allow_draft(self):
        pilot = HeterogeneousPilot()
        score, details = pilot.evaluate(model="gpt-4o", allow_draft=True)
        assert isinstance(score, float)
        assert details["total_items"] == 6
        assert details["skipped_draft_item_ids"] == []
        draft_id = "heterogeneous_pilot/igzo_in2o3_channel_capping/q6"
        assert draft_id in details["per_item"]
        assert details["per_item"][draft_id]["review_status"] == "draft"


class TestBlindedCalibrationPack:
    def test_export_blinded_calibration_pack(self):
        items = [it.to_dict() for it in PILOT_DATASET[:2]]
        responses = [
            {"item_id": items[0]["id"], "model": "model_1", "output": "Model 1 answer"},
            {"item_id": items[0]["id"], "model": "model_2", "output": "Model 2 answer"},
            {"item_id": items[1]["id"], "model": "model_1", "output": "Model 1 answer for item 2"},
        ]
        pack = export_blinded_calibration_pack(items, responses, seed=123)
        assert len(pack) == 2
        first = pack[0]
        assert first["item_id"] == items[0]["id"]
        assert len(first["variants"]) == 2
        # Verify model names are completely blinded
        for var in first["variants"]:
            assert "model" not in var
            assert var["variant_label"] in ["A", "B"]
            assert var["blinded_id"].startswith("BLIND-")


class TestPilotCLIWiring:
    """The scientific pilot must be reachable from Benchmark and the CLI."""

    def test_aliases_match_authoritative_collection(self):
        from researchbench.tasks.heterogeneous_pilot import DATASET, PILOT_ITEMS

        assert DATASET is PILOT_DATASET
        assert PILOT_ITEMS is PILOT_DATASET

    def test_benchmark_registers_pilot(self):
        from researchbench import Benchmark

        assert "heterogeneous_pilot" in Benchmark.available_tasks()
        bench = Benchmark(tasks=["heterogeneous_pilot"])
        result = bench.run(model="gpt-4o")
        assert len(result.results) == 1
        assert result.results[0].task_name == "heterogeneous_pilot"
        assert result.results[0].evaluator_version == "rubric-v0.1"
        assert 0.0 <= result.results[0].score <= 100.0

    def test_cli_run_without_allow_draft(self):
        from click.testing import CliRunner

        from researchbench.cli import main

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--tasks",
                "heterogeneous_pilot",
                "--model",
                "gpt-4o",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["results"][0]["task"] == "heterogeneous_pilot"
        assert data["results"][0]["evaluator_version"] == "rubric-v0.1"
        assert data["results"][0]["details"]["total_items"] == 5
        assert (
            "heterogeneous_pilot/igzo_in2o3_channel_capping/q6"
            in data["results"][0]["details"]["skipped_draft_item_ids"]
        )

    def test_cli_run_with_allow_draft_includes_draft_item(self):
        from click.testing import CliRunner

        from researchbench.cli import main

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--tasks",
                "heterogeneous_pilot",
                "--model",
                "gpt-4o",
                "--allow-draft",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["results"][0]["details"]["total_items"] == 6
        assert data["results"][0]["details"]["skipped_draft_item_ids"] == []

    def test_cli_data_validate(self):
        from click.testing import CliRunner

        from researchbench.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["data", "heterogeneous_pilot", "--validate"])
        assert result.exit_code == 0, result.output
        assert "6 pilot item(s) OK" in result.output
