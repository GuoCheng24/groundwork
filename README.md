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
python -m groundwork gate --baseline 0.812 --oracle 0.830 --se 0.019      # NO-GO, in ten seconds
```

**As a plugin**, inside Claude Code — the seven stages, no clone, no `PATH`:

```
/plugin marketplace add GuoCheng24/groundwork
/plugin install groundwork
```

Codex CLI reads the **same seven files** rather than a parallel mirror, so the
two cannot drift apart. Add the tools with `pip install groundwork-research`;
the stages tell you when to reach for each, and work without them.

Python 3.9+, **no dependencies**, nothing to configure. Works with Claude Code,
Codex CLI, DeepSeek, Kimi, or any agent that reads Markdown and runs a shell.

> **Never used a coding agent before?**
> → [**Getting started**](docs/getting-started.md) · [**上手指南（中文）**](docs/getting-started.zh.md)
> → [**A worked example**](docs/worked-example.md) — one direction, from idea to
> killed, in an afternoon. It ends in a NO-GO, which is the outcome this exists
> to produce cheaply and the one no other walkthrough shows you.
>
> From installing Claude Code or Codex to running a whole project with one —
> including the case every other tutorial skips: **a shared cluster node with no
> direct route to the internet.** The reverse tunnel, the `no_proxy` entry that
> makes `git clone` hang on a socket that will never open, why the IDE panel
> disconnects while the CLI on the same machine is fine, and how to share a GPU
> node with people who are not you.

| command | what it does, or refuses |
|---|---|
| `groundwork init` | starts a project whose first section is the gate, **left empty on purpose** |
| `groundwork night` | an overnight loop optimised for not stopping — here the first non-zero exit ends the night, and the morning report says which steps therefore never ran |
| `groundwork check` | a sweep that reports a pass because there was nothing to check, and an exemption that quietly disarms the check next to it |
| `groundwork gate` | a direction whose ceiling, baseline, random arm or positive control already answers it |
| `groundwork lit` | an occupancy verdict when the index that would have found the competitor did not answer |
| `groundwork prereg` | a pre-registration that version control says is younger than its own results |
| `groundwork probe` | `which` answering for `PATH` and being read as an answer about the machine, and a filesystem crawl that did not finish being read as an absence |
| `groundwork cluster` | a card whose free memory is somebody else's leftovers, and one arm split across two GPU models |
| `groundwork shard` | work split so that a restart takes an item twice or not at all, and a merge that quietly keeps one of two different answers for the same item |
| `groundwork watch` | a run that was never alive, an empty log read as silence rather than buffering, and a watch that dies with the session that set it up |
| `groundwork ledger` | a cause of death that is free text nobody can count |
| `groundwork stats` | the exact interval, the exact paired test, the smallest effect the split can resolve, and BH against BY — so nobody re-implements them |
| `groundwork noise` | a difference being quoted without the spread of the instrument that produced it |
| `groundwork reach` | a bot-challenge page being read as a paper |
| `groundwork install` | attaches the stages to Claude Code, Codex, or anything that reads Markdown |
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

 groundwork check ── runs every gate above over a project, in one command
```

