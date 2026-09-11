"""Non-interactive BEOL quiz scoring."""

import json

from click.testing import CliRunner

from researchbench.cli import main
from researchbench.quiz import score_item, select_items


def test_select_items_defaults_to_reviewed_only():
    items = select_items()
    assert items
    assert all(item.id.split("/")[-1] != "q6" for item in items)


def test_select_item_q1():
    items = select_items(item_id="q1")
    assert len(items) == 1
    assert items[0].id.endswith("q1")


def test_empty_answer_scores_low():
    item = select_items(item_id="q1")[0]
    payload = score_item(item, "")
    assert payload["normalized_score"] == 0.0
    assert payload["passed"] is False
    assert "ground_truth" not in payload


def test_cli_quiz_json_does_not_leak_ground_truth():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "quiz",
            "--item",
            "q1",
            "--format",
            "json",
            "--answer",
            "400 deg C thermal budget copper diffusion electromigration low-k dopant FEOL",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["normalized_score"] > 0
    assert "ground_truth" not in data
    assert "beol" in data["question"].lower()


def test_cli_quiz_requires_answer_without_tty():
    runner = CliRunner()
    result = runner.invoke(main, ["quiz", "--item", "q1"])
    assert result.exit_code != 0
    assert "--answer" in result.output


def test_quiz_list_prints_questions_not_ground_truth():
    runner = CliRunner()
    result = runner.invoke(main, ["quiz", "--list"])
    assert result.exit_code == 0, result.output
    assert "q1" in result.output
    assert "q6" not in result.output
    assert "ground truth" not in result.output.lower()
    assert "BEOL" in result.output or "beol" in result.output.lower()


def test_quiz_answers_file_scores_session(tmp_path):
    path = tmp_path / "answers.jsonl"
    path.write_text(
        '{"id": "q1", "answer": "400 C thermal budget copper diffusion electromigration low-k dopant FEOL"}\n'
        '{"id": "q2", "answer": ""}\n',
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["quiz", "--answers-file", str(path), "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["count"] >= 2
    assert "items" in data
    assert data["items"][0]["normalized_score"] > 0
    assert all("ground_truth" not in row for row in data["items"])


def test_load_answers_file_rejects_empty(tmp_path):
    from researchbench.quiz import load_answers_file

    path = tmp_path / "empty.jsonl"
    path.write_text("# comment only\n", encoding="utf-8")
    try:
        load_answers_file(str(path))
    except ValueError as exc:
        assert "no answers" in str(exc)
    else:
        raise AssertionError("expected ValueError")
