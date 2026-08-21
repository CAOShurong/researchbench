"""Paper comprehension task: evaluate deep understanding of research papers."""

from typing import Any

from researchbench.dataset_schema import DatasetItem, Provenance, validate_item

# --- Legacy placeholder data (NOT the authoritative dataset) -------------------
# These are the original keyword-matching scaffold items. They are retained
# for backward compatibility but are NOT used by evaluate(), data export, or
# any run path. Do not treat these as benchmark data.
LEGACY_PAPERS_PLACEHOLDER: list[dict[str, Any]] = [
    {
        "id": "attention-2017",
        "title": "Attention Is All You Need",
        "abstract": (
            "The dominant sequence transduction models are based on complex recurrent "
            "or convolutional neural networks that include an encoder and a decoder. "
            "The best performing models also connect the encoder and decoder through an "
            "attention mechanism. We propose a new simple network architecture, the "
            "Transformer, based solely on attention mechanisms, dispensing with "
            "recurrence and convolutions entirely. Experiments on two machine "
            "translation tasks show that these models are superior in quality while "
            "being more parallelizable and requiring significantly less time to train."
        ),
        "questions": [
            {
                "q": "What is the single most important architectural innovation introduced in this paper?",
                "reference_keywords": [
                    "transformer",
                    "self-attention",
                    "attention mechanism",
                    "no recurrence",
                    "no convolution",
                ],
            },
            {
                "q": "What is a key limitation of the Transformer architecture that subsequent work had to address?",
                "reference_keywords": [
                    "quadratic",
                    "O(n^2)",
                    "memory",
                    "computation",
                    "long sequences",
                    "position encoding",
                ],
            },
            {
                "q": "What experimental results support the paper's claims about the Transformer?",
                "reference_keywords": [
                    "machine translation",
                    "WMT",
                    "BLEU",
                    "parallelizable",
                    "faster training",
                    "superior quality",
                ],
            },
        ],
    },
    {
        "id": "resnet-2015",
        "title": "Deep Residual Learning for Image Recognition",
        "abstract": (
            "Deeper neural networks are more difficult to train. We present a residual "
            "learning framework to ease the training of networks that are substantially "
            "deeper than those used previously. We explicitly reformulate the layers as "
            "learning residual functions with reference to the layer inputs, instead of "
            "learning unreferenced functions. We provide comprehensive empirical evidence "
            "showing that these residual networks are easier to optimize, and can gain "
            "accuracy from considerably increased depth. On the ImageNet dataset we "
            "evaluate residual nets with a depth of up to 152 layers."
        ),
        "questions": [
            {
                "q": "What problem does the residual learning framework solve?",
                "reference_keywords": [
                    "degradation",
                    "deeper",
                    "harder to train",
                    "optimization difficulty",
                    "vanishing gradient",
                ],
            },
            {
                "q": "How does a residual block differ from a plain block?",
                "reference_keywords": [
                    "skip connection",
                    "identity mapping",
                    "shortcut",
                    "F(x) + x",
                    "residual function",
                ],
            },
            {
                "q": "What empirical evidence supports the effectiveness of residual networks?",
                "reference_keywords": [
                    "ImageNet",
                    "152 layers",
                    "deeper",
                    "lower complexity",
                    "accuracy improvement",
                    "easier to optimize",
                ],
            },
        ],
    },
]

# Backward-compat alias (do NOT use for new code)
PAPERS = LEGACY_PAPERS_PLACEHOLDER

# --- Authoritative versioned dataset (used by all execution paths) ------------

DATASET: list[DatasetItem] = [
    DatasetItem(
        id="paper_comprehension/attention-2017/q1",
        capability_tags=["C5", "C1"],
        ground_truth=(
            "The Transformer replaces recurrence and convolution with "
            "self-attention; key limitation is quadratic complexity in "
            "sequence length."
        ),
        ground_truth_source="paper",
        scoring_method="keyword_match_placeholder",
        contamination_risk="high",
        provenance=Provenance(
            source_id="arXiv:1706.03762",
            source_type="paper",
            license="arXiv-nonexclusive-license-1.1",
            author_role="benchmark_author",
            reviewer_role="",
            review_status="draft",
            review_notes=(
                "Classic paper, very likely in training data. Use for "
                "methodology critique, not factual recall. No expert "
                "review yet -- draft status only."
            ),
        ),
        expert_notes=(
            "The reference_keywords are a placeholder answer key for "
            "keyword matching. They do NOT constitute research-grade "
            "ground truth. A real rubric must be designed by a domain expert."
        ),
        version="1.0",
        task_data={
            "title": LEGACY_PAPERS_PLACEHOLDER[0]["title"],
            "abstract": LEGACY_PAPERS_PLACEHOLDER[0]["abstract"],
            "question": LEGACY_PAPERS_PLACEHOLDER[0]["questions"][0]["q"],
            "reference_keywords": LEGACY_PAPERS_PLACEHOLDER[0]["questions"][0][
                "reference_keywords"
            ],
        },
    ),
]

# Alias used by CLI _TASK_SAMPLE_PATH and other modules
PILOT_ITEMS = DATASET


class PaperComprehension:
    """Evaluates paper comprehension using the authoritative DATASET collection."""

    def evaluate(self, model: str = "gpt-4o", **kwargs) -> tuple[float, dict[str, Any]]:
        total_score = 0.0
        max_score = 0.0
        details: dict[str, Any] = {}

        for item in DATASET:
            # Validate before any model call
            errs = validate_item(item)
            if errs:
                raise ValueError(f"DatasetItem {item.id} failed validation: {'; '.join(errs)}")

            td = item.task_data
            mn = td.get("reference_keywords", [])
            raw = _call_model(
                model,
                f"Paper: {td.get('title', '')}\n{td.get('abstract', '')[:300]}\n\nQuestion: {td.get('question', '')}",
            )
            match_count = sum(1 for kw in mn if kw.lower() in raw.lower())
            correctness = min(match_count / max(len(mn), 1) * 1.5, 1.0)
            total_score += correctness
            max_score += 1.0
            details[item.id] = {
                "score": correctness,
                "max": 1,
                "review_status": item.provenance.review_status if item.provenance else "unknown",
            }

        score = (total_score / max_score * 100) if max_score > 0 else 0.0
        return score, {"per_item": details, "total_items": len(DATASET)}


def _call_model(model: str, prompt: str) -> str:
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return (
                "Mock response: The Transformer architecture uses self-attention "
                "mechanisms. A limitation is quadratic complexity. Results show "
                "superior BLEU scores on WMT translation tasks."
            )
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=512
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return (
                "Mock: The key innovation is residual learning via skip connections "
                "solving the degradation problem in deep networks."
            )
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=512, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock response for evaluation."
