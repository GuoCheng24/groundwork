# Talks, slides and posters — and why you must render them

## The talk is not the paper compressed

One claim, the evidence for it, and the question you would most want to be
asked. A talk that covers everything in the paper conveys nothing; a talk that
covers one thing well gets you the conversation afterwards, which is the point.

## Slides are visual, not text

A slide that is a paragraph is a slide nobody reads while listening to you say
the same words. Per slide: one figure, one chart, or one large number, with a
sentence. If a slide needs a paragraph, it is two slides or it is the paper.

## Render before you believe anything about layout

**You cannot tell what a slide looks like by reading its markup.** Convert the
deck to images and look at every page. The one time this was skipped, a document
was 17 pages in one renderer and 11 in another, and the difference was discovered
by somebody else.

```bash
# convert to images and check page count, overflow, empty pages, broken equations
python3 officeview.py deck.pptx
```

Two specifics that cost time:

- **the converter may not be on the PATH.** Concluding it is unavailable because
  a plain lookup fails is a real error that has been made; check the full path
  before deciding a capability does not exist;
- **a preview renderer lies in both directions** — it invents ugliness that the
  real viewer does not show, and it hides structural defects that make figures
  and equations disappear in the real one. Use it to confirm content is present;
  confirm structure in the target viewer.

## The projected slide is harsher than a thumbnail

A figure audited at link-unfurl scale is being judged at roughly 30% of its
drawn size. The back of a lecture theatre is worse. Re-audit every figure for
the room:

```bash
doubleblind render figures/slide_fig.py --scale 0.25
```

Fix the type size, not the amount of information. A slide that needs eight-point
labels has too much on it.

## Posters

A poster is read from two distances: a title and one finding from three metres,
the method from one. Build it as two layers and check the three-metre layer by
shrinking the whole thing to thumbnail size — if the finding is not legible
there, nobody at the session will see it.

## Fonts, again

A font that lacks a glyph prints a replacement character, and a cell that cannot
wrap truncates rather than overflowing. Both have shipped. Verify the built
artifact character by character.
