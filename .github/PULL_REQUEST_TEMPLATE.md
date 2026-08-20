---
name: Pull request
about: Submit a change to ResearchBench
---

## Summary

Short description of what this PR does and why.

## Checklist

- [ ] Change is single-purpose and scoped (see `docs/CONTRIBUTING.md`)
- [ ] `ruff check src tests` passes
- [ ] `ruff format --check src tests` passes
- [ ] `mypy src` passes (typecheck CI job)
- [ ] `pytest tests -v` passes and coverage stays above the CI gate (80%)
- [ ] New behavior is covered by tests
- [ ] User-facing changes are documented (README / docs/, or CHANGELOG)
- [ ] No fabricated data or scores; any example/mock output is labeled as mock

## Related issues

Closes #...

## Notes for reviewers

Anything unusual, trade-offs, or follow-up work.