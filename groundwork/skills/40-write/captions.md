# Captions — the audit nobody runs

A figure caption is prose that nobody proofreads, attached to an image nobody
re-derives. One pass over a finished manuscript's captions found eight defects,
none of which any numerical check could reach.

## Check the panel, not just the figure

The text referred to **Figure 4D** and **Figure 4E**. 4D existed and did not
show what the sentence claimed; **4E did not exist at all** — a dead reference
left by an earlier version of the figure. Every percentage in those sentences
recomputed correctly.

A cross-reference check that matches figure *numbers* passes this. Match the
**panel letter** too.

## A caption can state the direction backwards

One caption named two arms in the wrong order, and its stated colour encoding
was wrong in a way that **contradicted the discussion section**: the colours
encoded a stratum, not the direction of the estimate. Both the caption and the
discussion were confident.

- restate, in the caption, what each colour and each line *is*, and check that
  claim against the plotting code;
- check the caption against the sentence in the body that interprets the figure.
  When they disagree, one of them is wrong and it is not always the caption.

## A caption must describe every panel

Four supplementary figures had two, four, six and three panels and a single
title each. A multi-panel figure with one line of caption is a figure whose
panels are undocumented.

## Say how the thing in the figure was constructed

A stratified plot's cut points were never stated; they came from a proportion
taken elsewhere in the analysis. A smoothing or trimming choice made in the code
— stabilised weights, 1st/99th percentile truncation — appeared in no caption
and in no methods sentence.

If a reader cannot reconstruct the figure from the caption and the methods, the
caption is incomplete regardless of how the figure looks.

## Residue

Highlight colours, comment anchors and revision marks survive inside caption
text and print. Strip them as a formatting change so the tracked history stays
honest, rather than by retyping the caption.

## Two blind spots in the checks themselves

- **Text-versus-text collision detection cannot see text lying on a drawn
  line.** A long label sitting across a confidence interval passed every
  collision test. `doubleblind render` checks lines as artwork for this reason.
- **A font that lacks a glyph prints a replacement character**, and a table
  column that cannot wrap **truncates** rather than overflowing — in one
  build, a long non-Latin phrase was silently cut to its first character. Verify
  the built output character by character, not the source.
