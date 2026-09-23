# Diagrams — the overview figure is buildable, and layout is the hard part

The figure that sells the paper is usually a *scientific illustration mixed with
data panels* rather than a plot: the pipeline overview, the architecture, the
study design. These are normally drawn in commercial illustration software.

## They can be built from a plotting library, and there are two bonuses

Rebuilt one such figure from a top-tier journal in three iterations using only a
standard plotting library. It reached the same class, and it gained two things
the original does not have: it is **vector and reproducible**, and it is **driven
by the data** — the panel that shows a cohort size shows the actual cohort size,
so it cannot drift from the study.

The primitives needed are a modest set: people, cells, sequences, tissue planes,
stacked projections, boxes, arrows, a sequence logo, a tilted card for a
projection. Build them once, reuse them forever.

## The lesson that matters: primitives are not the bottleneck

The first version had every primitive working and close to the original. What
broke was **layout**: the title covered by artwork, an icon over a label, a
large dead area in one quadrant. Every failure was a collision.

Three consequences:

1. **Detect collisions from real rendered bounding boxes, automatically.** A
   manual register of what is where drifts the first time anyone edits the
   figure; querying the renderer does not.
2. **Check text against artwork and against lines, not only against text.** A
   collision test that compares strings to strings passes a title lying across a
   tile grid and a label sitting on a confidence interval. Both shipped.
3. **Look at the rendered image.** No geometric rule knows whether the figure
   reads well; it only knows whether things overlap.

```bash
doubleblind render figures/overview.py --scale 0.3
```

## Font coverage is a real constraint

A serif font for a non-Latin script may lack `≤`, `≥`, `∩` and any symbol
emoji, and they print as replacement characters. A table column that cannot wrap
**truncates** rather than overflowing — one build silently cut a long phrase to
its first character.

So: substitute symbols before building, allow columns to wrap, and **verify the
built output character by character**, not the source.

## Flow diagrams

For anything that is boxes and arrows, a text-based diagram language checked into
the repository beats a drawing: it diffs, it regenerates, and it cannot drift
from the text that describes it. Keep the drawn illustration for the things that
genuinely need illustration.
