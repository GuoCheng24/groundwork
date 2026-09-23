# Figures — the primitives are not the bottleneck

Publication-quality figures fail in a specific place, and it is not the drawing.

## Layout collision, not drawing quality

Once you have the primitives — panels, arrows, annotated axes, insets — the
thing that actually breaks a figure is **collision**: a label under artwork, two
annotations overlapping, a panel drifting out of its box, a title across a grid.
These are invisible in the script and obvious in the render.

**Detect them from real rendered bounding boxes, automatically.** A manual
register of "what is where" drifts from the figure the first time anyone edits
it; querying the renderer does not. `doubleblind render` does this, and its
rules exist because each one passed something:

- a title across a field of small tiles covered a few percent of its own
  bounding box — a threshold expressed as a *share* passed it twice, so the rule
  is any real overlap;
- column headers sat on a separator line, which is not a patch and so was in
  nobody's list;
- two labels three pixels apart do not overlap and read as one word;
- a character the font could not draw has a bounding box like any other glyph.

## Draw at the size it will be read

A figure drawn at full width is judged in a two-column layout, a thumbnail or a
projected slide. Text under about 10 px at the size it will be *seen* is texture.
Fix the type size, not the amount of information — a figure that needs eight-point
labels is a figure with too much in it.

## The failure no geometric rule can catch

A figure where every number is correct, nothing overlaps and the conclusion a
reader takes is the opposite of what the data says. Joining per-family points
with segments once made a shallower relationship look steeper: the within-group
slope a reader's eye follows was **30**, the pooled slope over the measured range
was **0.30**.

Guard against it by construction, not by inspection:

- fit lines over a **common range** rather than within groups;
- if groups are shown separately, show the pooled fit as well;
- put the comparison the claim makes in the figure, and nothing else.

Then look at the rendered image yourself and ask what it says, as though you did
not know the answer. That last step is not automatable and pretending otherwise
is how the inverted figure shipped.

## Build figures from data, every time

Generate from the committed result file in CI, and diff. A figure regenerated on
every build cannot silently describe a previous run; a figure checked in as a
binary and edited by hand will.
