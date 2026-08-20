"""Open question identification task: evaluate ability to identify open questions."""

from typing import Any

PAPER_SETS = [
    {
        "id": "llm-evaluation",
        "papers": [
            "Paper 1: LLMs achieve high accuracy on existing benchmarks but are vulnerable to distribution shift and adversarial examples.",
            "Paper 2: Human evaluation of LLM outputs shows poor correlation with automatic metrics, especially for creative tasks.",
            "Paper 3: Current benchmarks have significant data contamination issues - many test examples appear in training data.",
            "Paper 4: LLM performance varies significantly across languages and cultures, with most benchmarks focused on English.",
        ],
        "question": "Based on these papers, identify the single most important open question in LLM evaluation. Explain why it's important, what progress has been made, and what would need to be done to answer it.",
        "keywords": [
            "benchmark",
            "evaluation",
            "contamination",
            "human",
            "correlation",
            "metric",
            "diverse",
            "language",
            "culture",
            "robust",
            "distribution",
            "shift",
            "adversarial",
            "open question",
            "future",
            "direction",
        ],
    },
    {
        "id": "model-interpretability",
        "papers": [
            "Paper 1: Mechanistic interpretability has identified specific circuits in small transformers that implement particular behaviors.",
            "Paper 2: Current interpretability methods do not scale well to models with billions of parameters.",
            "Paper 3: There is a gap between interpretability findings and practical improvements in model safety or reliability.",
            "Paper 4: Feature visualization and probing methods can be misleading and may not reflect how models actually compute.",
        ],
        "question": "Based on these papers, identify the single most important open question in model interpretability. Explain why it's important, what progress has been made, and what would need to be done to answer it.",
        "keywords": [
            "interpretability",
            "mechanistic",
            "circuit",
            "scale",
            "safety",
            "reliability",
            "practical",
            "gap",
            "probing",
            "limitation",
            "scaling",
            "verification",
            "causal",
            "intervention",
            "open question",
            "future",
        ],
    },
]


class OpenQuestionId:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for ps in PAPER_SETS:
            paper_text = "\n".join(ps["papers"])
            raw = _call_model(model, f"Research Context:\n{paper_text}\n\nTask: {ps['question']}")
            kw_count = sum(1 for kw in ps["keywords"] if kw.lower() in raw.lower())
            max_kw = len(ps["keywords"])
            coverage = min(kw_count / max_kw * 2, 1.0)
            has_importance = any(
                w in raw.lower() for w in ["important", "critical", "key", "fundamental", "crucial"]
            )
            has_progress = any(
                w in raw.lower() for w in ["progress", "work", "known", "existing", "current"]
            )
            has_future = any(
                w in raw.lower() for w in ["future", "next", "would", "could", "need", "direction"]
            )
            quality = sum([has_importance, has_progress, has_future]) / 3.0
            length_score = min(len(raw) / 400, 1.0)
            score = (coverage * 0.35 + quality * 0.4 + length_score * 0.25) * 100
            total += score
            details[ps["id"]] = {
                "score": round(score, 1),
                "keyword_coverage": kw_count,
                "has_importance": has_importance,
                "has_future": has_future,
                "length": len(raw),
            }
        avg = total / len(PAPER_SETS)
        return avg, {"per_set": details, "average": round(avg, 1)}


def _call_model(model: str, prompt: str) -> str:
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "The most important open question is how to create benchmarks that resist contamination and correlate with human judgment. Progress has been made on detecting contamination, but solving it requires dynamic evaluation. Future work should focus on procedurally generated benchmarks."
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "The critical open question is whether interpretability findings from small models transfer to large models. Current methods don't scale. Answering this requires developing scalable verification techniques and testing whether circuit-level understanding improves safety."
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock open question analysis for evaluation."
