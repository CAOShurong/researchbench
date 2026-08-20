"""Evaluate a model with the ResearchBench Python API.

Real-model run (OpenAI):
    $env:OPENAI_API_KEY = "sk-..."
    python examples/evaluate_model.py --model gpt-4o

Mock run (no key -> canned answers, smoke-test only):
    python examples/evaluate_model.py --model gpt-4o

The script refuses to label mock output as a real evaluation: if no API key is
present it prints a clear warning. Never report mock scores as model results.
"""

import os
import sys

from researchbench import Benchmark


def main() -> int:
    model = "gpt-4o"
    if len(sys.argv) > 2 and sys.argv[1] == "--model":
        model = sys.argv[2]

    is_mock = not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY")
    if is_mock:
        print("*" * 72)
        print("WARNING: no OPENAI_API_KEY / ANTHROPIC_API_KEY detected.")
        print("Running in MOCK mode. Scores below are canned answers and are")
        print("NOT a real evaluation of model '%s'." % model)
        print("*" * 72)
        print()

    bench = Benchmark()
    result = bench.run(model=model)

    print()
    print(result.to_text(verbose=True))
    print()
    print("JSON report:")
    print(result.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
