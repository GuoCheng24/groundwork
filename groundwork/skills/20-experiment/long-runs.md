# Long runs — the loop has to survive the session that started it

An overnight research loop is only autonomous if it outlives the thing that
launched it. Three layers fail independently and each has cost a night.

## The conversation survives; the watcher does not

An agent session that writes every step to disk loses nothing to a dropped
connection — reconnecting resumes it, and a killed process is replayed from the
transcript. What does **not** survive is anything scheduled *inside* the
session: a monitor, a timer, a "check back in an hour". Those live and die with
the session, and their silence is indistinguishable from "nothing has happened".

One watch set up this way went unread for forty hours.

**So**: anything that must still be watching tomorrow goes into the system
scheduler, writes a **flag file**, and the flag file is named in the project's
own notes as the first thing to check on resuming. The agent reads a file; it
does not remember an intention.

## Foreground work dies with the shell

Launch detached (`nohup`), then do three things that take ninety seconds and
save hours:

1. confirm the process is alive at ~90 s — not at launch, when everything looks
   fine, but after the model has had time to fail to load;
2. read the **head** of the log, where the configuration is echoed. A run with a
   wrong flag looks identical to a right one until it finishes;
3. check that output is actually appearing, not buffered. A harness that writes
   at the end is a harness that loses everything to a crash.

## Resume has to be designed, not hoped for

- append one record per item and **flush** — a crash then costs one item;
- skip items already present, keyed by a stable id, so re-launching is safe;
- when splitting across GPUs, slice the item list **before** filtering out
  what is done. Slicing afterwards makes ownership depend on progress, and two
  shards restarted at different points then take the same item while a third is
  taken by nobody — silently, because each shard file looks complete alone;
- when merging shards, fail on an id whose copies disagree, naming the field.
  That is a real problem, not a tidying job.

## Clocks

A machine whose clock jumps backwards can make a cleanup job delete files it
considers expired, including session transcripts. Anything precious is committed
to version control, not left in a working directory with a timestamp.

## What "finished" means

A run is finished when its output has been **scored** and the numbers are on
disk, not when the process exited. Write the sentences afterwards, and never in
the same step as producing the numbers.