Seven stages, 50 files. Each stage decides whether you are allowed into
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
| [`00-gate`](groundwork/skills/00-gate/) | Gate — the four numbers that decide | [`breakthrough`](groundwork/skills/00-gate/breakthrough.md) · [`ceiling-first`](groundwork/skills/00-gate/ceiling-first.md) · [`metric-validity`](groundwork/skills/00-gate/metric-validity.md) · [`positive-control`](groundwork/skills/00-gate/positive-control.md) · [`two-toolboxes`](groundwork/skills/00-gate/two-toolboxes.md) |
| [`10-direction`](groundwork/skills/10-direction/) | Direction — candidates, not ideas | [`kill-argument`](groundwork/skills/10-direction/kill-argument.md) · [`lit-review`](groundwork/skills/10-direction/lit-review.md) · [`occupancy`](groundwork/skills/10-direction/occupancy.md) · [`originality`](groundwork/skills/10-direction/originality.md) · [`venue-fit`](groundwork/skills/10-direction/venue-fit.md) |
| [`20-experiment`](groundwork/skills/20-experiment/) | Experiment — sealed first, then launched | [`ablations`](groundwork/skills/20-experiment/ablations.md) · [`data-hygiene`](groundwork/skills/20-experiment/data-hygiene.md) · [`post-training`](groundwork/skills/20-experiment/post-training.md) · [`hardware`](groundwork/skills/20-experiment/hardware.md) · [`implementation`](groundwork/skills/20-experiment/implementation.md) · [`long-runs`](groundwork/skills/20-experiment/long-runs.md) · [`shared-machine`](groundwork/skills/20-experiment/shared-machine.md) |
| [`30-claim`](groundwork/skills/30-claim/) | Claim — three layers, blind to different things | [`citations`](groundwork/skills/30-claim/citations.md) · [`integrity`](groundwork/skills/30-claim/integrity.md) · [`review-loop`](groundwork/skills/30-claim/review-loop.md) · [`statistics`](groundwork/skills/30-claim/statistics.md) |
| [`40-write`](groundwork/skills/40-write/) | Write — from claims, not from results | [`build`](groundwork/skills/40-write/build.md) · [`captions`](groundwork/skills/40-write/captions.md) · [`claims`](groundwork/skills/40-write/claims.md) · [`diagrams`](groundwork/skills/40-write/diagrams.md) · [`figures`](groundwork/skills/40-write/figures.md) · [`structure`](groundwork/skills/40-write/structure.md) · [`theory`](groundwork/skills/40-write/theory.md) |
| [`50-submit`](groundwork/skills/50-submit/) | Submit — and everything after | [`compliance`](groundwork/skills/50-submit/compliance.md) · [`delivery`](groundwork/skills/50-submit/delivery.md) · [`patent`](groundwork/skills/50-submit/patent.md) · [`rebuttal`](groundwork/skills/50-submit/rebuttal.md) · [`resubmit`](groundwork/skills/50-submit/resubmit.md) · [`talks`](groundwork/skills/50-submit/talks.md) |
| [`90-memory`](groundwork/skills/90-memory/) | Memory — the archive is the asset | [`postmortems`](groundwork/skills/90-memory/postmortems.md) · [`wiki`](groundwork/skills/90-memory/wiki.md) |

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
is a strawman with error bars. See [`groundwork/skills/00-gate/ceiling-first.md`](groundwork/skills/00-gate/ceiling-first.md).

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

### Before either: what can this machine actually do

```console
$ groundwork probe
  GPU        6 card(s), 0 idle
  /dev/shm   126 GB, 0.3 GB used - this is RAM, and it is charged to you
  on PATH    git ssh rsync nvidia-smi gcc pandoc tectonic gh jq
  modules    69 in `module avail` - a catalogue that is deliberately not on PATH
  INSTALLED BUT NOT ON PATH - `which` says no and the machine says yes:
             ninja:   .../envs/af3/bin/ninja
             soffice: .../tools/lo76/opt/libreoffice7.6/program/soffice
  isolation  unprivileged user namespaces: yes; bwrap fuse-overlayfs podman
             /dev/kvm no, cgroup v2 delegation no
             so: file-system and process isolation without root, but no VM.
```

Both of those were real. `soffice` was declared unavailable for weeks on the
strength of `which soffice` returning nothing, while LibreOffice sat eight
directories deep under a shared mount; documents were checked with an
approximate renderer that under-reported overflowing text. `ninja` was missing
from `PATH` when an inference stack's JIT backend shelled out to it, and the
run was worked around instead of fixed. **A negative from `which` is a
statement about `PATH`.**

So is a negative from a filesystem crawl, and `probe` says which: it names the
roots it searched and the depth, lists the large mounts it did **not** search,
and if the crawl hit its time budget it says the results are unfinished
searches rather than absences. On a cluster the fast door is the module system,
which is where `probe` looks first.

The third block is the one that reopens work. "No root, so no containers" was
written down here as a constraint and was simply false: unprivileged user
namespaces, `bwrap` and `fuse-overlayfs` were all available.

