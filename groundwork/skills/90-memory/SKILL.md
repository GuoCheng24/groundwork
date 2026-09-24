---
name: groundwork-memory
description: >
  The running record that makes the next project cheaper: a ledger of what was
  decided, an archive of what died and why, and an index small enough to be
  loaded. Triggers: "record this", "archive", "post-mortem", "what did we
  learn", "记下来", "归档", "复盘".
---

# Memory — the archive is the asset

Most research memory systems record what worked. The expensive knowledge is in
what did not, and *why*, because that is what stops the same good idea being
re-proposed by the same good taste four months later.

```bash
groundwork ledger kill   --id <slug> --cause <from the closed taxonomy> \
    --what "..." --settled-by "..." --reopen-if "..."
groundwork ledger defect --id <slug> --missed-by mechanical|reviewer|figure|both \
    --what "..." --why "..." --check "..."
groundwork ledger roll
```

## In Claude Code: one index, not two

Claude Code keeps its own auto memory: a `MEMORY.md` index, one line per
memory, and a topic file behind each line; the first 200 lines or 25 KB of the
index load into every session. Use that as the index described below rather
than keeping a second one. Two indexes drift, and only one of them is loaded.

What auto memory does not give you is structure. Keep the archive and the
ledger as the files below, and put one line in `MEMORY.md` pointing at each.

## Three files, three jobs

**`archive/`** — one entry per direction that died. Verdict, cause (from
`archive/causes-of-death.json`), the cheap test that settled it, and what it
cost. Before any new direction, this is read first. A NO-GO that was never
written down is a NO-GO you will pay for twice.

**The ledger** — one entry per defect that got through, with the layer that
missed it and why that layer could not have seen it. Each entry that converts
becomes a mechanical check; each entry that does not converts into a note about
where the mechanical layer stops. Both are worth having.

**The index** — one line per topic: where to look and one hook. Conclusions and
numbers live in the topic file, never in the index.

## The constraint nobody plans for

An index that is loaded automatically has a **hard size limit**, and what
exceeds it is dropped silently — not truncated visibly, dropped. So:

- one line per entry, and adding an entry means compressing an old one;
- iron rules at the top, where they survive truncation;
- check the size after every edit, because the failure mode is invisible.

## Writing an entry that is still useful in four months

- **Absolute dates.** "Last week" is unreadable later.
- **The verdict first**, then the reason, then where the detail lives.
- **The star marks the surprise** — the thing that was not obvious and cost
  something. Entries without one are usually restating the repository.
- **Link liberally.** A link to an entry that does not exist yet marks something
  worth writing, not an error.
- **Delete what turned out to be wrong.** A memory that is confidently wrong is
  more expensive than no memory, and correcting one is the highest-value edit
  available.

## What does not belong

Anything the repository already records: code structure, past fixes, commit
history. Anything that only matters to the conversation it happened in. And
anything private — cohort data, manuscripts under review, internal identifiers
— which never enters a repository at all.

## In this stage

- [`postmortems.md`](postmortems.md) — the eight failure families that repeat
- [`wiki.md`](wiki.md) — persistent memory that stays worth loading
