# Integrity — the checks that catch what looks like a good result

Not misconduct. The ordinary ways a pipeline produces a number that is too good,
and the specific checks that catch each one.

## Leakage: the most common cause of a remarkable number

Selection, normalisation, imputation or threshold-fitting performed **before**
the split, on the whole dataset, then evaluated by cross-validation. The
resulting figure can be near-perfect and is measuring the leak.

One manuscript reported perfect discrimination from feature selection performed
on the full dataset. Redone with selection inside the fold, the effect went to
chance.

**Rule: a result far better than the field's best is a leakage report until
proven otherwise.** Move every fitted step inside the fold and re-run before
telling anyone, including yourself.

## The positive control, and what a null means without one

A clean null is only informative if the pipeline can recover an effect that is
known to exist. Run the positive control **first** — it is cheaper than the
experiment and it decides whether a null will mean anything. A study whose main
analysis and positive control both returned null measured the pipeline.

## Batch and site

If the acquisition site, scanner, batch or calendar period predicts the outcome,
a model will learn it and a random split will reward it. Check the association
explicitly, split by the grouping rather than at random, and if the grouping
cannot be adjusted for — because the dataset has no date column, for instance —
that is a limitation that belongs in the paper, stated by you.

## Multiplicity, with the right procedure

Benjamini–Hochberg controls the false discovery rate under independence and
positive dependence. Under **correlated two-sided** tests — a few hundred
correlated features, two-sided comparisons — that guarantee does not hold. Use
BY, e-BH or knockoffs and say which. See [`statistics.md`](statistics.md).

## Rounding, and the same number written twice

One manuscript wrote the same underlying value as 1.20 in one place and 1.21 in
another, from two different roundings of 1.205. Neither is wrong; together they
are a reader's afternoon. Derive every printed figure from one stored value at
one declared precision.

## Words that make a claim stronger than the design

- **"prespecified"** on an analysis added after the data were seen. Found four
  times in one manuscript, plus once in the introduction;
- **a date range in the methods** that contradicts analyses added later;
- **"significant"** for a difference inside the instrument's own noise.

Grep for the first, check the second against the change history, and require the
third to carry an interval.

## The rule underneath

Every one of these produces a *better-looking* result, which is why none of them
gets caught by somebody checking whether the work went well.
