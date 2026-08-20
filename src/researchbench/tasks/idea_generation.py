"""Idea generation task: evaluate novel research hypothesis generation."""

from typing import Any

CONTEXTS = [
    {
        "id": "few-shot-llm",
        "description": "Large language models can learn new tasks from just a few examples (few-shot learning). However, the mechanism by which they do this is poorly understood. Some argue it's just pattern matching on pretraining data, while others claim it represents true in-context learning. Existing evaluations focus on accuracy but don't probe the underlying mechanism.",
        "question": "Propose a novel research hypothesis about the mechanism of few-shot learning in LLMs, and describe a concrete experiment that would test your hypothesis.",
    },
    {
        "id": "rlhf-alignment",
        "description": "RLHF (Reinforcement Learning from Human Feedback) is the standard method for aligning LLMs with human preferences. However, it's known to reduce output diversity, can lead to sycophancy (telling users what they want to hear), and may not capture nuanced preferences across different cultures and contexts. Alternative alignment methods are an active area of research.",
        "question": "Propose a novel approach to AI alignment that addresses at least one key limitation of RLHF. Describe the core idea, why it would work, and how you would evaluate it.",
    },
]

NOVELTY_KEYWORDS = [
    "novel",
    "hypothesis",
    "propose",
    "framework",
    "approach",
    "method",
    "mechanism",
    "theory",
    "insight",
]
FEASIBILITY_KEYWORDS = [
    "experiment",
    "evaluate",
    "test",
    "measure",
    "dataset",
    "baseline",
    "control",
    "metric",
    "ablation",
]


class IdeaGeneration:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for ctx in CONTEXTS:
            raw = _call_model(model, f"Context: {ctx['description']}\n\nTask: {ctx['question']}")
            novelty = sum(1 for kw in NOVELTY_KEYWORDS if kw in raw.lower())
            feasibility = sum(1 for kw in FEASIBILITY_KEYWORDS if kw in raw.lower())
            length_score = min(len(raw) / 500, 1.0)
            generic_penalty = 1.0
            for phrase in ["further research is needed", "it depends", "more studies"]:
                if phrase in raw.lower():
                    generic_penalty -= 0.15
            score = (
                (min(novelty, 5) / 5 * 0.4 + min(feasibility, 5) / 5 * 0.3 + length_score * 0.3)
                * max(generic_penalty, 0.3)
                * 100
            )
            total += score
            details[ctx["id"]] = {
                "score": round(score, 1),
                "length": len(raw),
                "novelty_terms": novelty,
                "feasibility_terms": feasibility,
            }
        avg = total / len(CONTEXTS)
        return avg, {"per_context": details, "average": round(avg, 1)}


def _call_model(model: str, prompt: str) -> str:
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Mock hypothesis: I propose that few-shot learning in LLMs operates through a meta-learning mechanism where the model dynamically constructs task-specific representations in its hidden states. To test this, I would conduct an experiment measuring representational similarity across different few-shot prompts using probing classifiers and control for pretraining data overlap."
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Mock: I hypothesize that RLHF's diversity reduction stems from reward model overfitting to majority preferences. A novel approach would be to train an ensemble of reward models capturing diverse preference distributions."
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock research hypothesis for evaluation."
