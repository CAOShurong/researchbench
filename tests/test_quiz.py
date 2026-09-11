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
