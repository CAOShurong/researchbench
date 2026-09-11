"""Human-facing BEOL quiz: score a typed answer with the existing rubric."""

from __future__ import annotations

from typing import Any

from researchbench.dataset_schema import DatasetItem, is_runnable
from researchbench.rubric import Rubric
from researchbench.tasks.heterogeneous_pilot import PILOT_DATASET


def select_items(*, allow_draft: bool = False, item_id: str | None = None) -> list[DatasetItem]:
    """Reviewed pilot items by default; ``item_id`` matches a suffix or full id."""
    items = [item for item in PILOT_DATASET if allow_draft or is_runnable(item)]
    if item_id:
        matched = [item for item in items if item.id == item_id or item.id.endswith(item_id)]
        if not matched:
            known = ", ".join(item.id.split("/")[-1] for item in items)
            raise ValueError(f"unknown item {item_id!r}. Available: {known}")
        return matched
    return items


def score_item(item: DatasetItem, answer: str) -> dict[str, Any]:
    """Score ``answer`` against the item's stored rubric. Does not leak ground truth."""
    raw = item.task_data.get("rubric") or {}
    result = Rubric.from_dict(raw).evaluate(answer)
    return {
        "id": item.id,
        "question": item.task_data.get("question", ""),
        "normalized_score": result.normalized_score,
        "passed": result.passed,
        "criteria": [cs.to_dict() for cs in result.criterion_scores.values()],
    }


def format_text(payload: dict[str, Any], *, reveal: str | None = None) -> str:
    """Human report. ``reveal`` is optional ground-truth text after scoring."""
    lines = [
        payload["id"],
        "",
        payload["question"],
        "",
        f"score  {payload['normalized_score']:.2f} / 100"
        + ("  PASS" if payload["passed"] else "  FAIL"),
        "",
    ]
    for row in payload["criteria"]:
        mark = "ok" if row["passed"] else "miss"
        lines.append(
            f"  [{mark}] {row['criterion_name']}  {row['score']:.2f}/{row['max_score']:.2f}"
        )
        if row["triggered_negatives"]:
            lines.append(f"       hard negative: {', '.join(row['triggered_negatives'])}")
    lines.append("")
    lines.append("Rubric evidence scoring, not an expert grade.")
    if reveal:
        lines.append("")
        lines.append("Ground truth (for study, not a model ranking):")
        lines.append(reveal)
    return "\n".join(lines)
