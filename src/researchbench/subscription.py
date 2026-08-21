"""Subscription-mode evaluation protocol (RESEARCH_BENCHMARK.md Section 6.1).

Defines data structures for recording evaluations of subscription-based AI
products (ChatGPT, Claude, Codex, etc.) and raw API runs as first-class
benchmark targets. Supports import/export/validate via a stable JSON contract
that both ResearchBench and the separate SciModelMatrix project can consume.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# ---- Mandatory field sets ----------------------------------------------------

_SUB_MANDATORY = ("product", "prompt", "run_date", "full_output")
_API_MANDATORY = ("provider", "model_id", "prompt", "run_date", "full_output")
_RECORD_MANDATORY = ("benchmark_version", "task_id")


@dataclass
class SubscriptionRun:
    """A single evaluation run against a subscription-based AI product."""

    product: str
    reasoning_mode: str = "unknown"
    browsing: bool = False
    tool_access: list[str] = field(default_factory=list)
    context_supplied: str = "none"
    session_policy: str = "fresh_conversation"
    prompt: str = ""
    max_interactions: int = 1
    time_limit_seconds: int | None = None
    human_intervention: str = "none"
    run_date: str = ""
    full_output: str = ""
    cited_sources: list[str] = field(default_factory=list)
    observable_metrics: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": "subscription",
            "product": self.product,
            "reasoning_mode": self.reasoning_mode,
            "browsing": self.browsing,
            "tool_access": self.tool_access,
            "context_supplied": self.context_supplied,
            "session_policy": self.session_policy,
            "prompt": self.prompt,
            "max_interactions": self.max_interactions,
            "time_limit_seconds": self.time_limit_seconds,
            "human_intervention": self.human_intervention,
            "run_date": self.run_date,
            "full_output": self.full_output,
            "cited_sources": self.cited_sources,
            "observable_metrics": self.observable_metrics,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> SubscriptionRun:
        return SubscriptionRun(
            product=d.get("product", ""),
            reasoning_mode=d.get("reasoning_mode", "unknown"),
            browsing=d.get("browsing", False),
            tool_access=d.get("tool_access", []),
            context_supplied=d.get("context_supplied", "none"),
            session_policy=d.get("session_policy", "fresh_conversation"),
            prompt=d.get("prompt", ""),
            max_interactions=d.get("max_interactions", 1),
            time_limit_seconds=d.get("time_limit_seconds"),
            human_intervention=d.get("human_intervention", "none"),
            run_date=d.get("run_date", ""),
            full_output=d.get("full_output", ""),
            cited_sources=d.get("cited_sources", []),
            observable_metrics=d.get("observable_metrics", {}),
            notes=d.get("notes", ""),
        )


@dataclass
class APIRun:
    """A single evaluation run against a raw API."""

    provider: str
    model_id: str
    api_params: dict[str, Any] = field(default_factory=dict)
    context_supplied: str = "none"
    prompt: str = ""
    full_output: str = ""
    cited_sources: list[str] = field(default_factory=list)
    cost_usd: float | None = None
    run_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": "api",
            "provider": self.provider,
            "model_id": self.model_id,
            "api_params": self.api_params,
            "context_supplied": self.context_supplied,
            "prompt": self.prompt,
            "full_output": self.full_output,
            "cited_sources": self.cited_sources,
            "cost_usd": self.cost_usd,
            "run_date": self.run_date,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> APIRun:
        return APIRun(
            provider=d.get("provider", ""),
            model_id=d.get("model_id", ""),
            api_params=d.get("api_params", {}),
            context_supplied=d.get("context_supplied", "none"),
            prompt=d.get("prompt", ""),
            full_output=d.get("full_output", ""),
            cited_sources=d.get("cited_sources", []),
            cost_usd=d.get("cost_usd"),
            run_date=d.get("run_date", ""),
        )


@dataclass
class RunRecord:
    """A complete run record per RESEARCH_BENCHMARK.md Section 7.1.

    A subscription run and an API run are separate experimental conditions
    and must never be silently mixed.
    """

    benchmark_version: str
    task_id: str
    subscription_run: SubscriptionRun | None = None
    api_run: APIRun | None = None
    evaluation_result: dict[str, Any] = field(default_factory=dict)
    evaluator_version: str = ""
    failures_or_timeouts: str = ""
    notes: str = ""

    def __post_init__(self):
        if self.subscription_run is None and self.api_run is None:
            raise ValueError("RunRecord requires either subscription_run or api_run")
        if self.subscription_run is not None and self.api_run is not None:
            raise ValueError(
                "RunRecord cannot have both subscription_run and api_run — "
                "they are separate experimental conditions (RESEARCH_BENCHMARK.md §6.3)"
            )

    def to_dict(self) -> dict[str, Any]:
        run = self.subscription_run.to_dict() if self.subscription_run else self.api_run.to_dict()  # type: ignore[union-attr]
        return {
            "benchmark_version": self.benchmark_version,
            "task_id": self.task_id,
            "run": run,
            "evaluation_result": self.evaluation_result,
            "evaluator_version": self.evaluator_version,
            "failures_or_timeouts": self.failures_or_timeouts,
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> RunRecord:
        run_dict = d.get("run", {})
        mode = run_dict.get("mode", "")
        sub_run: SubscriptionRun | None = None
        api_run: APIRun | None = None
        if mode == "subscription":
            sub_run = SubscriptionRun.from_dict(run_dict)
        elif mode == "api":
            api_run = APIRun.from_dict(run_dict)
        else:
            raise ValueError(f"run.mode must be 'subscription' or 'api', got '{mode}'")
        return RunRecord(
            benchmark_version=d.get("benchmark_version", ""),
            task_id=d.get("task_id", ""),
            subscription_run=sub_run,
            api_run=api_run,
            evaluation_result=d.get("evaluation_result", {}),
            evaluator_version=d.get("evaluator_version", ""),
            failures_or_timeouts=d.get("failures_or_timeouts", ""),
            notes=d.get("notes", ""),
        )

    @staticmethod
    def from_json(s: str) -> RunRecord:
        return RunRecord.from_dict(json.loads(s))


def validate_run_record(record: RunRecord) -> list[str]:
    """Validate a RunRecord's mandatory fields. Returns list of errors (empty=valid)."""
    errors: list[str] = []

    for field_name in _RECORD_MANDATORY:
        val = getattr(record, field_name, "")
        if not val:
            errors.append(f"{field_name} is required")

    run = record.subscription_run or record.api_run
    if run is None:
        errors.append("either subscription_run or api_run is required")
        return errors

    mandatory = _SUB_MANDATORY if isinstance(run, SubscriptionRun) else _API_MANDATORY
    run_dict = run.to_dict()
    for f in mandatory:
        val = run_dict.get(f, "")
        if not val:
            errors.append(f"run.{f} is required (must not be empty)")

    if not record.evaluator_version:
        errors.append("evaluator_version is required")

    return errors