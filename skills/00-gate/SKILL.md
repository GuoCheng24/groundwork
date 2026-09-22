---
name: groundwork-gate
description: >
  Decide whether a research direction is allowed to cost a week. Run this BEFORE
  the first real experiment, before the literature deep-dive, before any code
  that is not a measurement. Triggers: "should we do this", "new direction",
  "is this worth it", "立项", "该不该做", "开工前". This is not a review of work
  already done; it is the thing that stops the work.
---

# Gate — the four numbers that decide

An autonomous pipeline is cheap at everything downstream: survey, ideate,
implement, write. The expensive failures are all upstream, and they repeat. Ten
of them are recorded with their cost in `archive/causes-of-death.json`; every
one was detectable before the first real experiment.

**Nothing below asks what the proposed method is.** A gate that knows what you
are hoping for is not a gate.

## The four measurements

Run these on the same split, in the same pipeline, before anything else.

| # | measurement | what it rules out |
|---|---|---|
| 1 | **strongest trivial baseline**, tuned as hard as the proposal would be | the signal was never structural |
| 2 | **oracle** — a method handed perfect access to the quantity the proposal estimates | there was no headroom to win |
| 3 | **random arm** — shuffled labels, or random assignment | the task does not need a learned policy |
| 4 | **positive control** — a case where the effect is known and must be recovered | a null would measure your pipeline |

Then:

```bash
groundwork gate --baseline 0.812 --oracle 0.838 --se 0.019 \
    --random 0.500 --positive-control 0.80 --positive-control-floor 0.70
```

It refuses when the headroom is under 2 standard errors, when a perfect method
would still be reported as null on this split, when the random arm reaches the
baseline, or when the positive control does not recover. It prints what a method
would have to capture to be detectable at all — decide whether that is worth
doing **before** the work, not after.

## Two gates a number cannot answer

**Occupancy.** Search the *mechanism*, not your framing of it, and not only the
last five years — a qualitative result was occupied by a 2017 paper and its
closed form by a 2003 one. Abstract-level search hits roughly 4% of what is
already there, so fetch full text for the candidates that matter. Search your
own prior output first: a subgroup analysis proposed as a new paper turned out
to be a table in the group's own supplement.

**Reduction.** Write the proposed quantity in the simplest equivalent form you
can, and try to reduce it to something known. A failure mode that looked new was
exactly a known balance condition under a change of variables; a
statistical-computational gap collapsed back onto sparse PCA. If you cannot
reduce it, that is the first evidence you have that it is new.

## The rule that makes the gate worth having

**A NO-GO is written down.** `archive/` is not a graveyard, it is the part of
this repository that cannot be regenerated: a direction that dies silently gets
re-proposed in four months by somebody with the same good taste that proposed it
the first time — often you. Record the verdict, the cause from
`causes-of-death.json`, and the cheap test that settled it.

## What this gate does NOT say

It does not say the idea is novel, that the method will work, or that the result
will be worth a paper. It says only that the ceiling, the baseline and the
controls have not already answered the question. Everything it passes still has
to survive `30-claim`.

## In this stage

- [`two-toolboxes.md`](two-toolboxes.md) — where originality actually comes from, and what to do when you only have one toolbox
- [`ceiling-first.md`](ceiling-first.md) — the measurement that was worth more than the project it came from
- [`breakthrough.md`](breakthrough.md) — why the serial deep-dive never produces the breakthrough
- [`positive-control.md`](positive-control.md) — run it before the experiment, not after the null
- [`metric-validity.md`](metric-validity.md) — can the metric carry the sentence you intend to write
