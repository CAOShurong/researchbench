"""Evidence-based rubric evaluator and human calibration pack (RESEARCH_BENCHMARK.md).

Replaces naive keyword/substring matching with structured criteria evaluation:
- Weighted rubric criteria with required evidence spans and negative indicators.
- Per-criterion audit scores, match explanations, and failure diagnosis.
- Blinded output generator for inter-annotator human calibration studies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Criterion:
    """A single evaluation criterion within an evidence-based rubric."""

    name: str
    description: str
    weight: float = 1.0
    evidence_patterns: list[str] = field(default_factory=list)
    negative_patterns: list[str] = field(default_factory=list)

    def evaluate(self, text: str) -> CriterionScore:
        """Evaluate a text response against this criterion."""
        lowered = text.lower()
        matched_evidence: list[str] = []
        triggered_negatives: list[str] = []

        for pat in self.evidence_patterns:
            if re.search(pat, lowered, re.IGNORECASE):
                matched_evidence.append(pat)

        for neg in self.negative_patterns:
            if re.search(neg, lowered, re.IGNORECASE):
                triggered_negatives.append(neg)

        # Calculate score: evidence coverage minus penalty for hard negatives
        if not self.evidence_patterns:
            base_ratio = 1.0
        else:
            base_ratio = len(matched_evidence) / len(self.evidence_patterns)

        # Negative indicators subtract proportionally (half credit per negative violation)
        neg_penalty = 0.5 * len(triggered_negatives)
        raw_score = max(0.0, (base_ratio - neg_penalty) * self.weight)

        return CriterionScore(
            criterion_name=self.name,
            score=round(raw_score, 3),
            max_score=self.weight,
            matched_evidence=matched_evidence,
            triggered_negatives=triggered_negatives,
            passed=(raw_score >= 0.6 * self.weight) and (len(triggered_negatives) == 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "evidence_patterns": self.evidence_patterns,
            "negative_patterns": self.negative_patterns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Criterion:
        return cls(
            name=data["name"],
            description=data["description"],
            weight=float(data.get("weight", 1.0)),
            evidence_patterns=list(data.get("evidence_patterns", [])),
            negative_patterns=list(data.get("negative_patterns", [])),
        )


@dataclass
class CriterionScore:
    """Scoring audit breakdown for a single criterion."""

    criterion_name: str
    score: float
    max_score: float
    matched_evidence: list[str]
    triggered_negatives: list[str]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_name": self.criterion_name,
            "score": self.score,
            "max_score": self.max_score,
            "matched_evidence": self.matched_evidence,
            "triggered_negatives": self.triggered_negatives,
            "passed": self.passed,
        }


@dataclass
class RubricResult:
    """Overall result of evaluating a response with a structured rubric."""

    total_score: float
    max_score: float
    normalized_score: float  # 0.0 to 100.0
    passed: bool
    criterion_scores: dict[str, CriterionScore]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "max_score": self.max_score,
            "normalized_score": self.normalized_score,
            "passed": self.passed,
            "criterion_scores": {k: v.to_dict() for k, v in self.criterion_scores.items()},
        }


@dataclass
class Rubric:
    """Structured rubric containing multiple criteria."""

    criteria: list[Criterion] = field(default_factory=list)
    passing_threshold: float = 60.0  # percentage

    def evaluate(self, response: str) -> RubricResult:
        """Evaluate a text response across all criteria."""
        total_score = 0.0
        max_score = 0.0
        scores: dict[str, CriterionScore] = {}

        for c in self.criteria:
            res = c.evaluate(response)
            scores[c.name] = res
            total_score += res.score
            max_score += res.max_score

        norm = (total_score / max_score * 100.0) if max_score > 0 else 0.0
        all_passed = all(cs.passed for cs in scores.values()) and (norm >= self.passing_threshold)

        return RubricResult(
            total_score=round(total_score, 3),
            max_score=round(max_score, 3),
            normalized_score=round(norm, 2),
            passed=all_passed,
            criterion_scores=scores,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "passing_threshold": self.passing_threshold,
            "criteria": [c.to_dict() for c in self.criteria],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Rubric:
        return cls(
            criteria=[Criterion.from_dict(c) for c in data.get("criteria", [])],
            passing_threshold=float(data.get("passing_threshold", 60.0)),
        )


def export_blinded_calibration_pack(
    items: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate blinded evaluation pack for human expert calibration studies."""
    import random

    rng = random.Random(seed)
    calibration_records: list[dict[str, Any]] = []

    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in responses:
        grouped.setdefault(r["item_id"], []).append(r)

    for it in items:
        item_id = it["id"]
        item_responses = grouped.get(item_id, [])
        if not item_responses:
            continue

        shuffled = list(item_responses)
        rng.shuffle(shuffled)

        blinded_variants = []
        for idx, resp in enumerate(shuffled):
            blinded_variants.append(
                {
                    "variant_label": chr(65 + idx),
                    "response_text": resp.get("output", ""),
                    "blinded_id": f"BLIND-{item_id}-{idx + 1}",
                }
            )

        calibration_records.append(
            {
                "item_id": item_id,
                "prompt": it.get("task_data", {}).get("question", ""),
                "rubric": it.get("task_data", {}).get("rubric", {}),
                "variants": blinded_variants,
            }
        )

    return calibration_records
