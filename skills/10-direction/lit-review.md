# Reading the literature so that the survey is usable later

A survey that reads as a list of papers produces a related-work section. A
survey that produces a *direction* is organised differently from the start.

## Read for three things, in three separate files

- **claimed** — the headline result of each paper. This is the easy one and the
  only one most surveys record.
- **conceded** — the limitations section. This is where the gaps that are real
  *and already known to be real* live, and it is the part that gets skipped
  because it is at the end and sounds negative. A conceded limitation with no
  follow-up paper is the highest-yield lead available.
- **assumed** — what every paper in the area takes for granted without arguing
  for it. Hardest to see, worth the most: a shared assumption nobody defends is
  either correct and boring or wrong and a paper.

Keeping them in separate files matters. Merged into "notes", the third category
disappears, because it is the only one that requires reading across papers
rather than within them.

## Query discipline

- Focused keywords naming the **mechanism**, not the claim sentence. A sentence
  drags a search into adjacent fields.
- **Query for recency explicitly.** An agent surveying from its own weights
  surveys the year its training stopped, and relevance sorting favours
  highly-cited old work. `proofground lit latest` exists for this.
- Do not stop at the abstract for anything that could be the same idea in other
  words. Abstract-level matching finds a small fraction of what is there.
- Search **older** literature for mechanisms. A qualitative result occupied by a
  2017 paper had its closed form in one from 2003.

## What a finished survey contains

Not a summary. A table whose rows are candidate directions and whose columns
are the five things [`SKILL.md`](SKILL.md) requires — claim, baseline, oracle,
null, venue — with the papers that bear on each cell. Anything that cannot fill
a row is not yet a candidate, and saying so is the survey's main output.

## The self-check

When the survey is done, answer in one sentence: **what does everyone in this
area believe that might be wrong?** If the answer is "nothing", the survey was a
reading list. That is a fine thing to have produced and it is not a direction.

## What to record

The occupancy verdicts, either way, in `archive/` — with the paper that settled
each. "Occupied, by this, which says this" saves the next person the same
afternoon, and the next person is usually you.
