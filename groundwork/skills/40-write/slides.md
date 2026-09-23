# Slides and decks — you cannot tell what a slide looks like by reading its markup

A presentation file is a zip of markup. Reading it tells you what is in the
deck; it tells you almost nothing about what is **on the page**, and the gap
between those two is where every slide failure lives.

One document rendered as 17 pages in one engine and 11 in another. That
difference was found by somebody else.

## Render, then look

```bash
# convert every page to an image, then assert on the images
<office-suite> --headless --convert-to pdf deck.pptx
# page count, per-page overflow, empty pages, unrendered equations
```

Three assertions worth automating, because they are the failures that recur:

1. **page count** matches what you think you built;
2. **no page is empty** — a slide whose only content failed to convert looks
   like a deliberate section break;
3. **no content extends past the slide boundary** — measure the bounding box of
   every text frame and image against the page, the same way
   [`../40-write/latex.md`](latex.md) measures an over-wide table. An overflow
   does not raise anything.

Then page through the images. Rendering is cheap; being surprised in the room
is not.

## The converter is probably installed and probably not on the PATH

A plain lookup for the office suite's binary will often find nothing even where
the suite is installed, because it lives under an application directory rather
than in a standard location. **Concluding "we cannot render here" from a failed
lookup is a real error that has been made**, and it costs the entire verification
layer above.

Check the full path before deciding a capability does not exist. This is the
same family as a hidden directory a recursive glob does not descend into: the
tool reported nothing and nothing was the wrong answer.

## An approximate renderer is a fallback, not a check

Where no real converter exists, a script that lays out the shapes approximately
is better than nothing for catching *gross* problems — a missing block, a
runaway text frame. It is not a substitute: it will not show you font
substitution, line-break differences, or the equation that did not convert.

Say which one produced the images you looked at.

## Slides are visual

A slide that is a paragraph is a slide nobody reads while listening to you say
the same words. Per slide: **one figure, one chart, or one large number**, with
a sentence. If it needs a paragraph, it is two slides or it belongs in the
paper.

This is worth enforcing mechanically, because it erodes under time pressure:

- **word count per slide**, with a ceiling;
- **the fraction of the slide that is empty** — measure it. A deck where every
  slide is 85% full is a deck of paragraphs, and the number tells you before the
  audience does;
- **the smallest type size used**, against what the room needs.

## The room is harsher than a thumbnail

A figure audited at link-unfurl scale is being judged at about 30% of its drawn
size. The back of a lecture theatre is worse, and a projector's contrast is
worse again.

```bash
doubleblind render figures/slide_fig.py --scale 0.25
```

Fix the **type size**, not the amount of information — and if that makes the
slide unreadable, the slide had too much on it.

Light-on-dark and dark-on-light behave differently under projection. Whichever
you choose, check the contrast ratio rather than trusting a screen.

## Fonts, one more time

A font that lacks a glyph prints a replacement character, and a text frame that
cannot shrink truncates rather than overflowing. Both have shipped. Verify the
**rendered** deck character by character for any non-Latin text, not the source.

## Posters

Read from two distances: a title and one finding from three metres, the method
from one. Build it as two layers, then shrink the whole thing to thumbnail size
— if the finding is not legible there, nobody walking past the session will see
it.
