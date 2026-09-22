# groundwork ⛰️🔬

[![ci](https://github.com/GuoCheng24/groundwork/actions/workflows/ci.yml/badge.svg)](https://github.com/GuoCheng24/groundwork/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![deps](https://img.shields.io/badge/dependencies-none-2e7d32)](#)
[![licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![stars](https://img.shields.io/github/stars/GuoCheng24/groundwork?style=flat&color=gold)](https://github.com/GuoCheng24/groundwork/stargazers)

**Your agent can hand you a paper by morning. The harder question is whether the
project should have existed — and that one is answerable in ten minutes, before
the night is spent.**

A full research pipeline for coding agents — direction, gate, experiment, claim,
paper, submission, memory — with the stage every other toolkit is missing: **one
that returns NO-GO.**

```bash
git clone https://github.com/GuoCheng24/groundwork && cd groundwork
python groundwork.py gate --baseline 0.812 --oracle 0.830 --se 0.019      # NO-GO, in ten seconds
```

Python 3.9+, **no dependencies**, nothing to configure. Works with Claude Code,
Codex CLI, DeepSeek, Kimi, or any agent that reads Markdown and runs a shell.

> **Never used a coding agent before?**
> → [**Getting started**](docs/getting-started.md) · [**上手指南（中文）**](docs/getting-started.zh.md)
>
> From installing Claude Code or Codex to running a whole project with one —
> including the case every other tutorial skips: **a shared cluster node with no
> direct route to the internet.** The reverse tunnel, the `no_proxy` entry that
> makes `git clone` hang on a socket that will never open, why the IDE panel
> disconnects while the CLI on the same machine is fine, and how to share a GPU
> node with people who are not you.

| command | what it refuses |
|---|---|
| `groundwork gate` | a direction whose ceiling, baseline, random arm or positive control already answers it |
| `groundwork lit` | an occupancy verdict when the index that would have found the competitor did not answer |
| `groundwork prereg` | a pre-registration that version control says is younger than its own results |
| `groundwork cluster` | a card whose free memory is somebody else's leftovers, and one arm split across two GPU models |
| `groundwork ledger` | a cause of death that is free text nobody can count |
| `groundwork reach` | a bot-challenge page being read as a paper |
| [`doubleblind`](https://github.com/GuoCheng24/doubleblind) | a number that exists in no file, a brief that tells the reviewer what to conclude, a caption nobody can read |

Every one of those refusals exists because the unrefused version shipped.

## The pipeline

```
 00-gate ──▶ 10-direction ──▶ 20-experiment ──▶ 30-claim ──▶ 40-write ──▶ 50-submit
   │             │                  │               │            │            │
 refuse      candidates       pre-register,     three layers   claims     compliance,
 the         that can         seal, commit,     blind to       first,     rebuttal,
 direction   survive it       then launch       different      figures    resubmit,
                              across idle       defects        audited    talk
                              GPUs
   └────────────────────── 90-memory: the archive of what died, and why ──────────┘
```

Seven stages, forty-two files. Each stage decides whether you are allowed into
the next one: a menu asks you to know which skill to call, a gate tells you.

Every file carries the failure that produced its rules, because the rules are
not obvious and the failures are what make them stick — a scorer that moved 0.37
points on a file that never changed, a preview renderer that lies in both
directions, an occupancy search that invented its own competitor, a
pre-registered "clean hardware test" that was not clean until a control existed.

---


### What is in each stage

| stage | what it decides | notes, each written from a failure |
|---|---|---|
| [`00-gate`](skills/00-gate/) | Gate — the four numbers that decide | [`breakthrough`](skills/00-gate/breakthrough.md) · [`ceiling-first`](skills/00-gate/ceiling-first.md) · [`metric-validity`](skills/00-gate/metric-validity.md) · [`positive-control`](skills/00-gate/positive-control.md) · [`two-toolboxes`](skills/00-gate/two-toolboxes.md) |
| [`10-direction`](skills/10-direction/) | Direction — candidates, not ideas | [`kill-argument`](skills/10-direction/kill-argument.md) · [`lit-review`](skills/10-direction/lit-review.md) · [`occupancy`](skills/10-direction/occupancy.md) · [`originality`](skills/10-direction/originality.md) · [`venue-fit`](skills/10-direction/venue-fit.md) |
| [`20-experiment`](skills/20-experiment/) | Experiment — sealed first, then launched | [`ablations`](skills/20-experiment/ablations.md) · [`data-hygiene`](skills/20-experiment/data-hygiene.md) · [`hardware`](skills/20-experiment/hardware.md) · [`implementation`](skills/20-experiment/implementation.md) · [`long-runs`](skills/20-experiment/long-runs.md) · [`shared-machine`](skills/20-experiment/shared-machine.md) |
| [`30-claim`](skills/30-claim/) | Claim — three layers, blind to different things | [`citations`](skills/30-claim/citations.md) · [`integrity`](skills/30-claim/integrity.md) · [`review-loop`](skills/30-claim/review-loop.md) · [`statistics`](skills/30-claim/statistics.md) |
| [`40-write`](skills/40-write/) | Write — from claims, not from results | [`build`](skills/40-write/build.md) · [`captions`](skills/40-write/captions.md) · [`claims`](skills/40-write/claims.md) · [`diagrams`](skills/40-write/diagrams.md) · [`figures`](skills/40-write/figures.md) · [`structure`](skills/40-write/structure.md) · [`theory`](skills/40-write/theory.md) |
| [`50-submit`](skills/50-submit/) | Submit — and everything after | [`compliance`](skills/50-submit/compliance.md) · [`delivery`](skills/50-submit/delivery.md) · [`patent`](skills/50-submit/patent.md) · [`rebuttal`](skills/50-submit/rebuttal.md) · [`resubmit`](skills/50-submit/resubmit.md) · [`talks`](skills/50-submit/talks.md) |
| [`90-memory`](skills/90-memory/) | Memory — the archive is the asset | [`postmortems`](skills/90-memory/postmortems.md) · [`wiki`](skills/90-memory/wiki.md) |

## The gate: four numbers, ten minutes, before anything

```console
$ groundwork gate --baseline 0.812 --oracle 0.830 --se 0.019

  headroom            +0.0180  (oracle 0.8300 - baseline 0.8120)
  one standard error  0.0190
  headroom in SEs     0.95
  smallest detectable 0.0532  (80% power, two-sided 0.05)

NO-GO.
  * Headroom is 0.95 SE, under the 2 SE this gate requires. Even a method that
    captured the entire gap would not separate from the baseline on this split.

Record it in archive/ with the cause, so the next person who has this
idea - including you, in four months - finds the verdict before the work.
```

Four measurements, on the same split, before the first real experiment:

| # | measurement | what it rules out |
|---|---|---|
| 1 | **strongest trivial baseline**, tuned as hard as the proposal | the signal was never structural |
| 2 | **oracle** — perfect access to whatever the proposal estimates | there was no headroom to win |
| 3 | **random arm** — shuffled labels or random assignment | the task never needed a learned policy |
| 4 | **positive control** — a case where the effect must be recovered | a null would measure your pipeline |

The gate does not ask what the method is. **A gate that knows what you are
hoping for is not a gate.**

It refuses when headroom is under two standard errors, when a perfect method
would still be reported as null on this split, when the random arm reaches the
baseline, or when the positive control does not recover. When it passes, it
prints the share of the headroom a method must capture to be detectable at
all — a number worth knowing before the work rather than after.

---

### The two sentences that make this a gate rather than advice

One project measured its oracle ceiling in its **tenth** session. The ceiling was
closed — there was nothing for any method to win. Measured in session one, every
conclusion of that project was available in a day, and the other nine sessions
need never have happened.

A later project did measure the ceiling on day one and saw an apparent **2.7× of
headroom**, so the gate passed. The baseline it compared against was **its own,
untuned**. The right comparison — three numbers read straight from the same
region of the same data — **beat the oracle ceiling by 0.047**. The project
should have died that morning. It went on to pass six further adversarial checks
over two weeks, and **not one of them asked whether the control had been
tuned**. Given the same budget, the final gain over that baseline was
**−0.0024**: indistinguishable from nothing, in the wrong direction.

So the rule has a second half, and it is the half that matters: *the baseline
gets the same tuning budget as the method.* A baseline nobody tried to make win
is a strawman with error bars. See [`skills/00-gate/ceiling-first.md`](skills/00-gate/ceiling-first.md).

## The archive: ten ways a direction dies

[`archive/causes-of-death.json`](archive/causes-of-death.json) records ten, each
with the cheap test that would have ended it sooner and what it cost when it did
not. They are not hypothetical:

| cause | what happened | cost |
|---|---|---|
| ceiling too low | the method worked; an oracle beat the baseline by 1.6–1.8 points, so the whole space available to any method was inside the noise | weeks |
| a thick baseline absorbed it | a structured encoding reproduced across cohorts; a dense local baseline with no structure reached the same number | weeks |
| positive control collapsed | the main analysis returned a clean null, and so did the case where the effect is known to exist | the whole study |
| reduces to known | a failure mode that looked new was a known balance condition under a change of variables | weeks |
| already occupied | a qualitative mechanism published in 2017, its closed form in 2003 | days–weeks |
| a random arm won | every learned repair policy was compared against the others and looked ordered; random assignment beat all of them | weeks |
| external validation collapsed | strong in development, absent in the external cohort | months |
| our own supplement | the "new paper" was a table in the group's own supplementary material | days |
| leakage flattered it | perfect discrimination from selecting features before splitting; redone correctly, chance | a submission |
| its ceiling was a smaller venue | it genuinely worked, and both routes to a flagship claim collapsed onto things already known | a rejection cycle |

Directions die in batches. One programme killed 32 of 32 candidates at this
stage; another 16 of 16. That is the gate working — but only if the verdicts are
written down.

---

## The occupancy gate: a silent index is not an empty literature

```console
$ groundwork lit occupancy "bfloat16 batch invariance importance ratio" -n 6
 1. 2025  ...
 ...
# backends: arxiv: ok, openalex: NO ANSWER, semanticscholar: ok

# ====================================================================
#  NO VERDICT AVAILABLE. The primary index did not answer, so this is
#  a preprint-only search. "Nothing occupies this" cannot be concluded
#  from it - a spent quota and an empty literature look identical.
# ====================================================================
```

That refusal is the whole point of the tool. The first version degraded silently
to a preprint-only search and printed the results as though the search were
complete — and the answer a spent quota produces is *"nobody has done this"*,
which is the most expensive wrong answer available at this stage.

`lit` also carries the three traps in checking that a paper exists at all:

- an occupancy search **can invent its neighbours**, so every candidate that
  matters is verified separately;
- a verifier that fails on the network **reports a hallucination** — a batch of
  failures at once is a network diagnosis, and `lit verify` returns a distinct
  exit code for it rather than a verdict;
- *"that identifier looks too recent to be real"* is **relative to today's
  date**, and has produced false accusations against real papers. The current
  year is resolved at run time, never written into the code.

And `lit journal` reports a venue's citation metrics with the caveat attached,
because one such figure quoted from memory once mis-set a venue choice by a
factor of two — and the freely available proxy was itself off by a factor of
three from the official number.

## The experiment stage: sealed first, then launched

```bash
groundwork prereg new prereg/PREREG_run3.md --title "run 3"   # six required sections
groundwork prereg seal prereg/PREREG_run3.md
git commit -m "Pre-register run 3"                              # BEFORE any generation
...
groundwork prereg verify prereg/PREREG_run3.md --results results/metrics_run3.json
```

`verify` checks the seal, checks every section is filled in, and **checks with
git that the pre-registration was committed before the results it governs**.

```console
  FAIL results.json was committed BEFORE the pre-registration was committed.
       A pre-registration written after its results is a write-up.
```

The six required sections are the six that get quietly dropped: what is held
fixed, what changes, the pre-stated analysis, **the stopping rule**, **what gets
written if it comes out the other way**, and **what was already known when this
was written**. That last one is not a confession box — an arm launched after
seeing a partial score is not disqualified, an undisclosed one is.

### and launched wherever the GPUs actually are

```console
$ groundwork cluster survey --nodes gpu01 gpu02 gpu03 gpu04
gpu03:
   [0] NVIDIA L40                   16.2 GB free of  45.0   util  97%
   [1] NVIDIA L40                   48.0 GB free of  48.0   util   0%   idle
...
14 idle card(s) across 3 reachable node(s).

$ groundwork cluster plan --nodes gpu01 gpu03 --need-gb 20 --shards 4 \
      --command 'python eval.py'
```

Three habits, each learnt by losing a night: **somebody else's job is not free
memory** (a card with 5 GB free is not idle, and a job placed there dies at 3
a.m.); **leave a card per node**, and leave an idle one rather than the scraps;
and **one arm, one GPU model** — `plan` refuses to split an arm across models
unless told the split is only a throughput knob.

That last refusal is not caution. The same weights, the same seed, greedy
decoding, the same batch size and the same scorer, on two different GPU models,
[scored 76.89% and 75.42%](https://github.com/GuoCheng24/ifeval-reproduction) —
1.48 points from changing nothing but the card. The same arm repeated on a
second card of the *same* model reproduced 541 of 541 generations byte for byte.

---

## The claim stage: three layers, blind to different things

| layer | finds | cannot see |
|---|---|---|
| re-derivation | a number that exists in no file; a bound stated tighter than the interval | a **correct number inside a sentence that does not follow from it** |
| a reader with no context | claims that do not follow; a comparison pointing the wrong way | a fabricated number that looks plausible |
| the rendered figure | labels that read as one word; a caption unreadable at the size it will be seen | whether the shape a reader takes from the figure is the shape the data supports |

Implemented in [**doubleblind**](https://github.com/GuoCheng24/doubleblind),
installable on its own. Its ledger records 20 real defects with the layer that
missed each one; 9 were caught by a person looking at the rendered artifact,
which is the number the third layer exists to shrink.

And the rule that decides what to ask a reviewer: **ask what the evidence
supports, never ask it to verify that X.** The first question has the answer in
it, and `doubleblind lint` finds the phrases that carry it before the request is
sent.

---

## Where every rule was paid for

Not a bibliography — repositories where these rules run in CI on every push.

| repository | what it demonstrates |
|---|---|
| [batch-logprob-gap](https://github.com/GuoCheng24/batch-logprob-gap) | the same measurement on three GPUs across two architectures; the effect is on all three and fp32 removes it on all three; the control is a re-run of the original card that must reproduce it cell for cell |
| [ifeval-reproduction](https://github.com/GuoCheng24/ifeval-reproduction) | a pre-registration chain CI re-hashes on every push; an official scorer measured against itself — ten runs on one unchanged file span 0.37 points and disagree on 2 prompts of 541 |
| [taichu-eval-reproduction](https://github.com/GuoCheng24/taichu-eval-reproduction) | a reproduction whose verdict turned on how eleven truncated generations were counted, and which says so |
| [doubleblind](https://github.com/GuoCheng24/doubleblind) | the three claim layers, each with a test asserting the defect it *cannot* catch |

---

## Using it with your agent

The stages are plain Markdown under [`skills/`](skills/) — no framework, no MCP
server, no second subscription.

- **Claude Code** — `ln -s .../groundwork/skills/* .claude/skills/`, then ask
  for a stage by name.
- **Codex CLI** — `codex exec < skills/00-gate/SKILL.md` for a fresh session.
- **DeepSeek / Kimi / any OpenAI-compatible endpoint** — the skill file is the
  system prompt; the tools are shell commands.

See [`adapters/`](adapters/) for the exact invocations, including how to get a
reviewer that is genuinely a *different* model for the claim stage.

---

## What is here, and what is not

`groundwork` is not a promise that an agent will produce a publishable paper
unattended. The gate exists because most directions should not be started, and a
pipeline that never returns NO-GO is selling something.

It is also not, today, a drop-in replacement for the largest generative
toolkits. Honestly, side by side with
[ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep), which
is careful work and worth using:

| | ARIS | groundwork |
|---|---|---|
| a stage that returns **NO-GO** before the work | — | **yes**, from four measurements |
| an archive of **how directions die**, each with the test that would have caught it | failed ideas as anti-repetition memory | **ten causes**, with the cheap test and the cost |
| pre-registration **version control can date** | — | **yes**, and it fails when the results are older |
| **multi-node idle-GPU placement**, shard ownership that survives a restart | one configured server, vast.ai, Modal | **yes**, and it refuses to split one arm across two GPU models |
| verification layers **blind to different defects**, each with a test asserting what it cannot catch | an LLM review gate with an un-forgeable reviewer-identity chain | **three layers**, no MCP required |
| literature **ingestion** (OpenAlex, Crossref, arXiv, Semantic Scholar) | **yes, several skills** | **yes**, one tool — re-ranked, and it **refuses an occupancy verdict when the primary index is silent**, because a spent quota and an empty literature look identical |
| a **record that compounds** — what died, what got through, what converted into a check | `meta-optimize` reads an event log | **yes**, `ledger`, with a closed taxonomy so the causes can be counted |
| paper compilation and reference style | **yes** | **yes**, as a recipe with the three silent variables that break it |
| Overleaf sync | **yes** | no |
| slides, posters, talks | **yes** | **yes**, with the rendering discipline — a deck was 17 pages in one renderer and 11 in another |
| theory track | `proof-orchestrator`, `proof-writer` | **yes**, one file: attack a *stated* open problem, and the three ways a result turns out to be known |
| grant proposals | **yes** | no |
| **handing a manuscript to a human collaborator** — tracked-change formatting regressions, orphaned equation objects, reference-manager fields, metadata that leaks through the explanation document | — | **yes**, from a manuscript delivered round after round and found unclean each time |
| **caption audit** — panel letters, a stated direction that is backwards, a colour encoding that contradicts the discussion | — | **yes** |

| patents | five skills | one skill, written from a live prosecution |

**If you already use ARIS, the useful move is not to switch.** Run
`groundwork gate` before its pipeline starts, and the `30-claim` layers before
anything leaves. Those are the two places it has nothing, and they are the two
places the expensive mistakes are.

## Licence

MIT.
