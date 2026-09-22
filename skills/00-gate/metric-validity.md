# Does the metric carry the claim?

A gate that is skipped almost universally: before measuring anything, ask
whether the number you are about to optimise can support the sentence you intend
to write.

## Three questions

**1. Can it be improved by doing more of something trivial?**

If the metric rewards more detections, more edges, more segments, then "do more"
is a strategy and the metric alone carries no information. On one project a
**random assignment policy improved the headline metric by 25.9% and beat every
learned method** it was compared against. The metric was not wrong; reporting it
alone was.

The fix is not to abandon the metric. It is to report it **with** the quantity
that trivial inflation costs — precision alongside recall, a false-positive rate
alongside a detection rate — and to include the trivial strategy as an arm.

**2. Does changing its definition flip the conclusion?**

Tolerances, connectivity rules, matching radii, rounding conventions, how ties
are handled. Recompute the headline comparison under two defensible definitions.
If the ordering changes, the metric cannot carry a claim on its own, and that
fact belongs in the paper rather than in a choice nobody sees.

**3. Is its own noise smaller than the effect?**

The scorer is an instrument. One official benchmark scorer, run ten times on an
unchanged file, spanned 0.37 points on its headline metric and disagreed with
itself on two prompts of 541 — and three runs had said it was stable. Any
arm-to-arm difference smaller than that spread is not a finding about the arms.
Measure it before quoting a difference; see
[`../30-claim/statistics.md`](../30-claim/statistics.md).

## The composite trap

A metric built as a mean of sub-metrics can move because one sub-metric moved,
in a direction the sentence does not claim. Report the components alongside the
composite, always — a composite that improves while its most relevant component
does not is a result about the composite's weighting.

## What to record

The metric, its definition including every tolerance, the trivial strategy that
inflates it, its measured noise, and the second definition you checked against.
Five lines, in the project document, before the first experiment.
