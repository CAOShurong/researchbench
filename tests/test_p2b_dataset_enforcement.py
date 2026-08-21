"""Phase 2b tests: DatasetItem enforcement in execution path."""

import json
import subprocess
import sys

import pytest

from researchbench.dataset_schema import (
    DatasetItem,
    Provenance,
    is_runnable,
    validate_item,
)
from researchbench.tasks.paper_comprehension import DATASET


def _run_cli(args):
    """Run researchbench via subprocess."""
    proc = subprocess.run(
        [sys.executable, "-m", "researchbench"] + args,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestUnifiedDataset:
    """sample, data text, data JSON, and runner read the SAME collection."""

    def test_data_text_reports_1_item(self):
        rc, stdout, _ = _run_cli(["data", "paper_comprehension"])
        assert rc == 0
        assert "1 item(s)" in stdout

    def test_data_json_exports_1_item_with_provenance(self):
        rc, stdout, _ = _run_cli(["data", "paper_comprehension", "--format", "json"])
        assert rc == 0
        data = json.loads(stdout)
        assert len(data) == 1
        assert "provenance" in data[0]
        assert data[0]["provenance"]["source_id"] == "arXiv:1706.03762"

    def test_sample_reads_from_dataset(self):
        rc, stdout, _ = _run_cli(["sample", "paper_comprehension", "--format", "json"])
        assert rc == 0
        data = json.loads(stdout)
        assert len(data["sample"]) > 10

    def test_run_uses_dataset_not_legacy(self):
        """Runner uses DATASET (1 item), not legacy PAPERS (2 items)."""
        rc, stdout, _ = _run_cli(
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
                "--allow-draft",
                "--format",
                "json",
            ]
        )
        assert rc == 0
        data = json.loads(stdout)
        r = data["results"][0]
        assert r["details"]["total_items"] == 1


class TestDraftRejection:
    """Draft items must not be silently runnable."""

    def test_run_rejects_draft_without_flag(self):
        rc, _, stderr = _run_cli(
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
            ]
        )
        assert rc != 0
        assert "draft" in stderr.lower()

    def test_run_allows_draft_with_flag(self):
        rc, _, _ = _run_cli(
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
                "--allow-draft",
                "--format",
                "json",
            ]
        )
        assert rc == 0

    def test_compare_rejects_draft_without_flag(self):
        rc, _, _ = _run_cli(
            [
                "compare",
                "--model",
                "gpt-4o",
                "--tasks",
                "paper_comprehension",
            ]
        )
        assert rc != 0

    def test_compare_allows_draft_with_flag(self):
        rc, _, _ = _run_cli(
            [
                "compare",
                "--model",
                "gpt-4o",
                "--tasks",
                "paper_comprehension",
                "--allow-draft",
                "--format",
                "json",
            ]
        )
        assert rc == 0

    def test_verify_allows_draft(self):
        rc, _, _ = _run_cli(["verify"])
        assert rc == 0


class TestInvalidDataRejection:
    """Invalid data causes non-zero exit BEFORE any model call."""

    def test_spy_no_model_call_on_invalid(self, monkeypatch):
        from researchbench.tasks import paper_comprehension as pc

        call_count = 0
        original = pc._call_model

        def counting(model, prompt):
            nonlocal call_count
            call_count += 1
            return original(model, prompt)

        bad = DatasetItem(
            id="bad/1",
            capability_tags=["C99"],
            ground_truth="x",
            ground_truth_source="x",
            scoring_method="bad",
            provenance=Provenance(source_id="", source_type="paper"),
        )
        orig_ds = list(pc.DATASET)
        pc.DATASET = [bad]
        try:
            monkeypatch.setattr(pc, "_call_model", counting)
            from researchbench.core import Benchmark

            bench = Benchmark(tasks=["paper_comprehension"])
            with pytest.raises(ValueError, match="failed validation"):
                bench.run(model="gpt-4o", allow_draft=True)
            assert call_count == 0
        finally:
            pc.DATASET = orig_ds

    def test_spy_no_model_call_on_draft(self, monkeypatch):
        from researchbench.tasks import paper_comprehension as pc

        call_count = 0
        original = pc._call_model

        def counting(model, prompt):
            nonlocal call_count
            call_count += 1
            return original(model, prompt)

        monkeypatch.setattr(pc, "_call_model", counting)
        from researchbench.core import Benchmark

        bench = Benchmark(tasks=["paper_comprehension"])
        with pytest.raises(ValueError, match="draft"):
            bench.run(model="gpt-4o", allow_draft=False)
        assert call_count == 0

    def test_spy_no_model_call_parallel(self, monkeypatch):
        from researchbench.tasks import paper_comprehension as pc

        call_count = 0
        original = pc._call_model

        def counting(model, prompt):
            nonlocal call_count
            call_count += 1
            return original(model, prompt)

        monkeypatch.setattr(pc, "_call_model", counting)
        from researchbench.core import Benchmark

        bench = Benchmark(tasks=["paper_comprehension"])
        with pytest.raises(ValueError, match="draft"):
            bench.run(model="gpt-4o", parallel=True, allow_draft=False)
        assert call_count == 0


class TestUnknownDataTask:
    def test_unknown_exits_nonzero(self):
        rc, _, _ = _run_cli(["data", "does_not_exist"])
        assert rc != 0

    def test_unknown_reports_error(self):
        _, stdout, _ = _run_cli(["data", "does_not_exist"])
        assert "Unknown" in stdout


class TestProvenanceRequired:
    def test_no_provenance_fails(self):
        item = DatasetItem(
            id="t/1",
            capability_tags=["C5"],
            ground_truth="a",
            ground_truth_source="p",
            scoring_method="rubric",
            provenance=None,
        )
        assert any("provenance is required" in e for e in validate_item(item))

    def test_unknown_license_fails(self):
        item = DatasetItem(
            id="t/1",
            capability_tags=["C5"],
            ground_truth="a",
            ground_truth_source="p",
            scoring_method="rubric",
            provenance=Provenance(
                source_id="x",
                source_type="paper",
                license="unknown",
                author_role="a",
                review_status="reviewed",
            ),
        )
        assert any("license" in e for e in validate_item(item))

    def test_missing_author_role_fails(self):
        item = DatasetItem(
            id="t/1",
            capability_tags=["C5"],
            ground_truth="a",
            ground_truth_source="p",
            scoring_method="rubric",
            provenance=Provenance(
                source_id="x",
                source_type="paper",
                license="MIT",
                author_role="",
                review_status="reviewed",
            ),
        )
        assert any("author_role" in e for e in validate_item(item))

    def test_pilot_item_passes_validation(self):
        for item in DATASET:
            assert not validate_item(item)

    def test_pilot_item_is_draft(self):
        for item in DATASET:
            assert not is_runnable(item)

    def test_pilot_has_valid_provenance(self):
        for item in DATASET:
            p = item.provenance
            assert p is not None
            assert p.source_id
            assert p.license != "unknown"
            assert p.author_role
            assert p.review_status == "draft"
