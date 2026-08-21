# RESULT.md — ResearchBench Round 3

## Executed facts (verified by running)

| Check | Result | Evidence |
|---|---|---|
| Phase 2b (Issue #5, PR #8) | MERGED `cc61bc0` | 8/8 CI pass |
| Phase 3 (Issue #7, PR #9) | MERGED `49bea45` | 8/8 CI pass |
| Python 3.9 full suite | 260 passed | CI Ubuntu + Windows |
| Python 3.13 full suite | 260 passed | CI Ubuntu + Windows |
| ruff check + format | clean | exit 0 |
| mypy | 14 files, no issues | exit 0 |
| Wheel build | success | sdist + wheel |
| Clean-venv CLI | valid item runs (rc=0, timestamp, total_items=1) | installed from wheel |
| Draft rejection | rc=1, clear error | installed from wheel |
| Unknown data task | rc≠0 | installed from wheel |
| Data JSON provenance | source_id=arXiv:1706.03762 | installed from wheel |
| RunRecord CLI | import/validate/export all pass | installed from wheel |
| Spy/counter | 0 model calls on invalid/draft | unit tests |

## What was fixed in this round

### Phase 2b: Authoritative dataset (AUDIT defects 1-5)
- `DATASET` (list[DatasetItem]) is the sole source for paper_comprehension; `LEGACY_PAPERS_PLACEHOLDER` retained but clearly named
- `Benchmark.run()` validates all items before any model call (sequential + parallel)
- Draft items rejected without `--allow-draft`; `verify` uses `allow_draft=True` (smoke test)
- Provenance required: source_id, source_type, license (not "unknown"), author_role, review_status
- `data unknown_task` exits non-zero
- sample/data text/data JSON/runner all read the SAME collection

### Phase 3: RunRecord CLI (AUDIT defect 4)
- `subscription.py`: from_dict/from_json, validate_run_record() with mandatory field checks
- `cli.py`: `run-record import/validate/export` command
- No hardcoded model names
- Subscription/API remain separate conditions

### Phase 4: Doc sync
- pyproject description: "prototype" not "comprehensive benchmark"
- Schema $id: `blob/master/` not `blob/main/`
- RESEARCH_BENCHMARK.md: updated test count (260), status of reproducibility/subscription
- docs/API.md: added RunRecord contract section

## Unverified items

- No real model evaluation has been run (only mock mode)
- No expert-validated items, gold rubrics, or human agreement measurements
- No contamination-resistant pilots or leaderboard
- LLM-as-judge not validated against human ratings
- The keyword scorer is a placeholder, not scientifically valid

## Scientific validity limitations

- All 7 scorers use keyword/substring matching
- Paper_comprehension pilot item is draft (no expert review)
- The 260 tests prove software mechanics, not scientific measurement
- Name collision with 2025 ResearchBench unresolved
- v0.1.0 tag is stale; no new release until scientific pilot

## Next steps

1. Research existing benchmarks (complete §8 comparison table)
2. Design expert rubrics for paper_comprehension + peer_review pilot
3. Pilot a contamination-resistant item using a recent/hidden paper
4. Validate LLM-as-judge against human ratings
5. Replace keyword-matching scorers with evidence-based evaluation
6. Resolve naming conflict before stable release