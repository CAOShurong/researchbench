"""Phase 3 tests: subscription/API RunRecord CLI integration (Issue #7)."""

import json
import subprocess
import sys

import pytest

from researchbench.subscription import (
    APIRun,
    RunRecord,
    SubscriptionRun,
    validate_run_record,
)


def _run_cli(args):
    proc = subprocess.run(
        [sys.executable, "-m", "researchbench"] + args,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _write_json(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def _valid_subscription_record():
    return RunRecord(
        benchmark_version="0.1.0",
        task_id="paper_comprehension/attention-2017/q1",
        subscription_run=SubscriptionRun(
            product="ChatGPT (GPT-4o)",
            reasoning_mode="auto",
            browsing=True,
            prompt="What is the core contribution?",
            run_date="2026-08-21T12:00:00Z",
            full_output="The Transformer uses self-attention...",
            cited_sources=["https://arxiv.org/abs/1706.03762"],
        ),
        evaluation_result={"score": 75.0},
        evaluator_version="keyword-matching-v0.1",
    )


def _valid_api_record():
    return RunRecord(
        benchmark_version="0.1.0",
        task_id="idea_generation/few-shot-llm",
        api_run=APIRun(
            provider="openai",
            model_id="gpt-4o-2024-11-20",
            api_params={"temperature": 0.0},
            prompt="Propose a novel hypothesis.",
            full_output="I propose that...",
            run_date="2026-08-21T12:00:00Z",
        ),
        evaluation_result={"score": 64.5},
        evaluator_version="keyword-matching-v0.1",
    )


class TestRunRecordValidation:
    def test_valid_subscription(self):
        errors = validate_run_record(_valid_subscription_record())
        assert not errors

    def test_valid_api(self):
        errors = validate_run_record(_valid_api_record())
        assert not errors

    def test_empty_benchmark_version(self):
        r = _valid_subscription_record()
        r.benchmark_version = ""
        assert any("benchmark_version" in e for e in validate_run_record(r))

    def test_empty_task_id(self):
        r = _valid_subscription_record()
        r.task_id = ""
        assert any("task_id" in e for e in validate_run_record(r))

    def test_empty_product(self):
        r = _valid_subscription_record()
        r.subscription_run.product = ""
        assert any("product" in e for e in validate_run_record(r))

    def test_empty_prompt(self):
        r = _valid_subscription_record()
        r.subscription_run.prompt = ""
        assert any("prompt" in e for e in validate_run_record(r))

    def test_empty_run_date(self):
        r = _valid_subscription_record()
        r.subscription_run.run_date = ""
        assert any("run_date" in e for e in validate_run_record(r))

    def test_empty_full_output(self):
        r = _valid_subscription_record()
        r.subscription_run.full_output = ""
        assert any("full_output" in e for e in validate_run_record(r))

    def test_empty_evaluator_version(self):
        r = _valid_subscription_record()
        r.evaluator_version = ""
        assert any("evaluator_version" in e for e in validate_run_record(r))

    def test_cannot_mix_subscription_and_api(self):
        with pytest.raises(ValueError, match="separate experimental conditions"):
            RunRecord(
                benchmark_version="0.1.0",
                task_id="test/1",
                subscription_run=SubscriptionRun(product="x"),
                api_run=APIRun(provider="y", model_id="z"),
            )

    def test_requires_at_least_one_run(self):
        with pytest.raises(ValueError, match="requires either"):
            RunRecord(benchmark_version="0.1.0", task_id="test/1")


class TestRunRecordRoundTrip:
    def test_subscription_round_trip(self):
        r = _valid_subscription_record()
        js = r.to_json()
        r2 = RunRecord.from_json(js)
        assert r2.task_id == r.task_id
        assert r2.benchmark_version == r.benchmark_version
        assert r2.subscription_run is not None
        assert r2.subscription_run.product == r.subscription_run.product
        assert r2.evaluator_version == r.evaluator_version

    def test_api_round_trip(self):
        r = _valid_api_record()
        js = r.to_json()
        r2 = RunRecord.from_json(js)
        assert r2.task_id == r.task_id
        assert r2.api_run is not None
        assert r2.api_run.model_id == r.api_run.model_id

    def test_corrupted_json(self):
        with pytest.raises(json.JSONDecodeError):
            RunRecord.from_json("not valid json{")

    def test_wrong_mode(self):
        r = _valid_subscription_record()
        d = r.to_dict()
        d["run"]["mode"] = "invalid"
        with pytest.raises(ValueError, match="mode"):
            RunRecord.from_dict(d)


class TestRunRecordCLI:
    def test_validate_subscription(self, tmp_path):
        r = _valid_subscription_record()
        p = _write_json(tmp_path, "sub.json", r.to_dict())
        rc, stdout, _ = _run_cli(["run-record", "validate", "--from", p])
        assert rc == 0
        assert "Valid" in stdout

    def test_validate_api(self, tmp_path):
        r = _valid_api_record()
        p = _write_json(tmp_path, "api.json", r.to_dict())
        rc, stdout, _ = _run_cli(["run-record", "validate", "--from", p])
        assert rc == 0
        assert "Valid" in stdout

    def test_validate_empty_fields(self, tmp_path):
        r = _valid_subscription_record()
        r.benchmark_version = ""
        p = _write_json(tmp_path, "bad.json", r.to_dict())
        rc, stdout, _ = _run_cli(["run-record", "validate", "--from", p])
        assert rc != 0
        assert "FAILED" in stdout

    def test_import_valid(self, tmp_path):
        r = _valid_subscription_record()
        p = _write_json(tmp_path, "sub.json", r.to_dict())
        rc, stdout, _ = _run_cli(["run-record", "import", "--from", p])
        assert rc == 0
        assert "Imported" in stdout

    def test_import_invalid(self, tmp_path):
        r = _valid_subscription_record()
        r.task_id = ""
        p = _write_json(tmp_path, "bad.json", r.to_dict())
        rc, _, _ = _run_cli(["run-record", "import", "--from", p])
        assert rc != 0

    def test_export_valid(self, tmp_path):
        r = _valid_subscription_record()
        p = _write_json(tmp_path, "sub.json", r.to_dict())
        out = str(tmp_path / "out.json")
        rc, _, _ = _run_cli(["run-record", "export", "--from", p, "--save", out])
        assert rc == 0
        with open(out, encoding="utf-8") as f:
            exported = json.loads(f.read())
        assert exported["task_id"] == r.task_id

    def test_export_invalid(self, tmp_path):
        r = _valid_subscription_record()
        r.subscription_run.full_output = ""
        p = _write_json(tmp_path, "bad.json", r.to_dict())
        rc, _, _ = _run_cli(["run-record", "export", "--from", p])
        assert rc != 0

    def test_corrupted_json(self, tmp_path):
        p = tmp_path / "corrupt.json"
        p.write_text("not json{", encoding="utf-8")
        rc, _, _ = _run_cli(["run-record", "validate", "--from", str(p)])
        assert rc != 0

    def test_round_trip_via_cli(self, tmp_path):
        """Export then import must preserve all fields."""
        r = _valid_subscription_record()
        src = _write_json(tmp_path, "src.json", r.to_dict())
        out = str(tmp_path / "exported.json")
        # Export
        rc, _, _ = _run_cli(["run-record", "export", "--from", src, "--save", out])
        assert rc == 0
        # Import
        rc, _, _ = _run_cli(["run-record", "import", "--from", out])
        assert rc == 0
        # Verify fields preserved
        with open(out, encoding="utf-8") as f:
            exported = json.loads(f.read())
        assert exported["benchmark_version"] == r.benchmark_version
        assert exported["task_id"] == r.task_id
        assert exported["run"]["product"] == r.subscription_run.product
        assert exported["run"]["full_output"] == r.subscription_run.full_output
        assert exported["evaluator_version"] == r.evaluator_version
