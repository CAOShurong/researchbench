"""Subscription-mode evaluation protocol (RESEARCH_BENCHMARK.md Section 6.1).

This module defines the data structures for recording evaluations of
subscription-based AI products (ChatGPT, Claude, Codex, etc.) as first-class
benchmark targets. Unlike API-mode runs, subscription products do not expose
token counts, temperature, or internal compute — only the observable output.

Usage:
    from researchbench.subscription import SubscriptionRun, RunRecord

    run = SubscriptionRun(
        product="ChatGPT (GPT-4o)",
        reasoning_mode="auto",
        browsing=True,
        tool_access=["web_search", "code_interpreter"],
        context_supplied="abstract_only",
        session_policy="fresh_conversation",
        prompt="What is the core contribution of this paper?",
        max_interactions=1,
        time_limit_seconds=120,
        human_intervention="none",
        run_date="2026-08-21T12:00:00Z",
        full_output="The paper introduces...",
        cited_sources=["https://arxiv.org/abs/1706.03762"],
    )
    record = RunRecord(
        benchmark_version="0.1.0",
        task_id="paper_comprehension/attention-2017/q1",
        subscription_run=run,
        evaluation_result={"score": 75.0, "evaluator_version": "keyword-matching-v0.1"},
    )
    print(record.to_json())
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


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
