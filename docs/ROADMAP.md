# Roadmap

This is a living, non-binding plan for the ResearchBench project. Items are
*proposals*, not commitments; nothing here has been validated, scored, or
shipped yet, and none of it counts as a claim of performance or adoption.

## Short term (next)

- **Score normalization audit.** Validate that scores behave well across
  response lengths and keyword-set sizes, and publish a table of the effective
  range each task actually produces. Add tests for any anomalies found.
- **Expert-validated task data.** Extend the built-in dataset only with items
  reviewed by domain experts, with provenance recorded per item. No
  count-padding: new items must add discriminative power, not bulk.
- **LLM-as-judge mode for open-ended tasks.** A documented, replicable
  judge-config (rubric JSON + provider settings) for the open-ended tasks, with
  a reproducibility note and a human-validation subset. Must not change the
  deterministic keyword scoring used today.
- **Report schema documentation.** A formal schema document for the `json` and
  `html` report outputs so downstream tooling can depend on it.

## Medium term

- **Cross-lingual / domain variants.** Domain-oriented task packs (biomedical,
  physics, social science) and non-English evaluation to broaden coverage.
- **Dataset registry + CLI data loading.** Load task datasets from JSON/YAML so
  the benchmark is not locked to the bundled fixtures.
- **Leaderboard / comparison artifact format.** A stable, signed output format
  for publishing multi-model comparisons (CI artifact / static page).

## Principles

- Any new dataset item must respect source licenses and record provenance.
- Deterministic scoring remains the default; probabilistic methods are
  opt-in and clearly labeled.
- All added tasks keep the `evaluate(model) -> (score, details)` interface and
  the `[0, 100]` score convention.
- No result in this repo is presented as real model performance unless it was
  actually produced by a live evaluation with a named provider and model id.