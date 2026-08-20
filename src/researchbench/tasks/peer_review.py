"""Peer review task: evaluate ability to write constructive peer reviews."""

from typing import Any

MOCK_SUBMISSIONS = [
    {
        "id": "weak-baseline",
        "title": "Improving Text Classification with a Novel Attention Mechanism",
        "abstract": "We propose a new attention mechanism for text classification. Our model achieves 94.2% accuracy on the IMDB dataset, outperforming the previous state-of-the-art of 94.0%. We evaluate on three datasets and show consistent improvements. Our attention mechanism is simple and can be added to any existing model.",
        "known_flaws": [
            "Only 0.2% improvement over SOTA - not statistically significant",
            "No statistical significance testing reported",
            "Only evaluates on 3 datasets, all sentiment analysis",
            "No comparison to compute costs or parameter counts",
            "Does not test on out-of-distribution samples",
            "No ablation study to isolate the contribution of the attention mechanism",
        ],
        "question": "Write a peer review of this paper. Identify at least 3 specific weaknesses, suggest concrete improvements, and give an overall recommendation (accept, minor revision, major revision, reject).",
        "keywords": [
            "statistical significance",
            "baseline",
            "limited",
            "generalization",
            "ablation",
            "improvement",
            "margin",
            "comparison",
            "compute",
            "robustness",
            "reproducibility",
        ],
    },
    {
        "id": "missing-details",
        "title": "Zero-Shot Learning for Medical Image Diagnosis",
        "abstract": "We apply zero-shot learning to medical image diagnosis. Using a pre-trained vision-language model, we achieve 87% accuracy on a chest X-ray dataset without any task-specific training data. Our approach uses CLIP embeddings and a novel prompt engineering strategy. Results suggest that foundation models can be effectively used for medical diagnosis without fine-tuning.",
        "known_flaws": [
            "No comparison to supervised baselines (fine-tuned models)",
            "Dataset not described - size, source, class balance unknown",
            "No discussion of ethical implications of medical AI without training data",
            "No error analysis - what types of cases does it fail on?",
            "Prompt engineering details not reproducible",
            "No confidence calibration or uncertainty quantification",
        ],
        "question": "Write a peer review of this paper. Identify at least 3 specific weaknesses, suggest concrete improvements, and give an overall recommendation.",
        "keywords": [
            "baseline",
            "supervised",
            "dataset",
            "reproducibility",
            "ethical",
            "error analysis",
            "calibration",
            "uncertainty",
            "limitation",
            "clinical",
            "validation",
        ],
    },
]


class PeerReview:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for sub in MOCK_SUBMISSIONS:
            raw = _call_model(
                model,
                f"Paper: {sub['title']}\nAbstract: {sub['abstract']}\n\nTask: {sub['question']}",
            )
            flaws_found = sum(1 for flaw in sub["known_flaws"] if _flaw_in_response(flaw, raw))
            kw_count = sum(1 for kw in sub["keywords"] if kw.lower() in raw.lower())
            has_recommendation = any(
                r in raw.lower() for r in ["accept", "reject", "revision", "revise"]
            )
            flaw_score = min(flaws_found / len(sub["known_flaws"]) * 1.5, 1.0)
            kw_score = min(kw_count / len(sub["keywords"]) * 1.5, 1.0)
            rec_score = 1.0 if has_recommendation else 0.3
            score = (flaw_score * 0.5 + kw_score * 0.3 + rec_score * 0.2) * 100
            total += score
            details[sub["id"]] = {
                "score": round(score, 1),
                "flaws_found": flaws_found,
                "total_flaws": len(sub["known_flaws"]),
                "has_recommendation": has_recommendation,
                "length": len(raw),
            }
        avg = total / len(MOCK_SUBMISSIONS)
        return avg, {"per_paper": details, "average": round(avg, 1)}


def _flaw_in_response(flaw: str, response: str) -> bool:
    key_parts = flaw.lower().split()
    return sum(1 for p in key_parts if p in response.lower()) >= 2


def _call_model(model: str, prompt: str) -> str:
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "This paper makes a modest contribution. The 0.2% improvement over SOTA is not statistically significant. The evaluation is limited to 3 sentiment datasets, raising questions about generalization. Major revision recommended: add significance testing, more diverse datasets, and ablation studies."
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "The paper lacks comparison to supervised baselines. Dataset details are insufficient for reproducibility. Ethical considerations of medical AI without training data are not discussed. Major revision required."
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock peer review for evaluation."
