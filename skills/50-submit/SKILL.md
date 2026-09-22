---
name: groundwork-submit
description: >
  Everything after the draft: venue compliance, rebuttal, resubmission to a new
  venue, and the talk. Triggers: "submit", "rebuttal", "reviewer", "resubmit",
  "slides", "投稿", "答复审稿人", "改投", "做报告".
---

# Submit — and everything after

## Venue compliance is a hard spec, so check it mechanically

Page limits, reference style, anonymisation, figure resolution, the declaration
checkboxes. Write a `check_venue_compliance.py` that fails on each, and run it
before every build. These are the cheapest possible rejections and they happen
to careful people at 2 a.m.

Two traps that have cost real submissions:

- **A reference manager's fields are live.** Updating them once, late, silently
  renumbered every citation. Convert to static text before the final build.
- **The style file is a silent variable.** The same document built with two
  versions of the same converter produced different citation formatting and a
  different page count.

## Rebuttal

Answer the review that was written, not the one you wish had been. For each
point, in this order:

1. the reviewer's sentence, quoted;
2. whether they are right — say so plainly when they are;
3. what changed, with the number;
4. what did not change, and why.

A rebuttal that concedes nothing reads as a rebuttal that read nothing. A
reviewer who is wrong about a fact is corrected with the fact and one sentence,
not with three paragraphs.

**Do not run new experiments to answer a point that reframing answers.** And do
not promise an experiment you have not run.

## Resubmission

A rejected paper ported to a new venue is not a copy with a new template. The
claim that failed once will fail again: decide which claim this version makes,
re-run `00-gate`'s venue-fit question against it, and rewrite the introduction
around the answer. Carry the previous reviews with you as a checklist of what a
reader stumbles on.

## Talk

The talk is not the paper compressed. One claim, the evidence for it, the thing
you would want to be asked. Every figure redrawn for the room it will be shown
in — `doubleblind render --scale 0.3` is the unfurl case; a projected slide at
the back of a lecture theatre is harsher than that, not gentler.

## In this stage

- [`patent.md`](patent.md) — the ordering constraints that cannot be undone
- [`delivery.md`](delivery.md) — handing a manuscript to a human who will open it in Word
- [`compliance.md`](compliance.md) — the venue's hard specs, as a file that fails
- [`rebuttal.md`](rebuttal.md) — answer the review that was written
- [`resubmit.md`](resubmit.md) — a rejected paper is not a template change
- [`talks.md`](talks.md) — talks, slides and posters, and why you must render them
- [`portals.md`](portals.md) — the submission-form fields that are writing tasks, and the one that picks your reviewers
- [`grants.md`](grants.md) — proposals: reviewers fund feasibility, not ideas
