"""Tests for the subscription-mode evaluation protocol (RESEARCH_BENCHMARK.md §6)."""

import json

import pytest

from researchbench.subscription import APIRun, RunRecord, SubscriptionRun


class TestSubscriptionRun:
    def test_to_dict_fields(self):
        run = SubscriptionRun(
            product="ChatGPT (GPT-4o)",
            reasoning_mode="auto",
            browsing=True,
            tool_access=["web_search", "code_interpreter"],
            context_supplied="abstract_only",
            prompt="What is the core contribution?",
            run_date="2026-08-21T12:00:00Z",
            full_output="The Transformer architecture...",
            cited_sources=["https://arxiv.org/abs/1706.03762"],
        )
        d = run.to_dict()
        assert d["mode"] == "subscription"
        assert d["product"] == "ChatGPT (GPT-4o)"
        assert d["browsing"] is True
        assert "web_search" in d["tool_access"]
        assert d["full_output"] != ""
        assert len(d["cited_sources"]) == 1

    def test_defaults(self):
        run = SubscriptionRun(product="Claude (Sonnet 4)")
        d = run.to_dict()
        assert d["reasoning_mode"] == "unknown"
        assert d["browsing"] is False
        assert d["max_interactions"] == 1
        assert d["human_intervention"] == "none"


class TestAPIRun:
    def test_to_dict_fields(self):
        run = APIRun(
            provider="openai",
            model_id="gpt-4o-2024-11-20",
            api_params={"temperature": 0.0, "max_tokens": 512},
            prompt="What is the core contribution?",
            full_output="The Transformer...",
            cost_usd=0.012,
            run_date="2026-08-21T12:00:00Z",
        )
        d = run.to_dict()
        assert d["mode"] == "api"
        assert d["model_id"] == "gpt-4o-2024-11-20"
        assert d["api_params"]["temperature"] == 0.0
        assert d["cost_usd"] == 0.012


class TestRunRecord:
    def test_subscription_record(self):
        run = SubscriptionRun(product="ChatGPT (GPT-4o)", full_output="answer")
        record = RunRecord(
            benchmark_version="0.1.0",
            task_id="paper_comprehension/attention-2017/q1",
            subscription_run=run,
            evaluation_result={"score": 75.0},
            evaluator_version="keyword-matching-v0.1",
        )
        d = record.to_dict()
        assert d["benchmark_version"] == "0.1.0"
        assert d["task_id"] == "paper_comprehension/attention-2017/q1"
        assert d["run"]["mode"] == "subscription"
        assert d["run"]["product"] == "ChatGPT (GPT-4o)"
        assert d["evaluation_result"]["score"] == 75.0
        assert d["evaluator_version"] == "keyword-matching-v0.1"

    def test_api_record(self):
        run = APIRun(provider="openai", model_id="gpt-4o", full_output="answer")
        record = RunRecord(
            benchmark_version="0.1.0",
            task_id="idea_generation/few-shot-llm",
            api_run=run,
            evaluation_result={"score": 64.5},
        )
        d = record.to_dict()
        assert d["run"]["mode"] == "api"
        assert d["run"]["provider"] == "openai"

    def test_json_serializable(self):
        run = SubscriptionRun(product="ChatGPT", full_output="answer")
        record = RunRecord(
            benchmark_version="0.1.0",
            task_id="test/task",
            subscription_run=run,
            evaluation_result={"score": 50.0},
        )
        js = record.to_json()
        data = json.loads(js)
        assert data["run"]["product"] == "ChatGPT"

    def test_cannot_mix_subscription_and_api(self):
        """RESEARCH_BENCHMARK.md §6.3: subscription and API are separate conditions."""
        sub = SubscriptionRun(product="ChatGPT")
        api = APIRun(provider="openai", model_id="gpt-4o")
        with pytest.raises(ValueError, match="separate experimental conditions"):
            RunRecord(benchmark_version="0.1.0", task_id="test", subscription_run=sub, api_run=api)

    def test_requires_at_least_one_run(self):
        with pytest.raises(ValueError, match="requires either"):
            RunRecord(benchmark_version="0.1.0", task_id="test")
