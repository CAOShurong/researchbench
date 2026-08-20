---
name: Bug report
about: Report a reproducible defect in ResearchBench
title: "[bug] "
labels: bug
---

**Describe the bug**
A clear and concise description of what is wrong.

**Environment**
- Python version:
- Platform (OS):
- researchbench version (`researchbench --version` or `pip show researchbench`):
- Installed with: (PyPI / editable / wheel path)

**Reproduction**
Minimal commands or code to reproduce. If the issue depends on model calls,
say whether you ran in mock mode or with a real API key.

```bash
researchbench run --tasks ... --model ...
```

**Expected vs actual**
What you expected to happen vs what happened.

**Relevant report output**
Paste the `--format json` or `--verbose` output here.

**Additional context**
Anything else relevant.

> Do **not** paste API keys or private data.