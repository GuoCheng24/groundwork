# Claims — the unit the paper is actually made of

A paper is not a description of what was run. It is a small number of claims,
each with evidence, arranged so a reader can check them. Drafting from the
results directory produces the first thing; drafting from a claim list produces
the second.

## The claim table, before any prose

| claim (one sentence) | evidence file | the check that re-derives it | what would falsify it |
|---|---|---|---|

Four columns, and the fourth is the one that changes the paper. A claim with no
falsifier is a description, and descriptions are what reviewers call
"incremental" without being able to say why.

A claim with no check does not go in the paper yet. See
[`../30-claim/SKILL.md`](../30-claim/SKILL.md).

## Polarity: the lead sentence is constructive

*We propose X, it solves Y, the number is Z.* Audits, ablations and negative
findings are supporting material and come after.

This is a rule about **ordering**, not about hiding. A limitation a reader would
notice must be in the paper, stated by you first — but a paper whose opening
sentence is an audit reads as a complaint, and reviewers score complaints badly
even when they are correct. One manuscript in audit shape was rated a serious
violation on exactly that ground, and the content did not change to fix it: the
order did.

## Scope belongs in the sentence

"The method improves accuracy" versus "on these four datasets, at this scale,
the method improves accuracy by 2 to 4 points". The second is less exciting and
is the one that survives. The tell for an over-scoped claim is that it contains
no numbers, no datasets and no conditions — add them and see whether anything
interesting is left. Often there is; when there is not, that is the finding.

## One claim, one number, one place

Derive every printed figure from one stored value at one declared precision.
The same underlying quantity written as 1.20 in one place and 1.21 in another —
two roundings of 1.205 — is not an error and it is still a reader's afternoon.

## The sentence that does not follow from its number

The most common defect that survives every mechanical check: the quantity is
correct and the causal claim, ranking or framing around it is not. *"Counting is
where thinking pays"* above a table where the counting task moved by exactly
zero. *"The furthest from the reference"* about a row that is the closest on the
other benchmark. *"Four estimators"* where two of them are provably the same
estimator.

No number-checker can see these. A reader who has not been told the conclusion
can. That is why the claim table has a fourth column and why
`30-claim` has three layers.

## From claim to section

One claim per subsection, its evidence immediately after it, its limitation in
the same subsection rather than exiled to the end. A limitations section that is
the only place limitations appear is a limitations section nobody believes.
