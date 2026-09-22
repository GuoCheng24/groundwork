---
name: proofground-direction
description: >
  Turn a research direction into candidate projects that can survive the gate:
  survey what exists, generate candidates, and kill the ones that are already
  occupied or that reduce to something known. Triggers: "research direction",
  "what should we work on", "survey", "find a gap", "选题", "调研", "查新".
---

# Direction — candidates, not ideas

An idea is a sentence. A candidate is a sentence plus the four numbers that would
let `00-gate` refuse it. Produce candidates.

## 1. Survey for the gap, not for the field

Read for three things and write them down separately:

- **what is claimed** — the headline result of each relevant paper;
- **what is conceded** — the limitations section. This is where the gaps that
  are real and known live, and it is the part most surveys skip;
- **what is assumed** — the setup every paper in the area shares without arguing
  for it. A shared assumption nobody defends is the most valuable thing a survey
  can find, and the hardest.

Search the mechanism rather than the application, and go back further than five
years. Abstract-level matching finds roughly 4% of what is already there; fetch
full text for anything that could be the same idea in other words.

## 2. Generate against the gate, not against taste

For each candidate write, before any enthusiasm:

```
claim        the single sentence the result would support
baseline     the strongest trivial method that would be its competitor
oracle       what "perfect access" would mean here, and how to measure it
null         the result that would end this project, and what it would mean
venue        who publishes the claim sentence above, as written
```

A candidate that cannot fill all five is not ready to be argued about.

## 3. Kill early and on purpose

Three cheap kills, in the order that costs least:

1. **Self-occupancy.** Search your own prior output. A subgroup analysis
   proposed as a new paper was already a table in the group's own supplement.
2. **Reduction.** Write the quantity in its simplest equivalent form and try to
   reduce it to something known. Failing to reduce it is the first real evidence
   of novelty; succeeding saves the week.
3. **Occupancy.** The mechanism, in older literature, in other vocabularies.

Then run `proofground gate`. Then, and only then, write code that is not a
measurement.

## 4. Decide the venue from the claim, not the ambition

A working method whose strongest supportable sentence is modest has a modest
venue, and deciding that up front is cheaper than a rejection cycle. Re-decide
whenever the claim changes — and the claim changes.

## What to record

Every candidate that dies goes into `archive/` with its cause. Candidates die in
batches: one programme killed 32 of 32 at this stage, another 16 of 16. That is
the gate working, not the gate being too strict — but only if the verdicts are
written down, or the same good taste proposes them again next quarter.

## In this stage

- [`occupancy.md`](occupancy.md) — is it already done, and can you tell - including the three traps of existence verification
- [`venue-fit.md`](venue-fit.md) — capacity is a separate gate from novelty; contribution type predicts acceptance better than topic
