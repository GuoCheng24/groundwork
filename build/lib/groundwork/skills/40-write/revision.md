# Revision — auditing a manuscript, including somebody else's

Different from writing your own paper and different from reviewing for a venue.
You are trying to find everything wrong with a document whose author will read
your list, and who has to remain able to act on it.

## Triage, in three bands, and the top band is small

- **BLOCKER** — the result as stated is not supported. Publishing it would
  require a correction. There are usually between zero and five of these and
  they are the entire value of the exercise.
- **MAJOR** — a reviewer will raise it and the answer is not ready.
- **MINOR** — wording, consistency, formatting.

Deliver them in that order and say how many are in each band in the first line.
A list of ninety undifferentiated comments gets skimmed; *"five blockers,
listed first"* gets read.

### What a blocker actually looks like

From one real four-round audit, the five that mattered were all of this shape:
**a number that is too good, produced by the pipeline rather than the world.**

The clearest: a perfect discrimination figure obtained by selecting features on
the whole dataset before splitting it. Redone with selection inside the fold,
the effect went to chance. Nothing in the manuscript was dishonest; the analysis
had simply been assembled in the order that felt natural.

So the first pass over any results section asks, of every headline number: *what
would produce this if the effect were not real?* See
[`../30-claim/integrity.md`](../30-claim/integrity.md).

## Rounds, and the reason a clean round is suspicious

Each round should find a class of thing the previous round could not see,
because it is looking differently — not harder. One manuscript went through
rounds that each declared it clean and were each disproved by the next, and the
pattern was always the same: **the round had used the same instrument as the
one before.**

A workable ladder, one instrument per round:

1. **the numbers**, recomputed from the data;
2. **the sentences around the numbers**, which is where a correct figure sits
   inside a claim that does not follow;
3. **the artifact as rendered** — figures, captions, cross-references, page
   count, the built PDF rather than the source;
4. **the machine-readable layer** — embedded objects, tracked-change state,
   metadata, reference fields, anything the text view does not show.

Round four is the one everybody skips and the one that found a deleted
sentence's equation object still welded to the following word, after **ten
rounds of text checking that all read only the text nodes**.

## Reading somebody else's manuscript

- **Separate "this is wrong" from "I would say it differently".** Put the second
  kind in a clearly labelled section, or leave it out. An author who finds three
  style preferences before the first real defect stops reading carefully.
- **Do not rewrite their voice.** You are auditing the argument, not adopting
  the paper.
- **Quote what you are objecting to.** A paraphrase lets the author answer a
  different sentence, and they will.
- **Give the command.** "Table 3's percentages do not sum" is an assertion;
  "`python check.py --table 3` reports 99.4" is a finding. An objection with no
  command is an opinion — drop it or convert it.
- **Say when you are unsure.** A list with confidence attached is usable; a list
  of equally confident items where two turn out to be wrong loses the other
  eighty-eight.

## Delivering the revision

The handover is its own failure surface — tracked changes that inherit
formatting, equation objects left behind, live reference fields, metadata, and
private values leaking through the very document that explains what was
scrubbed. All of it is in
[`../50-submit/delivery.md`](../50-submit/delivery.md), and it is the part that
turned "scientifically finished" into three more rounds.

Two rules specific to a collaborator's document:

- **decide "keep the reference fields" or "remove them" and do only one.** A
  document with renumbered citations in plain text and the original fields still
  live reverts the moment they press update;
- **nothing about your process goes in their package** — no script names, no
  check counts, no question you were asked rephrased as a question they asked.
  Keep internal versions in a directory whose name says so.

## The change ledger

Baseline paragraphs against current paragraphs through a sequence matcher,
printing the full text of every removed and added block. It is the only form
that reliably surfaces a wording change nobody intended, and it is what makes a
fourth round possible at all. Everything else summarises, and a summary cannot
show you the thing you did not know to look for.
