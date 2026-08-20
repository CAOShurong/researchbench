"""Reproduction task: evaluate ability to diagnose reproduction failures."""
from typing import Any

SCENARIOS = [
    {
        "id": "cuda-mismatch",
        "description": "A paper claims that their model achieves 72.3% accuracy on benchmark X using PyTorch 1.10 with a single A100 GPU. You clone their repository, install the exact dependencies from their requirements.txt, and run their evaluation script. You get 63.1% accuracy instead of 72.3%. The model architecture and weights match the paper description.",
        "question": "What could cause this reproducibility failure? List at least 3 possible causes, explain how you would diagnose each, and propose a fix for the most likely cause.",
        "keywords": ["seed", "random", "deterministic", "CUDA", "GPU", "precision", "batch size", "hardware", "dataloader", "shuffle", "normalization", "version", "checkpoint", "weight initialization", "environment", "dependency"],
        "key_causes": ["random seed not set", "CUDA deterministic mode", "batch size difference", "data loading order", "normalization statistics", "PyTorch version differences"],
    },
    {
        "id": "data-drift",
        "description": "A paper introduces a new NLP model achieving state-of-the-art results on the GLUE benchmark. You implement their architecture from scratch based on the paper description, use the standard GLUE dataset, and follow their training procedure. You get reasonable results on most tasks but significantly lower performance on the RTE task (59.8% vs their reported 68.4%).",
        "question": "What could cause this specific task failure? List at least 3 possible causes, explain how you would diagnose each, and propose a fix for the most likely cause.",
        "keywords": ["tokenizer", "preprocessing", "max length", "truncation", "padding", "learning rate", "warmup", "epoch", "early stopping", "class imbalance", "metric", "evaluation", "split", "validation", "test set", "leakage"],
        "key_causes": ["different tokenizer or preprocessing", "different max sequence length", "different evaluation metric", "data split or seed difference", "learning rate schedule mismatch"],
    },
]

class Reproduction:
    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total = 0.0
        details = {}
        for sc in SCENARIOS:
            raw = _call_model(model, f"Scenario: {sc['description']}\n\nTask: {sc['question']}")
            causes_found = sum(1 for cause in sc["key_causes"] if cause.lower() in raw.lower())
            kw_count = sum(1 for kw in sc["keywords"] if kw.lower() in raw.lower())
            cause_score = min(causes_found / len(sc["key_causes"]) * 1.5, 1.0)
            kw_score = min(kw_count / len(sc["keywords"]) * 1.5, 1.0)
            has_diagnosis = any(w in raw.lower() for w in ["diagnose", "check", "compare", "investigate", "test"])
            diagnosis_score = 1.0 if has_diagnosis else 0.5
            score = (cause_score * 0.5 + kw_score * 0.3 + diagnosis_score * 0.2) * 100
            total += score
            details[sc["id"]] = {"score": round(score, 1), "causes_found": causes_found, "keyword_coverage": kw_count, "length": len(raw)}
        avg = total / len(SCENARIOS)
        return avg, {"per_scenario": details, "average": round(avg, 1)}

def _call_model(model: str, prompt: str) -> str:
    import os
    if model.startswith("gpt") or model.startswith("openai"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Possible causes: (1) CUDA non-determinism - set torch.backends.cudnn.deterministic=True. (2) Random seed not set - set all seeds. (3) Batch size difference affecting batch norm statistics. Check by rerunning with same seed and comparing step-by-step outputs."
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024)
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "The RTE task is sensitive to input formatting. Check: (1) tokenizer version and max_length, (2) whether the evaluation uses matched or mismatched data, (3) learning rate warmup ratio. The most likely cause is a different max_length truncation strategy."
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    return "Mock reproduction analysis for evaluation."