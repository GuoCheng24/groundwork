# Ablations — the arm that is missing is usually the informative one

An ablation table is a claim about *which part does the work*. Most tables
answer a different question: which of the variants we happened to build scores
best.

## The three arms that are almost never there

1. **A random or shuffled arm.** If shuffling the labels, the assignment or the
   structure preserves the effect, the effect is the pipeline. On one project a
   random assignment policy beat **every** learned repair method it was compared
   against, on the metric the paper led with.
2. **The trivial baseline, tuned.** Not the untuned one. See
   [`../00-gate/ceiling-first.md`](../00-gate/ceiling-first.md): a project
   compared its oracle ceiling against its own untuned baseline, saw 2.7× of
   headroom, and shipped a final gain of −0.0024 once the baseline was given the
   same budget.
3. **The capacity control.** If the proposed component adds parameters or
   compute, an arm with the same budget spent on nothing in particular tells you
   whether the component or the budget did the work.

## Plan the table before the runs

Write the table with its rows and its empty cells first, and ask of each row:
*what does this row rule out?* A row that rules nothing out is a row that will
be cut by a reviewer, and it is cheaper to cut it now.

Then decide, in advance, **which pattern would make you abandon the component**.
An ablation you would explain away whatever it showed is not an experiment.

## One variable per row

If two things change between rows, that row is uninterpretable, and it will be
the row a reviewer asks about. This includes things that do not feel like
variables: batch size, a different GPU, a re-run of a nondeterministic scorer.
All three have moved a benchmark result by more than the effect being ablated —
see [`hardware.md`](hardware.md).

## Report the counts, not only the means

A difference of means with no dispersion is not evidence. For paired outcomes
report the discordant counts; for repeated runs report the spread across seeds
*and* the spread of the scorer itself. If the arm-to-arm difference is smaller
than either, say so in the table rather than in a footnote.

## The honest negative ablation

When the component does not help, the row stays in the table and the sentence
above it says so. A paper that removes its own failed ablations is a paper whose
reviewers will run them.
