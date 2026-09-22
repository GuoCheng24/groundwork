# Statistics — the four places a result quietly stops being true

Not a course. Four specific failures that have each cost a submission.

## 1. Measure your instrument before quoting a difference

An official benchmark scorer, run **ten times on one unchanged file**, spanned
**0.37 points** on its headline metric and disagreed with itself on **2 prompts
out of 541**. Three runs had said it was stable — three draws were not enough to
see it.

Any difference between two arms smaller than that spread is not a finding about
the arms. Before comparing anything:

```bash
# score the same output N times; report the spread per metric
python scorer_noise.py --responses generations.jsonl --n 10
```

If the scorer involves a language detector, a tokeniser with a global random
state, or a model call, assume it moves until measured.

## 2. Benjamini–Hochberg does not always control what you think

BH controls FDR under independence and under positive regression dependence.
Under **correlated two-sided** tests — which is exactly what a few hundred
correlated features and two-sided comparisons give you — that guarantee does not
hold. Use **BY**, **e-BH**, or **knockoffs** when you need the guarantee, and
say which.

## 3. Exact tests at small n, and report the counts

At small n, report the discordant counts, not only a p-value: *b = 2, c = 2,
exact two-sided p = 1.000* tells a reader what happened; "n.s." does not. Use
exact binomial intervals rather than normal approximations, and state the
interval next to every proportion.

And distinguish **underpowered** from **no difference**, in those words. A
paired test on 32 pairs has not shown that an effect is absent; it has shown
that 32 pairs cannot resolve it. Pre-register the number of pairs below which
the verdict is "underpowered" and honour it.

## 4. Do not over-correct a correct estimate

A uniform random subsample's mean is an **unbiased** estimate of the full-set
mean. Calling it "not readable as a full-set number" is a mistake in the
opposite direction, and the correction is harder to catch than the original
error because it sounds cautious.

When several estimators are legitimate — direct, difference, regression,
post-stratified — report them all with their intervals rather than picking one,
and check whether any two are the same estimator in disguise. Under a binary
auxiliary variable, regression and post-stratification coincide exactly: four
rows, three readings.

## The rule underneath all four

The number is not the claim. Before writing a sentence about a difference, know
the resolution of the instrument that produced it, and write the sentence that
survives at that resolution.
