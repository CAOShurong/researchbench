# Launch notes (agent-owned)

Research, 2026-09-11: high GitHub star velocity comes from **distribution + a
README that sells in 15 seconds**, not from more tests. Repeated independent
write-ups (AFFiNE, 0→10k pattern analyses) converge on:

1. First screen: one sentence, a picture of it working, one install command.
2. Ignition: Show HN (Tue–Thu, ~8–10am ET) plus 1–2 specialist subreddits the
   same day. Front page can mean hundreds of stars; a dump of “please star”
   dies.
3. Honest technical story beats “we built the best benchmark.”
4. Star-buying and fake velocity backfire.

This repository’s searchable claim is narrow on purpose:

> Score whether a chat model can reason about BEOL / heterogeneous integration,
> in the terminal, with no API key. Fluent wrong physics should fail.

It will not out-star DeepEval (18k, pytest-for-LLM-apps). It can convert
people who already care about semiconductor process / 3D integration / “does
this model actually know devices.”

## Assets that must stay true

- README first screen + `docs/assets/demo.svg` (numbers from mock run).
- `pip install "git+https://github.com/CAOShurong/researchbench.git@v0.4.1"`
- Binder badge.
- GitHub About + topics (`beol`, `heterogeneous-integration`).

## Show HN text (ready; do not overclaim)

Title:

```text
Show HN: Terminal quiz for whether an LLM knows BEOL device physics
```

Body:

```text
I needed to know if a chat model could actually reason about back-end-of-line
constraints (400 °C thermal budget, IGZO, HZO, Cu–Cu hybrid bonding) instead of
sounding fluent and being wrong.

researchbench runs that quiz in the terminal. No API key required for a mock
pass; with a key it scores real answers against a coded rubric with hard
negatives.

  pip install "git+https://github.com/CAOShurong/researchbench.git@v0.4.1"
  researchbench run --tasks heterogeneous_pilot --model gpt-4o

Mock mode on the canned paragraph scores 13.78/100 — it knows “400 C” and
misses the rest. That is the point.

This is a prototype, not a leaderboard, and it is unrelated to Liu et al.
ResearchBench (ACL 2026 Findings).

Repo: https://github.com/CAOShurong/researchbench
```

## Channels that fit (do not spam)

- Hacker News Show HN (weekday US morning).
- r/Semiconductors, r/ECE, r/MachineLearning (technical post, not “star please”).
- Device/process people on X, linking the GIF/SVG and the one command.

The user does not post. Keep this file current so a later session can paste
it without rewriting the claim.
