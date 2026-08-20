"""Literature synthesis task: evaluate ability to synthesize multiple papers."""
from typing import Any

SYNTHESIS_SETS = [
    {
        "id": "chain-of-thought",
        "papers": [
            "Wei et al. (2022): Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. Shows that adding step-by-step reasoning traces improves performance on arithmetic, commonsense, and symbolic reasoning tasks.",
            "Wang et al. (2022): Self-Consistency Improves Chain of Thought Reasoning in Language Models. Shows that sampling multiple reasoning paths and taking the majority answer improves accuracy over single CoT.",
            "Kojima et al. (2022): Large Language Models are Zero-Shot Reasoners. Shows that simply adding 'Let's think step by step' to the prompt elicits reasoning without few-shot examples.",
        ],
        "question": "Synthesize these three papers on chain-of-thought reasoning. Identify: (1) the key trend across papers, (2) a contradiction or tension between their findings, (3) an important open question that remains unanswered.",
        "keywords": ["trend", "step-by-step", "reasoning", "prompting", "improvement", "tension", "few-shot", "zero-shot", "diversity", "open question", "limitation", "generalization"],
    },
    {
        "id": "scaling-laws",
        "papers": [
            "Kaplan et al. (2020): Scaling Laws for Neural Language Models. Shows that model performance follows a power-law with model size, dataset size, and compute, suggesting optimal allocation strategies.",
            "Hoffmann et al. (2022): Training Compute-Optimal Large Language Models (Chinchilla). Shows that previous scaling laws underestimated the importance of data, and that for a given compute budget, models should be trained on more data than previously thought.",
            "Muennighoff et al. (2023): Scaling Data-Constrained Language Models. Shows that when data is limited, repeating data can extend scaling benefits, but with diminishing returns, and proposes optimal data repetition strategies.",
        ],
        "question": "Synthesize these three papers on scaling laws. Identify: (1) how the understanding of scaling has evolved, (2) a practical implication for training large models, (3) a limitation of the scaling law framework.",
        "keywords": ["scaling", "power-law", "compute", "data", "optimal", "evolved", "shift", "chinchilla", "data-constrained", "repetition", "diminishing", "practical", "training", "efficiency", "limitation"],
    },
]

class LiteratureSynthesis:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for sset in SYNTHESIS_SETS:
            paper_text = "\n".join(sset["papers"])
            raw = _call_model(model, f"Papers:\n{paper_text}\n\nTask: {sset['question']}")
            kw_count = sum(1 for kw in sset["keywords"] if kw.lower() in raw.lower())
            max_kw = len(sset["keywords"])
            coverage = min(kw_count / max_kw * 2, 1.0)
            length_score = min(len(raw) / 400, 1.0)
            score = (coverage * 0.6 + length_score * 0.4) * 100
            total += score
            details[sset["id"]] = {"score": round(score, 1), "keyword_coverage": kw_count, "length": len(raw)}
        avg = total / len(SYNTHESIS_SETS)
        return avg, {"per_set": details, "average": round(avg, 1)}

def _call_model(model: str, prompt: str) -> str:
    import os
    if model.startswith("gpt") or model.startswith("openai"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Mock synthesis: The key trend is that reasoning capabilities improve with structured prompting. The tension is between few-shot and zero-shot approaches. The open question is whether CoT represents genuine reasoning or pattern matching."
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024)
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Mock: Scaling understanding evolved from compute-optimal to data-optimal. Practical implication: train on more tokens. Limitation: scaling laws may break at extreme scales."
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    return "Mock synthesis for evaluation."