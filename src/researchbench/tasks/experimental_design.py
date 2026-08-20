"""Experimental design task: evaluate ability to design valid experiments."""

from typing import Any

HYPOTHESES = [
    {
        "id": "drug-efficacy",
        "hypothesis": "A new drug Compound X reduces tumor growth in mice by at least 50% compared to placebo, through inhibition of the Y receptor pathway.",
        "question": "Design a rigorous experiment to test this hypothesis. Specify: (1) control conditions, (2) sample size and power analysis, (3) dependent and independent variables, (4) potential confounders and how to control them, (5) statistical analysis plan, (6) expected results and interpretation.",
        "keywords": [
            "control",
            "placebo",
            "random",
            "sample size",
            "power",
            "blinding",
            "randomization",
            "independent",
            "dependent",
            "variable",
            "confound",
            "t-test",
            "ANOVA",
            "regression",
            "statistical",
            "p-value",
            "effect size",
            "replication",
        ],
    },
    {
        "id": "nlp-model",
        "hypothesis": "A new attention mechanism with adaptive sparsity improves long-document summarization quality over standard transformers, while using less compute.",
        "question": "Design a rigorous experiment to test this hypothesis. Specify: (1) datasets and evaluation metrics, (2) baseline models, (3) control conditions, (4) statistical significance testing, (5) ablation studies needed, (6) potential confounding factors.",
        "keywords": [
            "dataset",
            "metric",
            "ROUGE",
            "BLEU",
            "baseline",
            "transformer",
            "ablation",
            "significance",
            "compute",
            "efficiency",
            "document",
            "long",
            "confound",
            "reproducibility",
            "hyperparameter",
        ],
    },
]


class ExperimentalDesign:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for h in HYPOTHESES:
            raw = _call_model(model, f"Hypothesis: {h['hypothesis']}\n\nTask: {h['question']}")
            kw_count = sum(1 for kw in h["keywords"] if kw.lower() in raw.lower())
            max_kw = len(h["keywords"])
            coverage = min(kw_count / max_kw * 2, 1.0)
            length_score = min(len(raw) / 600, 1.0)
            sections = sum(
                1
                for s in ["control", "sample", "statistical", "confound", "interpret"]
                if s in raw.lower()
            )
            completeness = sections / 5.0
            score = (coverage * 0.35 + length_score * 0.25 + completeness * 0.4) * 100
            total += score
            details[h["id"]] = {
                "score": round(score, 1),
                "keyword_coverage": kw_count,
                "sections": sections,
                "length": len(raw),
            }
        avg = total / len(HYPOTHESES)
        return avg, {"per_hypothesis": details, "average": round(avg, 1)}


def _call_model(model: str, prompt: str) -> str:
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Mock experimental design: I would use a randomized controlled trial with 100 mice per group, double-blinded. The independent variable is drug dose, dependent variable is tumor volume. Confounders include mouse age, weight, and baseline health. Statistical analysis: two-way ANOVA with post-hoc tests."
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Mock: Use standard summarization datasets (CNN/DailyMail, arXiv, GovReport). Baselines: BART, Longformer, standard transformer. Metrics: ROUGE, BERTScore, human evaluation. Ablation: remove adaptive sparsity to measure its contribution."
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock experimental design for evaluation."