### Split it so a restart loses nothing

```console
$ groundwork shard merge 'out_s*.jsonl' --expect 2638
  out_s0.jsonl: 528 rows
  ...
1595 distinct id(s)

SHORT BY 1043: expected 2638. A shard that died leaves a hole that no file
reports, because every shard file is complete on its own.
```

The rule is one line, and it is the whole tool: **slice the item list before
filtering out what is already done.** Slice afterwards and ownership depends on
how far each shard happened to get — restart two shards at different points and
they take the same item while a third is taken by nobody. Nothing errors, and
every shard file is internally consistent. `shard plan` prints that line in the
shape your harness needs it, and a test demonstrates the wrong order producing
both the overlap and the orphan rather than asserting that it would.

`merge` refuses two different answers for one id, naming the fields that
differ. That is not a duplicate to be deduped: two runs produced different
answers, and which one survives depends on the order the files were listed in.

### Then launch it so that it outlives the session

```console
$ groundwork watch start --name run3 -- python eval.py --shard 0/4
started run3 (pid 41883)

waiting 90s before believing it started...

IT IS ALREADY GONE (exit 1). The head of its log:

  | weights not found
```

Ninety seconds, not zero: a job that fails to load its weights looks exactly
like a job that is training, at launch. When the head of the log is **empty**,
`watch` says so as *buffering* rather than as silence — those two look
identical from outside, and only one of them loses everything in a crash.

When the run ends, `groundwork watch status` writes `archive/runs/<name>.DONE`
with the verdict, and exits non-zero if the log holds a traceback, an OOM, a
`Killed` or a NaN. The flag file is the point. A watch set up *inside* an agent
session dies with that session, and its silence is indistinguishable from
"nothing has happened" — one such watch here went unread for forty hours. A
file is read by whoever comes next; an intention is not.

The tool's own first version had the bug it exists to catch: `os.kill(pid, 0)`
succeeds for a process that has exited and **not been reaped**, so a job that
died one second in was reported as alive. Both directions are now in CI.

---

## One command that runs all of them

```console
$ groundwork check
  n/a   gate          no PROJECT.md, so no recorded gate
  ok    prereg        2 sealed pre-registration(s), every required section filled
  ok    prereg-order  2 entered the record before the results they govern
  FAIL  noise         results are being compared with no measured noise floor
                      -> groundwork noise --n 10 --command '<your scorer>'
  waiv  raw-data      the generations are the artefact here; they are 3 MB and versioned
  ok    private       61 tracked file(s) scanned, nothing private found

  3 ok, 1 failed, 1 not applicable, 1 waived
```

Three decisions make this more than a checklist.

**`n/a` is printed as loudly as `FAIL`, and it is not a pass.** A sweep over a
project with no pre-registration must not show a green tick: a check that
passed because there was *nothing to check* has told you the opposite of the
truth. Most sweeps of this kind are mostly `n/a` on a young project, and that
is the reading.

**A waiver names its check and carries a reason, and the reason is reprinted
every time.** A flat exemption list is how a repository disarms itself — an
entry written for one document silently exempted a deliberately broken second
one here, and the CI step whose job was to fail started passing. A waiver in
`archive/waivers.json` with an empty reason does not waive anything.

**It scans what git would carry, not what git already carries**, and it says
what it scanned against. A scan restricted to tracked files passes right up to
the moment you `git add`, which is the moment it exists for; ignored files stay
out, because a scan that shouted about a 30 GB generations file would be turned
off. What counts as private is partly project-specific — a cluster's node
names, an internal ticket prefix — so a project declares its own patterns in
`archive/private-patterns.json`, and every clean result names how many patterns
it applied rather than just saying nothing was found.

**It refuses to accuse.** A pre-registration written to another template is
reported as *not judged by name*, not as incomplete — deciding whether prose
answers a question is not something a name match can do, and a sweep that
guesses generates false accusations against documents that do answer it. The
checks that stay are the ones that can be decided mechanically: is there a
seal; did version control see the plan first; is the noise floor on disk; is a
home path about to be pushed.

