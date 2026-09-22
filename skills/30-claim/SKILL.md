---
name: proofground-claim
description: >
  Turn results into claims that survive somebody checking. Three layers that are
  blind to different defects: re-derive every number, hand the artifact to a
  reader who was told nothing, and audit the figure a reader will actually see.
  Triggers: "write up the results", "check the claims", "before submitting",
  "核对数字", "审稿前", "出图".
---

# Claim — three layers, blind to different things

The agent that produced a result is the wrong thing to ask whether it is right:
the reasoning that produced the claim is the reasoning being asked to check it.
Three layers catch this, and **no two of them catch the same defects**.

| layer | finds | cannot see |
|---|---|---|
| re-derivation | a number that exists in no file; a bound stated tighter than the interval; a quantity written in words | a **correct number inside a sentence that does not follow from it** |
| a reader with no context | claims that do not follow; a comparison pointing the wrong way; a framing the data will not carry | a fabricated number that looks plausible |
| the rendered figure | labels that read as one word; a caption unreadable at the size it will be seen; a character the font could not draw | whether the shape a reader takes from the figure is the shape the data supports |

All three are implemented in [`doubleblind`](https://github.com/GuoCheng24/doubleblind),
which is standard library only apart from the figure layer:

```bash
pip install doubleblind
doubleblind trace README.md --data results/ --derive 'python scripts/metrics.py'
doubleblind review README.md --data results/ --agent codex
doubleblind render figures/main.py
```

## The rule that decides what to ask the reviewer

Ask what the evidence supports. Never ask it to verify that X.

> ✗ "Confirm that all four estimators fall below the card number."
> ✓ "For each numeric claim, state what these files actually support."

The first question has the answer in it. `doubleblind lint` reads the request
before it is sent and finds the phrases that carry the conclusion — six
mechanisms, because the wording changes and the mechanism does not.

And the reviewer has to be a **different model** with **zero context**. Same
model, fresh context still carries the priors that wrote the artifact. Record the
model id and the packet hash next to the verdict, or "a different model checked
it" is a claim about a conversation nobody can inspect.

## Polarity

The main sentence of a result is constructive: *we propose X, it solves Y, the
number is Z.* Audits, ablations and negative findings are supporting material.
A paper whose lead sentence is an audit reads as a complaint, and reviewers
score complaints badly even when they are right.

This is not a licence to bury the negative part. It is an instruction about
which sentence goes first.

## What survives

Every finding that survives its own verification becomes a mechanical check, in
CI, that fails on a deliberately broken input. A finding that stays a report is
worth one catch; the same finding as a check is worth every future one. Findings
in the first row of the table above convert; findings in the second row mostly
do **not**, and recording which is which is how you know the reviewer layer is
not optional.

## In this stage

- [`statistics.md`](statistics.md) — the four places a result quietly stops being true
