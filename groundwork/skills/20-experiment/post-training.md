# Post-training — the number that moves when nothing moved

Every rule here is from a measurement in
[batch-logprob-gap](https://github.com/GuoCheng24/batch-logprob-gap), which
publishes the script for each one, or from an identity you can check in three
lines. The stage is RL post-training — GRPO and every other clipped-surrogate
objective — because that is where a quantity that *should be exactly 1* is not,
and the debugging goes to the wrong place for days.

## The importance ratio moves without the policy moving

At the first inner epoch, `exp(logp_new - logp_old)` is the identity **by
construction**: the two log-probs come from the same weights. Whatever moves it
there is an off-policy correction the algorithm applies to a policy that never
changed.

It moves. bf16 matrix multiplication is not batch invariant, so the same
sequence scored in a batch of 1 and a batch of 8 gets different log-probs, and
the ratio leaves `[0.9, 1.1]` for **1.8% to 60.0% of tokens** depending on the
model. The policy is identical and the tokens are identical.

**Check it before you debug anything else**: score one batch of prompts at two
batch sizes with the same weights, and histogram the ratio. Ten minutes, and it
tells you whether the number you are chasing is a training signal or an
arithmetic artefact.

## It reaches the clip decision, so it is not a logging curiosity

The tempting dismissal is that a ratio of 1.02 changes nothing. It changes
which side of the PPO clip a token lands on: **clip status flips for 1.68% to
10.11% of tokens** across three models, and the flip rate depends on the
advantage distribution — 8.59% under gaussian advantages, 2.47% when 90% of
them are zero. A sparse advantage keeps more tokens away from the boundary, so
the same arithmetic noise reaches the gradient less often.

## And at 1.5B it does not reach the reward — report both halves

Six GRPO arms on GSM8K with Qwen2.5-1.5B-Instruct, 150 steps, two seeds each:
fp32 clone, fp16 clone, chunk = micro-batch, guided fp32 layers, fp32 head
only, and the default. **They finish within 0.013 reward of each other.** The
per-step reward noise is sd 0.14, so a 30-step mean carries an SE of about
0.026 — the arms are not distinguishable at this scale.

That is the whole finding, and both halves have to be said together. The noise
is real, it reaches the gradient, **and** it does not move what the model learns
here. Reporting only the first half sells a week of fp32 plumbing that costs
11.8 s/step against 9.3 and buys 0.004 reward inside an SE of 0.026.

The honest form of the rule: **measure whether it reaches your reward before
you pay to remove it.** The measurement is two arms and two seeds.

## The other term in the ratio: truncated sampling

The engine and the trainer may not be normalising over the same support. Under
`top_p=0.8, top_k=1024`, vLLM's processed log-probs are normalised over the
nucleus while the trainer's are over the full vocabulary, so the ratio carries
a factor equal to the kept probability mass: mean **0.896** against a kept mass
of **0.895**, with **51.8%** of tokens out of band. Renormalising the trainer's
log-prob over the replayed support removes it — mean 1.001, 4.3% out of band,
which is the engine-vs-trainer noise floor of the `top_p=1.0` control.

So: **find out which normalisation each side uses before concluding anything
about drift.** Half of your out-of-band tokens may be a definition, not a
divergence. The control row is what tells you which.

## A group-normalised advantage cannot blow up

GRPO z-scores the rewards inside a group of `G` samples. For **any** reward
distribution whatsoever,

```
max |a_i| = sqrt(G - 1)        exactly, and it is attained
```

The extreme configuration is one outlier against `G-1` equal values: with
`r = (x, m, m, ..., m)` the deviations are `d(G-1)/G` and `-d/G`, the population
variance is `d^2 (G-1)/G^2`, and the ratio is `(G-1)/sqrt(G-1)`. The outlier's
size cancels.

So "heavy-tailed rewards make the advantage explode" is not a thing that can
happen — the normalisation is a projection onto a sphere, and the tail is gone
before the objective sees it. Checked numerically against Cauchy, Pareto,
lognormal with sigma 8, binary and 90%-sparse rewards at `G` from 2 to 64: the
bound is never exceeded and is attained every time.

If your advantages look explosive, the cause is elsewhere — the ratio above,
the clip, or the KL term.

## The case the bound does not cover: a group where every reward is equal

All correct, or all wrong. On an easy prompt or an impossible one this is the
common case, and it should contribute **nothing**: the variance is zero, so the
normalisation is `0/0` and what happens next is decided by arithmetic rather
than by the algorithm.

Eight rollouts that all scored `0.7`, summed in a loop the way a reduction
does: the mean lands one ulp high, the variance comes out **1.2e-32** instead
of zero, and the advantage is the full **1.0**, with a sign chosen by rounding.
A group that carries no information emits a unit-scale gradient.

Two things make it hard to catch:

- **it depends on the reward value.** Eight copies of `0.7` and of `0.1` do it;
  `0.3`, `0.65` and `1/3` do not. So it appears on some prompts and not others,
  which reads like a property of the data;
- **it depends on your runtime.** CPython 3.12 gave `sum` compensated
  summation, so the identical code returns exactly `0.0` there and `1.0` on
  3.9. This was found by a test that passed on one and failed on the other.

The fix is an epsilon in the **denominator** — `(r - mean) / (std + eps)`,
which takes the same case to 1e-11 — and not a test for `std == 0`, which is
the branch that never fires. Better still, **drop groups whose rewards are all
equal before the normalisation**: that is what the epsilon is approximating,
and it says so in the code.

## What to check, in order

1. the ratio at the first inner epoch, which should be exactly 1;
2. the normalisation each side uses, with a `top_p=1.0` control row;
3. the clip fraction, and whether it flips between two runs of the same weights;
4. **whether any of it reaches the reward** — two arms, two seeds, and the SE of
   your own reward curve before the comparison;
5. the group size, and what happens when a group's rewards are all equal.