Two of those were found by running the sweep against this author's own
repositories. `prereg verify` had been asking when a pre-registration was
*last* committed, so redacting a machine name from a sealed plan moved it
forward past its own results and the tool called a correctly pre-registered
study a write-up. And a `sha256` appearing inside a document was being taken as
its seal — impossible, since a file cannot contain its own digest; the digest
in that document belonged to the plan it amended.

---

## The night

Every toolkit in this space has an overnight loop, and the thing they all
optimise is *not stopping*. That is backwards. A night is expensive because of
what it commits you to in the morning, not because of the GPU hours: an arm
that ran all night on a wrong flag produces a table, and the table gets
believed.

```console
$ groundwork night run docs/night-plan.txt --name fullset

[prereg] groundwork prereg verify prereg/PREREG_fullset.md --results results/
  rc=0  0.0 min

[capacity] groundwork cluster survey --nodes gpu01 gpu02 --need-gb 20
  rc=1  0.2 min
  | 0 idle card(s) across 2 reachable node(s).

The night stopped at [capacity]. That is the tool working: the step exited
non-zero and nothing downstream ran on top of it.
```

`night` runs a plan in order and **the first step that exits non-zero ends
it**. Every tool here is built to exit non-zero at the right moment — `gate` on
a direction with no headroom, `prereg verify` on a plan younger than its
results, `shard merge` on a hole or a disagreement, `noise` on a scorer that
fails, `check` on a gate with nothing behind it — and `night` is what makes
those exits matter while you are asleep.

What you read in the morning is a report that says where it stopped, the lines
from the log that say why, **which steps therefore never ran**, and the one
command that continues after you have fixed it. The steps that did not run are
the point: they are what the morning is still free to reconsider.

A worked plan is in [`docs/night-plan.txt`](docs/night-plan.txt) — the full-set
arms of a benchmark reproduction, gate chain and all.

And when every step passes, the report says so in the only way that is true:
*the commands succeeded, which is not the same as the result being right.*

To be told rather than to remember, `--notify` takes a shell command:

```bash
groundwork night run plan.txt --notify 'curl -sf -X POST "$WEBHOOK" -d "$GROUNDWORK_SUMMARY"'
```

No messaging vendor is built in — a webhook is a `curl`, a message is a
`mail`, a desktop bell is a `notify-send`, and a tool that ships one
integration ships a token to store and a vendor to follow. The command is
handed the verdict in its environment, **and its exit code is reported**: a
notification that fails silently is worse than none, because you are then
waiting for a message that is not coming, and the file that would have told you
is the one you have stopped checking.

---

## The claim stage: three layers, blind to different things

| layer | finds | cannot see |
|---|---|---|
| re-derivation | a number that exists in no file; a bound stated tighter than the interval | a **correct number inside a sentence that does not follow from it** |
| a reader with no context | claims that do not follow; a comparison pointing the wrong way | a fabricated number that looks plausible |
| the rendered figure | labels that read as one word; a caption unreadable at the size it will be seen | whether the shape a reader takes from the figure is the shape the data supports |

