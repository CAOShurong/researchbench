"""Dataset item schema (RESEARCH_BENCHMARK.md Section 4.2).

Defines the mandatory per-item metadata structure for benchmark dataset items.
Every dataset item must carry this metadata to make rigorous evaluation possible.

This is a data definition module — it does not contain scoring logic. It
defines what a valid dataset item looks like so that:
- item authors know what fields to provide;
- the evaluation framework can validate items before use;
- downstream consumers can inspect item provenance and contamination risk.

Usage:
    from researchbench.dataset_schema import DatasetItem, validate_item

    item = DatasetItem(
        id="paper_comprehension/attention-2017/q1",
        capability_tags=["C5", "C1"],
        ground_truth="The Transformer replaces recurrence and convolution with
                       self-attention; key limitation is quadratic complexity.",
        ground_truth_source="expert: ML researcher, verified against the paper",
        scoring_method="rubric",
        contamination_risk="high",
        hard_negatives=[],
        expert_notes="Classic paper; likely in training data. Use for
                       methodology critique, not factual recall.",
    )
    errors = validate_item(item)
    assert not errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# All 16 capabilities from RESEARCH_BENCHMARK.md Section 3
VALID_CAPABILITIES = {
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "C8",
    "C9",
    "C10",
    "C11",
    "C12",
    "C13",
    "C14",
    "C15",
    "C16",
}

VALID_SCORING_METHODS = {
    "exact_match",
    "rubric",
    "llm_judge",
    "human_panel",
    "later_paper_validation",
    "keyword_match_placeholder",
}

VALID_CONTAMINATION_RISK = {"low", "medium", "high"}


@dataclass
class DatasetItem:
    """A single benchmark dataset item with mandatory metadata."""

    id: str
    capability_tags: list[str]
    ground_truth: str
    ground_truth_source: str
    scoring_method: str
    contamination_risk: str = "medium"
    hard_negatives: list[dict[str, Any]] = field(default_factory=list)
    expert_notes: str = ""
    version: str = "1.0"
    # The actual task data (prompts, paper texts, etc.)
    task_data: dict[str, Any] = field(default_factory=dict)


def validate_item(item: DatasetItem) -> list[str]:
    """Validate a dataset item. Returns a list of error strings (empty = valid)."""
    errors: list[str] = []

    if not item.id:
        errors.append("id is required")

    if not item.capability_tags:
        errors.append("capability_tags is required (at least one of C1–C16)")
    else:
        invalid = [t for t in item.capability_tags if t not in VALID_CAPABILITIES]
        if invalid:
            errors.append(
                f"invalid capability_tags: {invalid}. Valid: {sorted(VALID_CAPABILITIES)}"
            )

    if not item.ground_truth:
        errors.append("ground_truth is required")

    if not item.ground_truth_source:
        errors.append("ground_truth_source is required (who produced it and how)")

    if item.scoring_method not in VALID_SCORING_METHODS:
        errors.append(
            f"invalid scoring_method: '{item.scoring_method}'. "
            f"Valid: {sorted(VALID_SCORING_METHODS)}"
        )

    if item.contamination_risk not in VALID_CONTAMINATION_RISK:
        errors.append(
            f"invalid contamination_risk: '{item.contamination_risk}'. "
            f"Valid: {sorted(VALID_CONTAMINATION_RISK)}"
        )

    return errors
