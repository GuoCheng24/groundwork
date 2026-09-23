---
name: groundwork-experiment
description: >
  Run the experiment the way it can still be believed afterwards: pre-registered
  and sealed before generation, launched across whatever GPUs are actually idle,
  resume-safe, and analysed by the plan that was written first. Triggers: "run
  the experiment", "launch", "train", "evaluate", "预注册", "跑实验", "扫超参".
---

# Experiment — sealed first, then launched

## 1. Pre-register, seal, commit — in that order

```bash
groundwork prereg new prereg/PREREG_run3.md --title "run 3"
# fill every section, then
groundwork prereg seal prereg/PREREG_run3.md
git add prereg/ && git commit -m "Pre-register run 3"      # BEFORE any generation
```

Six sections are required because these are the six that get quietly dropped:
what is held fixed, what changes, the pre-stated analysis, **the stopping rule**,
**what gets written if it comes out the other way**, and **what was already known
when this was written**.

That last one is not a confession box. An arm launched after seeing a partial
score is not disqualified — an *undisclosed* one is. Say plainly what was known
and why the arm is being run, and the work survives a reader who notices.

Afterwards:

```bash
groundwork prereg verify prereg/PREREG_run3.md --results results/metrics_run3.json
```

which checks the seal, checks every section is filled, and checks with git that
the pre-registration was committed **before** the results it governs. A
pre-registration committed after its results is a write-up.

## 2. Find the capacity that is actually free

Start with the machine you are on, because what it can do is usually
underestimated:

```bash
groundwork probe            # GPUs, /dev/shm, what is installed off PATH, isolation
```

`which X` answers for `PATH`, not for the machine. LibreOffice was declared
unavailable here for weeks on that evidence while it sat eight directories deep
under a shared mount; `ninja` was missing from `PATH` while an inference stack's
JIT backend needed it. On a cluster, `module avail` is the real catalogue. And
"no root, so no containers" was false: unprivileged user namespaces, `bwrap`
and `fuse-overlayfs` were all available to an ordinary account.

Then look outward:

```bash
groundwork cluster survey --nodes gpu01 gpu02 gpu03 gpu04
groundwork cluster plan --nodes gpu01 gpu03 --need-gb 20 --shards 4 \
    --command 'python eval.py --data data/subset.jsonl'
```

Three habits, each learnt by losing a night:

- **Somebody else's job is not free memory.** A card with 19 GB in use and 5 GB
  free is not idle; a job placed there dies at 3 a.m. after the queue has moved.
- **Leave a card per node.** Shared clusters are social, and the idlest card is
  the one to leave, not the scraps.
- **One arm, one GPU model.** The same weights on two different cards do not
  always produce the same number — measured, not assumed. `plan` refuses to
  split an arm across models unless told the split is only a throughput knob.

## 3. Make the harness resume-safe before you need it

- append one record per item and **flush**, so a crash costs one item;
- skip items already present in the output, keyed by a stable id;
- when sharding, slice the item list **before** the already-done filter. Slicing
  the filtered list makes ownership depend on how far each shard has got, and
  two shards restarted at different points then take the same item while a third
  is taken by nobody — silently, because every shard file looks complete alone.

```bash
groundwork shard plan --items 2638 --shards 5      # sizes, and that line in place
groundwork shard merge 'out_s*.jsonl' --expect 2638
```

`merge` exits non-zero on two different answers for one id — naming the fields
that differ — and on a total short of what was expected, which is what a shard
that died leaves behind.

## 4. Launch it so that it outlives this session

```bash
groundwork watch start --name run3 -- python eval.py --shard 0/4
groundwork watch status                 # what happened, and write the flag file
```

`watch` launches detached, waits ninety seconds **before believing it started**
— a job that fails to load its weights looks exactly like one that is training,
at launch — then prints the head of the log where the configuration is echoed.
An empty head is reported as buffering, not as silence, because those two look
identical and only one of them loses everything in a crash.

When the run ends it writes `archive/runs/<name>.DONE` with the verdict. That
file is the point: a watch set up *inside* a session dies with the session, and
its silence is indistinguishable from "nothing has happened" — one went unread
for forty hours. A flag file is read by whoever comes next; an intention is not.

`status` greps the log for the things that end runs quietly (a traceback, an
OOM, a `Killed`, a NaN) and exits non-zero if it finds one, so it can sit in a
loop or a cron line.

## 5. Leave it running, and let it stop itself

```bash
groundwork night run night-plan.txt --name fullset
groundwork night report
```

A plan is one shell command per line, and **the first one that exits non-zero
ends the night**. That is the opposite of what an overnight loop usually
optimises, and it is the point: a night is expensive because of what it commits
you to in the morning. An arm that ran all night on a wrong flag produces a
table, and the table gets believed.

The morning report says where it stopped, the lines from the log that say why,
and **which steps therefore never ran** — which is what the morning is still
free to reconsider. There is a worked plan in `docs/night-plan.txt`.

## 6. Analyse the plan that was written first

Run the pre-stated analysis and report it whichever way it comes out. Then, and
only then, look at anything else — and label it exploratory.

**Measure the noise floor of your own scorer before quoting a difference.** An
official benchmark scorer, run ten times on one unchanged file, spanned 0.37
points and disagreed with itself on two prompts of 541. Three runs had said it
was stable. Any arm-to-arm difference smaller than that is not a finding about
the arms.

## In this stage

- [`long-runs.md`](long-runs.md) — the loop has to survive the session that started it
- [`hardware.md`](hardware.md) — the card is a variable, and it is worth 1.48 points
- [`shared-machine.md`](shared-machine.md) — sharing a cluster with people who are not you
- [`data-hygiene.md`](data-hygiene.md) — the preprocessing that silently happens twice
- [`ablations.md`](ablations.md) — the arm that is missing is usually the informative one
- [`implementation.md`](implementation.md) — making the thing you are testing actually be the thing
