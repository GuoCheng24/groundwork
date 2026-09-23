# LaTeX — the failures that compile cleanly

A manuscript that builds without a warning can still be wrong on the page. Every
item here produced a clean log.

## The font is not what you wrote in the front matter

A `\setmainfont` declared in a document's YAML front matter may never reach the
preamble, depending on the converter and template. The build succeeds, no
warning appears, and the body text is the typesetter's default — which reads as
a preprint rather than a journal submission, and which a supervisor will notice
before you do.

**Diagnose by measurement, in three steps:**

1. `pdffonts` the built PDF and read the **body** object. Low object ids are
   body text; high ones are fonts embedded inside figures, and those *will* show
   the font you wanted and mislead you.
2. Export the intermediate `.tex` and grep for the font commands. Zero hits
   means the front matter never made it into the preamble.
3. Test the font command alone in a minimal document, to separate "the channel
   is broken" from "this machine does not have that font".

**The reliable channel is a separate preamble file included explicitly**, not
front matter. Put `fontspec`, the main font, unicode substitutions and every
package there, and include it from every build target so the main document and
the supplement cannot diverge.

## Characters the font cannot draw

A font may lack `→`, superscript minus, `⊥`, `⊂`, `≈`, and several Greek
letters. The result is a "could not represent" warning in a long log, and a gap
on the page.

And a subtler one: **bibliography exports often contain a Unicode hyphen
(U+2010) that is not an ASCII hyphen.** It looks identical in an editor, the
font has no glyph for it, and the PDF gets a blank where the hyphen should be —
which an automated character count will not flag, because nothing is wrong with
the text. Grep the bibliography for non-ASCII dashes before the final build.

## A centred over-wide table does not warn

This one is the reason to distrust a clean log. A wide table inside `\centering`
is treated as a **single box**, centred, overflowing equally on both sides — and
that does not trigger the line-level overfull warning. The log is clean across
every build while the table visibly overhangs the text block on the page.

Four tables in one submission were over the text width, by up to 63 points, with
zero warnings in every compile.

**Detect it by measuring**, not by grepping the log:

```latex
\newsavebox\tb\sbox\tb{<the tabular>}
\ifdim\wd\tb>\textwidth \typeout{OVERWIDE: \the\wd\tb\space vs \the\textwidth}\fi
```

Or render and look. **Fixes:** bind long-text tables to `tabularx` with an `X`
column so they wrap; for numeric tables, `\small` plus a smaller `\tabcolsep`
usually recovers the width. A full-width `\includegraphics` cannot overflow;
display equations *do* warn, so the log is trustworthy for those.

## Exact journal citation style without hunting for a style file

Rather than installing a bibliography processor or finding a `.bst` for each
venue: render the bibliography with a converter using the venue's **official
CSL style**, extract the formatted entries, and inject them as a literal
`thebibliography` keeping the original keys. Citations still resolve and
renumber, and the PDF, the Word copy and the journal's own style agree
**exactly** rather than approximately.

Journal name abbreviations are part of the style for many venues, and a
bibliography of full journal names will be sent back.

## Never run a global regular expression over a manuscript

In a basic regular-expression dialect, `\|` is **alternation, not a literal
pipe**. One such command intended to change an axis label collapsed into a
pattern matching the empty string, and rewrote 939 places across 262 of 562
lines — every capital letter of one kind, every slash, every dollar sign, every
closing parenthesis.

It was recovered only because the transformation was fully known, by inverting
it in a script and then reading all eight pages by eye. The clean PDF had
already been overwritten.

**Rules:** use exact-match editing for manuscript changes; if a scripted
substitution is unavoidable, copy the file first and preview the match set
before writing; and after any such change, compile **and read the pages**.

## Verify the built artifact, not the source

Numbers, figure counts, page counts and fonts are properties of the output. A
source that looks like ten pages builds to eleven, and a converter version
change alone has moved a page count with no warning. See
[`build.md`](build.md) and [`../50-submit/compliance.md`](../50-submit/compliance.md).
