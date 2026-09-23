# Why the serial deep-dive never produces the breakthrough

A structural result about how research agents fail, and it is not about the
agent's intelligence.

## The measurement

One programme ran roughly **forty campaigns** in the serial style: one direction
at a time, days of cost per attempt, verification far outweighing generation,
parallelism of about one. Every one ended negative or turned into an audit.

The two breakthrough pipelines validated at the highest level share a skeleton
that this does not have — **cheap parallel generation, automated screening,
selection** — and they sample four to five orders of magnitude more.

> **Forty samples failing to find a breakthrough is a statistical necessity, not
> a capability problem.**

That reframing matters because the natural response to forty failures is to
conclude the ideas were bad, or the researcher was, and to try harder in the
same shape.

## The mechanism behind "it turned into an audit"

Auditing has a **guaranteed deliverable**: point the machinery at existing work
and something publishable comes out. Construction has no such guarantee. So the
more expensive each attempt is, the more rational it becomes to slide from
constructing toward auditing — and the slide feels like good judgement every
single time.

**The fix is not to audit less. It is to make attempts cheap enough that
construction stops being the risky option.**

## The adaptation for a hundred evaluations rather than a million

Copying a million-evaluation search is not available to most people, and
imitating its *shape* at forty samples is worse than useless. What transfers:

- **Small batches with strong priors.** Ten to thirty candidates per round, each
  carrying a stated reason it might win. Not random mutation — the prior is the
  thing that substitutes for sample count.
- **A tiered screen.** A cheap filter that kills most candidates in minutes, a
  middle tier in an hour, a full evaluation only for what survives. Most
  candidates must die at tier zero or the economics do not change.
- **A fixed evaluator.** The screen is written *before* the candidates and does
  not move. A screen adjusted after seeing the candidates is selection, and the
  survivors are selected for beating your judgement rather than the problem.
- **Kill on a number, not on a feeling.** Each tier has a threshold from
  `00-gate`, and the candidate that fails it is recorded in `archive/`.

## The honest caveat

This makes the search cheaper. It does not make the ceiling higher — the gate
still applies to every candidate, and a batch of thirty candidates in a
direction with no headroom produces thirty NO-GOs faster.

That is the correct outcome, and it is worth having faster.
