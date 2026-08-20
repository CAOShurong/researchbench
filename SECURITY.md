# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Best-effort fixes  |

ResearchBench is an early-stage (alpha) project. While it has no network-facing
code of its own and runs entirely locally from user-provided model responses,
we aim to fix reported security issues in the latest release on a best-effort
basis.

## Reporting a vulnerability

Please **do not** open a public issue for a vulnerability.

- Use GitHub's private vulnerability reporting at the repository's
  *Security > Report a vulnerability* page, or
- email the maintainer (address in `pyproject.toml` / `authors`) with the
  subject `[security] <short description>`.

Include, where possible:

- A short description of the issue and its impact
- The affected version(s)
- Steps to reproduce or a minimal proof of concept
- Suggested fix, if you have one

We aim to acknowledge reports within 5 business days and will keep you informed
as the issue is triaged and fixed. Please allow a reasonable disclosure window
before publishing details.

## Scope

This policy covers the `researchbench` package itself. Third-party data sets and
model providers follow their own security terms and are out of scope here. LLM
output is untrusted by design; sanitize it if you surface it in your own
interfaces (the `--format html` report uses HTML escaping for this reason).