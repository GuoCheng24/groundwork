# The positive control — run it before the experiment, not after the null

The cheapest experiment in any project, and the one that decides whether the
expensive one can mean anything.

## What it is

A case where the effect **is known to exist and must be recovered**. Not a
sanity check that the code runs: a measurement that would fail if the pipeline
could not detect the thing you are about to look for.

Examples of the shape:

- the association everyone in the field already reports, in your pipeline, on
  your data;
- a synthetic injection of the effect at a known size;
- a variable that is a known proxy for the outcome by construction.

## Why it goes first

A null result with no positive control is not a result. It is compatible with
"there is no effect" and with "this pipeline cannot see effects", and nothing in
the null distinguishes them.

One project's main analysis returned a clean null. So did the positive control.
Two weeks of interpretation had been spent on a pipeline finding.

Running it first costs an afternoon and changes what a null would be worth.
Running it after a null is a much harder conversation with yourself, because now
you are looking for a reason to disbelieve your own result.

## Pre-state the floor

The control needs a number it must clear, written before it runs:

```bash
proofground gate --baseline ... --oracle ... --se ... \
    --positive-control 0.80 --positive-control-floor 0.70
```

Without a floor, a weak-but-non-zero positive control gets interpreted
generously, which is the same failure one level up.

## The negative control, too

The mirror image: a case where the effect **must not** appear. Shuffled labels,
a permuted grouping, an outcome that is unrelated by construction. If the
pipeline finds something there, the pipeline is the finding.

Most projects have one of the two. The pair is what makes a null publishable and
a positive finding believable, and both together still cost less than one real
experiment.

## What to record

Both controls, their thresholds, and their results, in the project's first
results file — before the main analysis exists. They are the evidence that the
main number means what you will say it means.
