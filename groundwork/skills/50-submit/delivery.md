# Delivery — handing a manuscript to a human who will open it in Word

The stage nobody writes about, and the one where a paper that is scientifically
finished stops being deliverable. Everything here was found *after* a round that
had been declared clean.

## Tracked changes inherit formatting you did not choose

A programmatic replace inside a tracked-changes document creates a new run that
inherits the run properties of the first run it replaced. Observed, across one
manuscript set: **P values silently lost their italics**, **seven caption
paragraphs turned entirely bold** because the bold title run was first, and
**whole lines of a title page became superscript** because a numbered run led
the span.

None of it is visible in the text. All of it is visible to an editor.

- cut runs at the **accepted-state character span** and set properties on that
  span, rather than replacing whole runs;
- after any change, assert that the accepted-state and rejected-state text of
  every paragraph is unchanged;
- **any sentence that went through a replace gets a formatting diff**, not just
  a text diff.

## Text checks read text. Equations are not text.

Deleting a sentence containing an equation left the equation object behind. The
accepted view rendered `Clinicopathological R²features` — the deleted sentence's
formula welded onto the next word. **Ten rounds of text checking missed it**,
because every one of them read only the text nodes.

Rule: any paragraph that changed, list **every** embedded object in it and its
deletion state. Wrapping the equation in the deletion element is schema-legal
and renders correctly.

## Reference-manager fields are live, and half-de-fielding is worse than either

A manuscript arrived with 18 citation fields and one bibliography field. The
renumbering and eleven new references had been inserted as **plain text** —
numbers outside the fields, entries inside the field result. One "update
citations" in the collaborator's reference manager would have produced old and
new numbers side by side and reverted the bibliography to its earlier length.

**Count the fields before touching references, and decide: keep them or remove
them.** You cannot do half. If you remove them, remove the field structure and
leave the text byte-identical, and say so at the top of the hand-off note.

## Privacy leaks travel through the explanation document

Document properties carried a personal email address, a machine username, a
device identifier with an account id, and a grammar tool's document id. All were
scrubbed.

**And they leaked back anyway** — into the note that explained what had been
scrubbed, which quoted the original values, and which shipped in the same
package. Checking the source files is not enough:

- scan **every** document inside the final archive, including archives inside it;
- two classes of check, with different scopes: private **values** across all
  content, metadata **field names** only where metadata lives — otherwise the
  explanatory document reports itself;
- the accepted verification is byte-level: every archive entry identical except
  the metadata files, the document body byte-identical, and the rendered output
  identical character by character.

## What does not go to the collaborator

- your instructions, your process, your script names, your count of checks;
- a question *you* were asked, rephrased as a question *they* asked — they will
  read it as their own and be confused;
- internal working versions. Keep them in a directory whose name says so.

## Two small traps that cost an afternoon each

- A bold-the-cross-references regex for `Figure \d` without a negative
  lookbehind also bolds the `Figure 2` inside `eFigure 2`. Five hits.
- Saving a document over its own path raises rather than overwriting. Write to a
  temporary name and move it.

## The form that actually catches things

A **change ledger**: baseline paragraphs against current paragraphs through a
sequence matcher, printing the full text of every removed and added block. Line
by line, it is the only form that reliably surfaces a wording change nobody
intended. Everything else summarises.

And a baseline used for a "reject all revisions and compare" check must itself
be rejected first — a baseline that carries its own tracked changes makes every
comparison report a difference.

## The four steps, fixed

1. read the change ledger end to end;
2. compare formatting run by run;
3. render and read every page, in two views;
4. run the check suite.

Each round that skipped one of these was declared clean and was not.
