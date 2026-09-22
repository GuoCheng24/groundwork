# Ceiling first — the measurement that was worth more than the project

The rule: **the first section of a project document is the ceiling and the
trivial baseline, and work does not start while it is empty.**

It is a hard gate rather than advice because it has been learnt twice, the
second time after it was already written down.

## What it cost the first time

One project measured its oracle ceiling in its **tenth** session. The ceiling
was closed — there was nothing for the method to win. Measured in session one,
every conclusion of that project was available in a day and the other nine
sessions need never have happened.

**That lesson is worth more than the entire scientific output of the project it
came from**, which is why it is a gate and not a suggestion.

## What it cost the second time, after the rule existed

A later project *did* measure its oracle ceiling on day one, and saw an apparent
**2.7× of headroom**. Gate passed.

The baseline it compared against was **its own, untuned**. The correct
comparison was three numbers read directly from the same region of the same
data — an area, a maximum and a mean. Together they **beat the oracle ceiling by
0.047**. The project should have died that morning.

Instead it passed six further adversarial checks over two weeks, and not one of
them asked whether the control had been tuned. After giving the baseline the
same budget, the proposed method's gain over it was **−0.0024** —
indistinguishable from nothing, in the wrong direction.

So the rule has a second half, and it is the half that matters:

> **The ceiling is measured against the strongest trivial baseline, and that
> baseline gets the same tuning budget, the same regularisation search and the
> same attention as the method.**

A baseline nobody tried to make win is not a baseline. It is a strawman with
error bars.

## The third question, about the metric itself

Ask whether changing the metric's definition — a tolerance, a connectivity rule,
a rounding convention — flips the conclusion. If it does, that metric cannot
carry a claim on its own.

One project's headline metric could be improved 25.9% by **random assignment**,
which beat every learned method it was compared against. Reported alone, that
metric carried no information at all.

## The three self-checks on the gate itself

1. **Is the comparison corrected for multiplicity?** A gate that quietly runs
   six comparisons and reports the best is not a gate.
2. **Is there a shuffled control?** If the pipeline produces the same effect on
   shuffled labels, the effect is the pipeline.
3. **Does the baseline reach the level an independent implementation would?**
   If your baseline is below the published number for the same method on the
   same data, you are comparing against your own bug.

## In practice

```bash
proofground gate --baseline <strongest trivial, tuned> \
                 --oracle <perfect access to the estimated quantity> \
                 --se <standard error of a difference on this split> \
                 --random <shuffled or randomly assigned arm>
```

Fill the baseline in last, after you have tried to make it win.
