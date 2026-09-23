# Occupancy — is it already done, and can you tell?

The gate that kills most candidates, and the one most likely to give a confident
wrong answer. Everything below is a failure mode that produced one.

## Search the mechanism, in the right words, at the right length

- **Feed focused keywords, not the claim sentence.** A whole sentence drags the
  search off into adjacent fields; three to five terms naming the *mechanism*
  find the neighbourhood.
- **Re-rank by word hits** (title weighted about 3×, abstract 1×). A broad
  index returns the right paper mixed with noise from other fields; without
  re-ranking the right paper is on page three and you conclude it does not
  exist.
- **Go back further than five years.** A qualitative mechanism was occupied by a
  2017 paper and its closed form by one from 2003. Recent-only search finds
  recent competitors, not prior art.
- **Search your own output first.** A "new paper" turned out to be a table in
  the group's own supplementary material.

## The training-cutoff trap

An agent surveying from its own weights is surveying the year its training
stopped. Always issue a *recency* query explicitly, and sort so that new work is
not buried by highly-cited old work. Anything time-varying — impact factors,
acceptance rates, deadlines, state of the art — is queried, never recalled.

Quoting a journal's impact factor from memory once mis-set a venue choice by a
factor of two. Citation-based proxies are **not** the official figure either:
one journal's proxy read 6.6 against an official 20.1. Report the source and the
caveat, or do not report the number.

## The three traps of existence verification

Before citing anything an automated search surfaced:

1. **An occupancy search can invent its neighbours.** A generated "closest
   competitor" with a plausible title, year and identifier can simply not exist.
   Every candidate that matters gets its existence checked separately.
2. **A verifier that fails on the network reports a hallucination.** When four
   backends all fail to resolve, the tool says "probably fabricated" — and a
   flaky tunnel makes it say that about real, well-known papers. *A whole batch
   failing at once is a network diagnosis, not a literature one.*
3. **Fetching the abstract page directly is the most reliable cross-check, and
   it has two failure modes of its own.** A leading prompt — one that states the
   title you expect — induces the reading model to confirm it, so the question
   must be neutral: *"does this page exist; if it is a 404, say so."* And a
   reading model with an earlier cutoff will call a genuinely recent paper
   hypothetical, so never ask whether a paper is "from the future".

**"That identifier looks too recent to be real" is not a test.** It is relative
to today's date, and it has produced false accusations against real papers.
Judge by multiple backends failing *while the network is healthy*, not by the
number.

## The closing rule

A verdict of "already occupied" requires reading the thing that occupies it. A
search result is a candidate; a PDF you have read is evidence. One tool's
"unresolved" is never enough to close the question in either direction.

## What to record

Either outcome goes into `archive/`. "Occupied, by this paper, which says this"
is worth as much as a green light and costs the next person nothing to re-check.
