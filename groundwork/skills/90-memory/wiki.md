# The research wiki — persistent memory that stays worth loading

A memory that grows without bound stops being read. A memory that is curated by
hand stops being written. The structure below is what survived both failures.

## Three layers, and the size constraint that shapes them

**Index** — one line per topic: where to look, and one hook. Nothing else. It is
the layer that gets loaded automatically, and **it has a hard size limit beyond
which content is dropped silently** — not truncated visibly, dropped. So:

- one line per entry, and adding an entry means compressing an old one;
- iron rules at the top, where they survive truncation;
- **check the size after every edit**, because the failure mode is invisible. An
  index has exceeded its limit twice here, both times immediately after adding
  something important.

**Topics** — one file per project or theme, carrying the conclusions and the
numbers. Anything longer than a line belongs here, not in the index.

**Archive** — directions that died, with causes. Read before starting anything.
See [`SKILL.md`](SKILL.md).

## Writing an entry that is still useful in four months

- **absolute dates.** "Last week" is unreadable later, and an agent reading it
  later will compute the wrong thing from it;
- **the verdict first**, then the reason, then where the detail lives;
- **mark the surprise.** The thing that was not obvious and cost something. An
  entry without one is usually restating what the repository already says;
- **link liberally**, including to entries that do not exist yet — a dangling
  link marks something worth writing, not an error;
- **delete what turned out to be wrong.** A confidently wrong memory is more
  expensive than no memory. Correcting one is the highest-value edit available,
  and it happens least often because nothing prompts it.

## What does not belong

- what the repository already records: code structure, past fixes, commit
  history. If `git log` says it, the memory should not;
- anything that only mattered inside the conversation it happened in;
- **anything private** — cohort data, manuscripts under review, internal
  identifiers, paths that reveal a person or an institution. These never enter a
  repository and they leak most often through a file that explains what was
  removed. See [`../50-submit/delivery.md`](../50-submit/delivery.md).

## Failed ideas are the highest-value entries

They are also the ones nobody writes, because writing them feels like recording
a failure rather than a result. The test: **would this entry have stopped me?**
If yes, it is worth more than the successful entry next to it, and it is the one
thing an agent cannot regenerate from the code.
