# Contributing

The most valuable contribution to this repository is **an entry that cost you
something**.

## Adding a cause of death

`archive/causes-of-death.json` is a closed taxonomy on purpose: a free-text
cause is one nobody can count, and the point of the file is that the same causes
keep recurring. If a direction of yours died in a way none of the ten covers,
that is a genuinely new entry and it is worth more than a feature.

An entry needs all of:

- **what happened** — the specific way it ended, stated as a pattern rather than
  as your project. The pattern is the part that transfers;
- **the cheap test** that would have ended it sooner;
- **the gate** it belongs to, naming a stage that exists under `skills/`;
- **the rule** in one sentence;
- **what it cost** when it was missed.

CI checks the shape and that the gate names a real stage.

## Adding or changing a check

Every gate has to be **seen refusing**, on an input built to trip it, and seen
**passing** on the boundary case that must still get through. A gate that
refuses everything is as useless as one that refuses nothing, and both look fine
until somebody depends on them.

So a pull request that adds a refusal adds two tests.

## Adding a skill

Skills here are written from failures, not from principles. A section that says
"be careful about X" is not useful; a section that says "X shipped, here is what
it looked like, here is the rule that catches it" is. If you cannot say what it
cost, it probably belongs in a comment rather than in `skills/`.

Every note in a stage directory must be linked from that stage's `SKILL.md` —
CI fails on an orphan, because a file nobody links to is a file nobody reads.

## What not to send

- Private data of any kind. Patterns transfer; cohorts, manuscripts under review
  and internal identifiers do not, and they must never enter a repository.
- Dependencies. The core is standard library only and that is a feature — it is
  what lets this run on a locked-down cluster where installing anything is a
  half-day. The figure layer in `doubleblind` is the one exception, and it is an
  optional extra.
- Counts for their own sake. Seventeen files that each carry a real failure are
  worth more than a hundred that restate the obvious, and the repository is
  explicitly not competing on that number.
