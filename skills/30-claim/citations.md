# Citations — the reference that resolves to nothing

An agent-written bibliography has a specific failure: entries that are
well-formed, plausibly titled, correctly formatted, and not real. They survive
every check a word processor performs.

## Verify every entry against an index, before submission

```bash
scholarcheck refs.bib          # or: proofground lit verify "<title>"
```

Three verdicts, and the middle one is the one that matters:

- **verified** — the identifier resolves to a record;
- **unchecked** — a source was unavailable. *This is not a verdict.* A batch of
  unchecked entries at once is a network diagnosis, not a literature one;
- **suspect** — it resolved nowhere reachable, and a human must look.

A tool that collapses "unchecked" into "suspect" will accuse real papers during
an outage, and one that collapses it into "verified" will pass fabrications.
Keep the three separate, and make the exit code distinguish them.

## The traps in checking existence

See [`../10-direction/occupancy.md`](../10-direction/occupancy.md) for the full
set; the two that bite at citation time:

- **asking a reader model about a page while telling it the title you expect**
  makes it confirm the title you expect. Ask neutrally: *does this page exist;
  if it is an error page, say so*;
- **"that identifier looks too recent to be real" is not a test.** It is
  relative to today's date and has produced false accusations against real
  papers.

## Cite what you read

An entry that resolves is still the wrong citation if it does not support the
sentence. The failure mode here is a real paper on an adjacent topic, retrieved
because the search matched its title, attached to a claim it never makes. When a
citation carries weight — a priority claim, a "this is already known", a
competitor comparison — **read the thing**, not the abstract.

## Style is a build artifact, not a manual task

Render the bibliography with the venue's official style file rather than
approximating it, and rebuild it on every build so the document and the style
cannot drift. See [`../40-write/build.md`](../40-write/build.md), which also
covers what a reference manager's live fields do to numbering when somebody
opens the document and clicks update.

## Numbers in citing sentences

"Smith et al. report 84.5%" is two claims: that the number is 84.5, and that
Smith et al. report it. The first is checkable mechanically against a committed
note; the second is not. Keep a file of quoted external numbers with their
source and page, and trace the manuscript against it like any other result file.
