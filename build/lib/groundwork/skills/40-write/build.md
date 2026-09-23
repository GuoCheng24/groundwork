# Build — one authoritative source, and a preview you must not trust

Producing a PDF and an editable document from one manuscript is where days
disappear. The strategy below was arrived at by losing several.

## LaTeX is the source. The word-processor file is a copy.

Typeset from `.tex`. Compact tables, automatic figure numbering, centring, real
serif type and correct mathematics are native there and cost nothing. The
converted word-processor route — convert, open in a preview, hand-fix column
widths, fonts, centring and numbering — is a downgrade you pay for every
revision, because the preview renderer, the real word processor and the
typesetter never agree.

Revise the `.tex`. It drives both outputs.

**Produce the word-processor copy anyway** — collaborators track changes in it,
some funders and some journals require it — but produce it *from the same
source* and stop polishing it.

## The preview lies in both directions

This is the part that wastes the most time, because it is not obvious that a
preview can be wrong.

- **It invents ugliness.** Substituted fonts and clumsy table rendering in a
  free previewer usually look correct in the real word processor. Do not hand-fix
  cosmetic problems you have only seen in a preview.
- **It hides real defects.** A namespace-prefix problem that makes figures and
  equations **disappear** in the real word processor and in its web viewer
  renders fine in the previewer.

**Net rule:** use the preview to check that content is *present*; check anything
structural — figures, equations, captions, numbering — in the real target
viewer. A document that rendered 17 pages in one and 11 in the other is the
reason this rule exists.

## Citation style, exactly rather than approximately

Rather than hunting for a bibliography style file for each venue: render the
bibliography with a converter using the venue's **official CSL style**, extract
the formatted entries, and inject them as a literal bibliography with the
original keys. Citations still resolve and renumber, and the PDF, the
word-processor copy and the journal's own style agree exactly instead of
approximately.

## Three silent variables

1. **The converter's version.** The same document built with two versions of the
   same converter produced different citation formatting and a different page
   count, with no warning. Pin it and record it.
2. **Reference-manager fields.** They are live. Updating them once, late,
   silently renumbered every citation in the document. Convert to static text
   before the final build.
3. **Font coverage.** A character the chosen font cannot draw becomes an empty
   box, and in a language the template was not designed for it can overflow and
   truncate a whole block. Check coverage, do not assume it.

## Before it goes out

Re-extract the numbers from the **built artifact**, not the source, and match
them against the current results — anchored so a figure cannot match inside a
longer one. A built file that quotes numbers its own data has since replaced
passes every check that only reads the source.