Implemented in [**doubleblind**](https://github.com/GuoCheng24/doubleblind),
installable on its own. Its ledger records 22 real defects with the layer that
missed each one; 10 were caught by a person looking at the rendered artifact,
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
| [taichu-eval-reproduction](https://github.com/GuoCheng24/taichu-eval-reproduction) | a reproduction whose verdict turns on **16 truncated generations** — the card's number is inside the interval under one scoring and outside it under the other, measured on all 1,000 items rather than argued from a subsample, and the page says so |
| [doubleblind](https://github.com/GuoCheng24/doubleblind) | the three claim layers, each with a test asserting the defect it *cannot* catch |

---

## Using it with your agent

The stages are plain Markdown under [`skills/`](groundwork/skills/) — no framework, no MCP
server, no second subscription.

- **Claude Code** — `ln -s .../groundwork/skills/* .claude/skills/`, then ask
  for a stage by name.
- **Codex CLI** — `codex exec < groundwork/skills/00-gate/SKILL.md` for a fresh session.
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
| **checking a training run** | `training-check` | narrower and measured: one file on RL post-training, where the importance ratio leaves `[0.9, 1.1]` for 1.8–60.0% of tokens **with the policy unchanged**, flips the PPO clip decision for 1.68–10.11%, and — across six GRPO arms, two seeds, 150 steps — does **not** reach the reward. Both halves, because the first half alone sells a week of fp32 plumbing |
| **launching a long run and being sure it started** | `run-experiment`, `monitor-experiment`, an experiment queue | **yes**, and the check is the point: ninety seconds before believing it, the log head read back, an empty head called buffering rather than silence, and a flag file that outlives the session so the watch is not an intention |
| **finding out what the machine can actually do** | — | **yes** — including what is installed but not on `PATH`, the module catalogue, whether isolation without root is available, and which large mounts it did *not* search |
| **running every gate at once, over a project** | `meta-optimize` over an event log | **yes**, `check` — and it reports `n/a` as loudly as `FAIL`, because a sweep that passes for want of anything to check has told you the opposite of the truth |
| verification layers **blind to different defects**, each with a test asserting what it cannot catch | an LLM review gate with an un-forgeable reviewer-identity chain | **three layers**, no MCP required |
| literature **ingestion** (OpenAlex, Crossref, arXiv, Semantic Scholar) | **yes, several skills** | **yes**, one tool — re-ranked, and it **refuses an occupancy verdict when the primary index is silent**, because a spent quota and an empty literature look identical |
| a **record that compounds** — what died, what got through, what converted into a check | `meta-optimize` reads an event log | **yes**, `ledger`, with a closed taxonomy so the causes can be counted |
| paper compilation and reference style | **yes** | **yes**, and two files deeper: the failures that *compile cleanly* — a centred over-wide table that never warns, a font declaration that never reaches the preamble, a bibliography hyphen that is not a hyphen |
| **producing the Word copy** — where a starred table vanishes without a trace, and why extracting the XML text cannot see it | — | **yes** |
| Overleaf **sync** specifically | **yes** | no — the editor's API is not covered; the LaTeX and Word production path is, in much more depth |
| **renting GPUs** — vast.ai, Modal, a serverless backend | **yes** | no, and deliberately: this has never been run here, and a file written from a vendor's documentation would be the one file in this repository not backed by something that happened. `cluster` assumes you can ssh to a GPU; if you cannot, ARIS covers that and this does not |
| **installable as a plugin** | yes | **yes**, and from one source: the Claude Code and Codex manifests point at the *same* seven stage files, so there is no mirror to fall behind |
| **being told when it ends** | `feishu-notify` | `night --notify` takes any shell command — a webhook is a `curl` — and **reports the notification's own exit code**, because a message that failed silently leaves you waiting for one that is not coming |
| **submission portals** — the field that picks your reviewers, eligibility rules, what anonymity actually leaks | — | **yes** |
| slides, posters, talks | **yes** | **yes**, two files: the talk, and the production discipline — a deck was 17 pages in one renderer and 11 in another, and the converter is usually installed but not where a plain lookup finds it |
| theory track | `proof-orchestrator`, `proof-writer` | **yes**, one file: attack a *stated* open problem, and the three ways a result turns out to be known |
| grant proposals | **yes** | **yes** — the gate applied before the proposal, "why you" as a checkable question, and the preliminary result that was designed to be reportable either way |
| **handing a manuscript to a human collaborator** — tracked-change formatting regressions, orphaned equation objects, reference-manager fields, metadata that leaks through the explanation document | — | **yes**, from a manuscript delivered round after round and found unclean each time |
| **caption audit** — panel letters, a stated direction that is backwards, a colour encoding that contradicts the discussion | — | **yes** |

| patents | five skills | **two**, from a live prosecution: the four orderings that cannot be undone, and the disclosure document an attorney actually drafts from |

**If you already use ARIS, the useful move is not to switch.** Run
`groundwork gate` before its pipeline starts, and the `30-claim` layers before
anything leaves. Those are the two places it has nothing, and they are the two
places the expensive mistakes are.

## Licence

MIT.
