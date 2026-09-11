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


def item_suffix(item: DatasetItem) -> str:
    return item.id.split("/")[-1]


def list_items_text(items: list[DatasetItem]) -> str:
    """Questions only. Never includes ground truth."""
    lines = [f"{len(items)} BEOL quiz item(s). Rubric scoring, not an expert grade.", ""]
    for item in items:
        lines.append(item_suffix(item))
        lines.append(str(item.task_data.get("question", "")).strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_answers_file(path: str) -> dict[str, str]:
    """JSONL rows ``{"id": "q1", "answer": "..."}``. Keys may be suffix or full id."""
    import json
    from pathlib import Path

    text = Path(path).read_text(encoding="utf-8")
    answers: dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: not JSON") from exc
        key = row.get("id") if isinstance(row, dict) else None
        answer = row.get("answer") if isinstance(row, dict) else None
        if not isinstance(key, str) or not key.strip() or not isinstance(answer, str):
            raise ValueError(f"{path}:{lineno}: need string id and answer")
        answers[key.strip()] = answer
    if not answers:
        raise ValueError(f"{path}: no answers")
    return answers


def score_session(items: list[DatasetItem], answers: dict[str, str]) -> dict[str, Any]:
    """Score every item. Missing ids count as an empty answer (score 0)."""
    rows: list[dict[str, Any]] = []
    for item in items:
        suffix = item_suffix(item)
        answer = answers.get(item.id) or answers.get(suffix) or ""
        rows.append(score_item(item, answer))
    scores = [row["normalized_score"] for row in rows]
    mean = sum(scores) / len(scores) if scores else 0.0
    return {
        "count": len(rows),
        "mean": round(mean, 2),
        "passed": sum(1 for row in rows if row["passed"]),
        "items": rows,
    }


def format_session_text(session: dict[str, Any]) -> str:
    lines = [
        (
            f"BEOL quiz  {session['passed']}/{session['count']} passed  "
            f"mean {session['mean']:.2f} / 100"
        ),
        "",
        "Rubric evidence scoring, not an expert grade.",
        "",
    ]
    for row in session["items"]:
        mark = "PASS" if row["passed"] else "FAIL"
        lines.append(
            f"  {item_suffix_from_id(row['id']):<4}  {row['normalized_score']:6.2f}  {mark}"
        )
    return "\n".join(lines) + "\n"


def item_suffix_from_id(item_id: str) -> str:
    return item_id.split("/")[-1]


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
