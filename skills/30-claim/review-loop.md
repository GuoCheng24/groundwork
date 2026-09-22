# The review loop — and the two ways it degenerates

Reviewing, fixing and re-reviewing until a score clears a threshold is a good
loop. It has two degenerate attractors and both feel like progress.

## Degeneration 1: optimising the reviewer

A loop that terminates on a reviewer's score optimises the reviewer's score.
With the same model on both sides, and a fixed rubric, the fastest path to a
higher score is to write toward the rubric — and every round of that is a round
of real edits producing a real improvement in a number that means less each time.

Counters, all cheap:

- **the reviewer changes model between rounds**, or at least between the first
  and the last;
- **the reviewer never sees the previous review or the score**, so it cannot
  reward the edits that were made for it;
- **a fixed hold-out objection list** written before the loop starts: the
  concerns that must be addressed regardless of what any round says. If the
  score rises and the list is untouched, the loop is not working;
- **stop on the list, not on the score.**

## Degeneration 2: sliding from construction into auditing

The deeper one. Auditing has a guaranteed deliverable — point the machinery at
existing work and something comes out — and construction does not. So every time
an attempt is expensive, the rational move is to audit instead, and a loop left
to itself will drift there while remaining productive the entire way.

Roughly forty campaigns in one programme ended negative or became audits. The
fix is not discipline; it is
[`../00-gate/breakthrough.md`](../00-gate/breakthrough.md) — make attempts cheap
enough that construction stops being the risky option.

## What a round must contain

1. an objection, quoted, with the file and line it applies to;
2. what the evidence actually says;
3. **a command that settles it**. An objection with no command is an opinion;
   convert it or drop it, and record the dropped ones with the reason so the
   same objection is not re-litigated next round;
4. the fix, implemented, before the next review. Not promised.

## Budget rules that prevent the loop eating the night

- a hard round cap, and a stop when the objection list is clear;
- an estimated cost per suggested experiment, and a refusal above a threshold
  that flags it for a person instead;
- **prefer reframing to re-running.** When a weakness can be addressed by
  stating the claim correctly, that is not a lesser fix, it is usually the right
  one — the original sentence was overreaching.

## What must never be optimised away

Do not hide a weakness to raise a score. Practically: keep a list of every
limitation any round raised, including the ones addressed by reframing, and
require that list to appear in the manuscript. A limitations section that
shrinks across rounds is the signature of a loop that has started gaming itself.
