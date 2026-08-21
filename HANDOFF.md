---
schema_version: portable-project-memory/v1
handoff_revision: 5
updated_at: "2026-08-21T11:40:00+08:00"
updated_by: "agent-session"
base_revision: git:7b9daf7c97966f69835709bad59d2633db5e9fb3
workspace_fingerprint: sha256:b7fc4235a032ebd0ae291f92e5ec71dd894be444dfc8e22ec96195ae064144b8
context_fingerprint: sha256:27846abba75b153341b21dd871fb41c7cacaed64276f4075dde21112faf9bf22
status: active
---

# Project Handoff

## Current objective

**RESEARCH_BENCHMARK.md has been written and is the authoritative design
document.** The current v0.1.0 implementation uses keyword-matching scoring
which is a **placeholder**, not scientifically valid. The next agent must read
`RESEARCH_BENCHMARK.md` before any benchmark work and follow its next-steps
section (Section 11).

The benchmark's central question is: *"Which AI system is genuinely the better
research assistant, in what research abilities, under what conditions, and how
do we know?"*

## Confirmed state

### Completed

- **7 task modules** with deterministic keyword scoring (paper_comprehension,
  idea_generation, literature_synthesis, experimental_design, peer_review,
  reproduction, open_question_id). Each has `evaluate(model) -> (score, details)`.
- **CLI** (10 commands): `list`, `show`, `run`, `compare`, `tasks`, `sample`,
  `data`, `report`, `schema`, `verify`. Options: `--format text|json|html`,
  `--save`, `--verbose`, `--dry-run`, `--ignore`, `--benchmark`, `--quiet`,
  `--parallel`, `--save-responses`. Glob patterns in `--tasks`.
- **Core**: `Benchmark`, `BenchmarkResult`, `TaskResult`. `to_text()`/`to_json()`/
  `to_html()`/`to_format()`. `compare(models)`.
- **Tests**: 162 tests covering per-task scoring logic, CLI commands, report
  rendering, mock mode, error paths. Coverage: 88% (the ~12% gap is live-SDK
  branches that require API keys).
- **CI**: 3 jobs (test matrix Ubuntu/Windows x 3.9/3.11/3.13 with 80% coverage
  gate + ruff, mypy on 3.11, wheel build + clean-venv smoke test).
- **Docs**: TASK_DEFINITIONS.md, USAGE.md, CONTRIBUTING.md, RESEARCH.md,
  API.md, ROADMAP.md, FAQ.md, report-schema.json.
- **Examples**: evaluate_model.py, run_cli_demo.sh, run_cli_demo.ps1, README.md.
- **Packaging**: SPDX license, py.typed, minimal deps (click only), verified
  wheel build + install.
- **Repo hygiene**: .gitattributes, CHANGELOG, CODE_OF_CONDUCT, SECURITY,
  dependabot, pre-commit, issue/PR templates, .gitignore.

### In progress

- Project memory files (this handoff) are being initialized for the first time.

### Blocked

- Nothing blocked. The repo is in a known-good state.

## Changed artifacts

| Path | Change | State |
|---|---|---|
| `src/researchbench/` | All modules completed | Clean, committed |
| `tests/` | 162 tests | Clean, committed |
| `docs/` | 8+ documentation files | Clean, committed |
| `examples/` | 4 demo files | Clean, committed |
| `.github/workflows/ci.yml` | 3-job CI | Clean, committed |
| `pyproject.toml` | Full metadata, SPDX, minimal deps | Clean, committed |
| `.ai/` + memory files | First-time initialization | Just created, needs review |

## Verification evidence

| Check | Result | Executed at / artifact version | Basis / exit code | Evidence or command |
|---|---|---|---|---|---|
| `pytest tests` | PASS | 2026-08-21 | exit 0, 165 tests | `--cov --cov-fail-under=80` |
| `ruff check src tests` | PASS | 2026-08-21 | exit 0 | `ruff check` |
| `ruff format --check src tests` | PASS | 2026-08-21 | exit 0 | `ruff format --check` |
| `mypy src` | PASS | 2026-08-21 | exit 0 | `mypy src` |
| GitHub CI (all 6 matrix jobs) | PASS | 2026-08-21 | run 32447648205 success | `gh run list` |
| Profile PR #90 (fix false claim) | MERGED | 2026-08-21 | CI SUCCESS | `gh pr view 90` |
| Run-record metadata implemented | PASS | 2026-08-21 | 3 new tests pass | `test_run_record_metadata`, `test_raw_output_captured` |

## Decisions referenced

- `docs/ROADMAP.md` lists proposed future directions (non-binding).
- The CAOShurong GitHub Sources program has a `D-20260820-030000-c018` decision
  authorizing the build of this benchmark. See
  `E:\Codex\Projects\caoshurong\github-sources-program\DECISIONS.md`.

## Risks and unknowns

- **CRITICAL: All 7 tasks use keyword substring matching as their sole scoring
  method.** This is a placeholder, not a scientifically valid evaluation.
- **CRITICAL: Naming conflict.** A 2025 "ResearchBench" paper and code repo
  already exists (scientific discovery, idea retrieval, hypothesis generation).
  Other competitors: ResearcherBench, DeepResearch Bench, RPC-Bench (ACL 2026).
  The public README and RESEARCH.md previously claimed "no existing benchmark
  covers this gap" — this was **false** and has been corrected. A rename may be
  needed (user decision).
- **CRITICAL: Public claims vs. reality.** The project is a prototype, not a
  validated benchmark. It has no expert-validated datasets, gold answers, model
  results, or leaderboard. The README now reflects this honestly.
- **CI was red on Python 3.9** due to `test_run_benchmark` checking `result.stderr`
  which is empty on click 8.1.x (py3.9 default `mix_stderr=True`). **Fixed.**
- **3 unpushed commits** exist locally (not pushed; user will push).
- **No reproducibility metadata.** Run records contain only the model name.
- **No subscription-model protocol.** Only API calls are supported.
- **No contamination prevention.** All papers are well-known classics.
- The `examples/demo.ipynb` was added by an external agent; not reviewed.

## Next actions

1. **Read `RESEARCH_BENCHMARK.md` in full** — it is the authoritative design
   document. All benchmark work must reconcile with it.
2. Research existing benchmarks (Section 8 of RESEARCH_BENCHMARK.md): complete
   the comparison table with real findings for PaperQA2, SciCode, MLAgentBench,
   and others.
3. Design the dataset schema (Section 4.2): per-item metadata, ground truth,
   contamination risk, hard negatives.
4. Design the run-record format (Section 7.1): implement run-record capture in
   `BenchmarkResult` and `TaskResult` (currently `raw_output` is never
   populated — this must be fixed).
5. Design expert rubrics for at least 2 pilot tasks (paper comprehension + peer
   review).
6. Implement subscription-mode protocol (Section 6.1).
7. Pilot a contamination-resistant item using a recent/hidden paper.
8. Validate LLM-as-judge against human ratings on pilot items.
9. Only then replace keyword-matching scorers with evidence-based evaluation,
   task by task.
10. Do NOT push to GitHub unless the user explicitly requests it.

## User decisions required

- Whether to continue with ROADMAP features (LLM-as-judge, expert data) or
  publish and promote the current version first.
- Whether to push committed changes to GitHub.