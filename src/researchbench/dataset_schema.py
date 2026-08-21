"""Dataset item schema (RESEARCH_BENCHMARK.md Section 4.2).

Defines the mandatory per-item metadata structure for benchmark dataset items.
Every dataset item must carry this metadata to make rigorous evaluation possible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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

VALID_SOURCE_TYPES = {
    "paper",
    "expert",
    "author_confirmed",
    "later_paper",
    "expert_curated",
    "synthetic",
}

VALID_REVIEW_STATUS = {"draft", "reviewed", "validated", "rejected"}

RUNNABLE_REVIEW_STATUS = {"reviewed", "validated"}


@dataclass
class Provenance:
    """Verifiable provenance for a dataset item."""

    source_id: str
    source_type: str = "paper"
    license: str = "unknown"
    author_role: str = ""
    reviewer_role: str = ""
    review_status: str = "draft"
    review_notes: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "license": self.license,
            "author_role": self.author_role,
            "reviewer_role": self.reviewer_role,
            "review_status": self.review_status,
            "review_notes": self.review_notes,
        }


@dataclass
class DatasetItem:
    """A single benchmark dataset item with mandatory metadata."""

    id: str
    capability_tags: list[str]
    ground_truth: str
    ground_truth_source: str
    scoring_method: str
    contamination_risk: str = "medium"
    provenance: Provenance | None = None
    hard_negatives: list[dict[str, Any]] = field(default_factory=list)
    expert_notes: str = ""
    version: str = "1.0"
    task_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "capability_tags": self.capability_tags,
            "ground_truth": self.ground_truth,
            "ground_truth_source": self.ground_truth_source,
            "scoring_method": self.scoring_method,
            "contamination_risk": self.contamination_risk,
            "hard_negatives": self.hard_negatives,
            "expert_notes": self.expert_notes,
            "version": self.version,
            "task_data": self.task_data,
        }
        if self.provenance is not None:
            d["provenance"] = self.provenance.to_dict()
        return d


def validate_item(item: DatasetItem) -> list[str]:
    """Validate a dataset item. Returns a list of error strings (empty = valid)."""
    errors: list[str] = []

    if not item.id:
        errors.append("id is required")

    if not item.capability_tags:
        errors.append("capability_tags is required (at least one of C1-C16)")
    else:
        invalid = [t for t in item.capability_tags if t not in VALID_CAPABILITIES]
        if invalid:
            errors.append(
                f"invalid capability_tags: {invalid}. Valid: {sorted(VALID_CAPABILITIES)}"
            )

    if not item.ground_truth:
        errors.append("ground_truth is required")

    if not item.ground_truth_source:
        errors.append("ground_truth_source is required")

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

    # Provenance is REQUIRED for all items
    if item.provenance is None:
        errors.append("provenance is required (must not be None)")
    else:
        p = item.provenance
        if not p.source_id:
            errors.append("provenance.source_id is required")
        if p.source_type not in VALID_SOURCE_TYPES:
            errors.append(
                f"invalid provenance.source_type: '{p.source_type}'. "
                f"Valid: {sorted(VALID_SOURCE_TYPES)}"
            )
        if not p.license or p.license == "unknown":
            errors.append("provenance.license is required and must not be 'unknown'")
        if not p.author_role:
            errors.append("provenance.author_role is required")
        if not p.reviewer_role and p.review_status in RUNNABLE_REVIEW_STATUS:
            errors.append("provenance.reviewer_role is required for reviewed/validated items")
        if p.review_status not in VALID_REVIEW_STATUS:
            errors.append(
                f"invalid provenance.review_status: '{p.review_status}'. "
                f"Valid: {sorted(VALID_REVIEW_STATUS)}"
            )

    return errors


def is_runnable(item: DatasetItem) -> bool:
    """Return True if the item's review_status allows it to be run as a benchmark item."""
    if item.provenance is None:
        return False
    return item.provenance.review_status in RUNNABLE_REVIEW_STATUS
