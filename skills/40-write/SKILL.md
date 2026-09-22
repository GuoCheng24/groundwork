---
name: groundwork-write
description: >
  Write the paper from claims that have already survived checking, with figures
  and tables regenerated from data rather than transcribed. Triggers: "write the
  paper", "draft", "figures", "tables", "写论文", "画图", "做表".
---

# Write — from claims, not from results

## Start from the claim list, not from the results directory

By the time writing starts, `30-claim` has produced a list of claims that
survived their own checks. Draft from that list. A section written by walking
the results directory ends up describing what was run rather than arguing for
something, and the difference is visible to a reviewer in one paragraph.

For each claim: the sentence, the evidence file, the check that re-derives it.
If a claim has no check, it is not ready to be in the paper.

## Tables are generated, never transcribed

Build every table from the committed result file with a script, and have CI
rebuild it and diff. A table typed once is a table that will be wrong after the
next run, and nobody re-reads a table they have already checked.

The same goes for prose figures. `doubleblind trace` holds a document to its
data; point it at the manuscript, not only at the README, and use `--derive`
for quantities a script recomputes rather than an allow list — a number in an
allow list has stopped being checked.

## Figures carry structure, and get audited

- Draw the comparison the claim makes, not everything measured.
- Fit lines over a **common range**. Per-family points joined by segments once
  made a shallower relationship look steeper and reversed a figure's visual
  conclusion while every number in it was correct.
- Audit the rendered result with `doubleblind render` at the size it will be
  seen. Then look at it yourself: no rule about geometry knows which slope a
  reader will perceive.

## Stale artifacts

A built PDF is not the source. Re-extract the numbers from the built artifact
and match them against the current results, anchored so a figure cannot match
inside a longer one. A manuscript that quotes a figure its own data has since
replaced passes every check that only reads the source.

## The lead sentence

Constructive: *we propose X, it solves Y, the number is Z.* The audit, the
ablation and the negative result are supporting material and belong after it.
This is a rule about ordering, not about hiding: a limitation that a reader
would notice must be in the paper, stated by you first.

## In this stage

- [`build.md`](build.md) — one authoritative source, and a preview you must not trust
- [`figures.md`](figures.md) — the primitives are not the bottleneck; collision is
- [`captions.md`](captions.md) — the audit nobody runs, and the eight things one pass found
- [`claims.md`](claims.md) — the unit the paper is actually made of
- [`structure.md`](structure.md) — write the paper the venue actually prints
- [`diagrams.md`](diagrams.md) — the overview figure is buildable; layout is the hard part
- [`theory.md`](theory.md) — attacking a stated open problem across days
- [`revision.md`](revision.md) — auditing a manuscript, including somebody else's
