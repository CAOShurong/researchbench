"""Tests for the ResearchBench CLI (text/json/html reports, compare, verbose)."""

import json
import subprocess
import sys

import pytest
from click.testing import CliRunner

from researchbench.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestModuleEntry:
    def test_python_m_researchbench_list(self):
        out = subprocess.run(
            [sys.executable, "-m", "researchbench", "list"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert out.returncode == 0
        assert "paper_comprehension" in out.stdout


class TestListCommand:
    def test_list_outputs_all_tasks(self, runner):
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        for name in [
            "paper_comprehension",
            "idea_generation",
            "literature_synthesis",
            "experimental_design",
            "peer_review",
            "reproduction",
            "open_question_id",
        ]:
            assert name in result.output

    def test_version_option(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "researchbench" in result.output.lower()


class TestShowCommand:
    def test_show_known_task(self, runner):
        result = runner.invoke(main, ["show", "paper_comprehension"])
        assert result.exit_code == 0
        assert "paper_comprehension" in result.output

    def test_show_reports_dataset_size(self, runner):
        result = runner.invoke(main, ["show", "paper_comprehension"])
        assert result.exit_code == 0
        assert "Dataset (PAPERS)" in result.output

    def test_show_unknown_task(self, runner):
        result = runner.invoke(main, ["show", "nope"])
        assert result.exit_code == 0  # graceful
        assert "Unknown" in result.output


class TestTasksCommand:
    def test_tasks_text(self, runner):
        result = runner.invoke(main, ["tasks"])
        assert result.exit_code == 0
        assert "paper_comprehension" in result.output
        assert "dataset:" in result.output.lower()

    def test_tasks_json(self, runner):
        result = runner.invoke(main, ["tasks", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 7
        assert data[0]["name"] == "paper_comprehension"
        assert "dataset_size" in data[0]
        assert data[0]["dataset_size"] > 0

    def test_tasks_json_save(self, runner, tmp_path):
        out = tmp_path / "tasks.json"
        result = runner.invoke(main, ["tasks", "--format", "json", "--save", str(out)])
        assert result.exit_code == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 7


class TestSampleCommand:
    def test_sample_text(self, runner):
        result = runner.invoke(main, ["sample", "paper_comprehension"])
        assert result.exit_code == 0
        assert "Sample prompt" in result.output
        assert "architectural innovation" in result.output

    def test_sample_json(self, runner):
        result = runner.invoke(main, ["sample", "paper_comprehension", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["task"] == "paper_comprehension"
        assert len(data["sample"]) > 0

    def test_sample_unknown_task(self, runner):
        result = runner.invoke(main, ["sample", "nope"])
        assert result.exit_code == 0
        assert "Unknown" in result.output

    @pytest.mark.parametrize(
        "task_name",
        [
            "paper_comprehension",
            "idea_generation",
            "literature_synthesis",
            "experimental_design",
            "peer_review",
            "reproduction",
            "open_question_id",
        ],
    )
    def test_sample_all_tasks_non_empty(self, runner, task_name):
        result = runner.invoke(main, ["sample", task_name, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["sample"]) > 0, f"{task_name} sample is empty"


class TestRunCommand:
    def test_run_text_default(self, runner):
        result = runner.invoke(main, ["run", "--model", "gpt-4o", "--tasks", "paper_comprehension"])
        assert result.exit_code == 0
        assert "ResearchBench" in result.output
        assert "AVERAGE" in result.output

    def test_run_json_to_stdout(self, runner):
        result = runner.invoke(
            main, ["run", "--model", "gpt-4o", "--tasks", "idea_generation", "--format", "json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["model"] == "gpt-4o"
        assert data["n_tasks"] == 1

    def test_run_html_to_stdout(self, runner):
        result = runner.invoke(
            main, ["run", "--model", "gpt-4o", "--tasks", "peer_review", "--format", "html"]
        )
        assert result.exit_code == 0
        assert "<!doctype html>" in result.output.lower()

    def test_run_verbose_adds_details(self, runner):
        plain = runner.invoke(main, ["run", "--tasks", "paper_comprehension", "--model", "gpt-4o"])
        verbose = runner.invoke(
            main, ["run", "--tasks", "paper_comprehension", "--model", "gpt-4o", "--verbose"]
        )
        assert verbose.exit_code == 0
        assert len(verbose.output) > len(plain.output)
        # verbose output references a details key produced by PaperComprehension
        assert "per_paper" in verbose.output

    def test_run_save_to_file(self, runner, tmp_path):
        out = tmp_path / "report.json"
        result = runner.invoke(
            main,
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
                "--format",
                "json",
                "--save",
                str(out),
            ],
        )
        assert result.exit_code == 0
        assert "saved to" in result.output
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["model"] == "gpt-4o"

    def test_run_save_html_to_file(self, runner, tmp_path):
        out = tmp_path / "report.html"
        result = runner.invoke(
            main,
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
                "--format",
                "html",
                "--save",
                str(out),
            ],
        )
        assert result.exit_code == 0
        assert "<!doctype html>" in out.read_text(encoding="utf-8").lower()

    def test_run_unknown_task_errors(self, runner):
        result = runner.invoke(main, ["run", "--tasks", "nope"])
        assert result.exit_code != 0

    def test_run_save_to_missing_dir_errors_cleanly(self, runner, tmp_path):
        bad_dir = tmp_path / "no" / "such" / "dir"
        result = runner.invoke(
            main,
            [
                "run",
                "--tasks",
                "paper_comprehension",
                "--model",
                "gpt-4o",
                "--format",
                "json",
                "--save",
                str(bad_dir / "out.json"),
            ],
        )
        assert result.exit_code != 0
        assert "Error" in result.output
        assert "Traceback" not in result.output

    def test_run_all_tasks(self, runner):
        result = runner.invoke(main, ["run", "--tasks", "all", "--model", "gpt-4o"])
        assert result.exit_code == 0
        assert "AVERAGE" in result.output


class TestCompareCommand:
    def test_compare_text_table(self, runner):
        result = runner.invoke(
            main,
            [
                "compare",
                "--model",
                "gpt-4o",
                "--model",
                "claude-3-opus",
                "--tasks",
                "paper_comprehension",
            ],
        )
        assert result.exit_code == 0
        assert "Comparison" in result.output
        assert "gpt-4o" in result.output
        assert "claude-3-opus" in result.output
        assert "AVERAGE" in result.output

    def test_compare_json(self, runner):
        result = runner.invoke(
            main,
            [
                "compare",
                "--model",
                "gpt-4o",
                "--model",
                "claude-3-opus",
                "--tasks",
                "idea_generation",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["models"] == ["gpt-4o", "claude-3-opus"]
        assert len(data["results"]) == 2
        for entry in data["results"]:
            assert "average" in entry and "per_task" in entry

    def test_compare_html(self, runner):
        result = runner.invoke(
            main,
            [
                "compare",
                "--model",
                "gpt-4o",
                "--model",
                "claude-3-opus",
                "--tasks",
                "peer_review",
                "--format",
                "html",
            ],
        )
        assert result.exit_code == 0
        assert "<table>" in result.output
        assert "gpt-4o" in result.output

    def test_compare_requires_at_least_one_model(self, runner):
        result = runner.invoke(main, ["compare", "--tasks", "paper_comprehension"])
        assert result.exit_code != 0

    def test_compare_save_to_file(self, runner, tmp_path):
        out = tmp_path / "cmp.json"
        result = runner.invoke(
            main,
            [
                "compare",
                "--model",
                "gpt-4o",
                "--model",
                "claude-3-opus",
                "--tasks",
                "paper_comprehension",
                "--format",
                "json",
                "--save",
                str(out),
            ],
        )
        assert result.exit_code == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data["results"]) == 2

    def test_compare_verbose(self, runner):
        plain = runner.invoke(
            main, ["compare", "--model", "gpt-4o", "--tasks", "paper_comprehension"]
        )
        verbose = runner.invoke(
            main, ["compare", "--model", "gpt-4o", "--tasks", "paper_comprehension", "--verbose"]
        )
        assert verbose.exit_code == 0
        assert len(verbose.output) > len(plain.output)
        assert "details" in verbose.output
