# Public name candidates

The name **ResearchBench** is already used by Liu et al. (ACL 2026 Findings,
arXiv:2503.21248). This file proposes replacements. **Choosing and renaming
is a user decision.** Do not retitle the package, GitHub repo, or PyPI
name without that decision.

Checked against the colliding paper, ResearcherBench, DeepResearch Bench,
RPC-Bench, SciCode, and MLAgentBench. These three are unused as of
2026-09-10 in that set.

| Rank | Candidate | Why | Risk |
|---|---|---|---|
| 1 | **DeviceReason** | Matches the actual scientific pilot (BEOL / heterogeneous integration / device physics). Searchable. Unlikely to be read as the Liu suite. | Narrow if the project later covers all of academic research. |
| 2 | **AssistTrace** | Emphasises evidence tracing for a research assistant, which is the design document’s identity. | Generic; could collide later. |
| 3 | **EEWorkEval** | Honest about Electronic Engineering + work-product evaluation. Distinct from “Deep Research” report benches. | Ugly; academic reviewers may prefer a single coined word. |

Rejected here: `SciAssistBench` (too close to “research bench”), `BEOLBench`
(too small a label for the whole framework), `ResearchTrace` (still collides
on the first word).

Until a name is chosen, keep calling the *code* `researchbench` internally
and keep the public README explicit about the collision.
