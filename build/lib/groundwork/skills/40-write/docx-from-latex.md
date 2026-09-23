# Producing a Word copy — where whole tables disappear without a trace

Many venues and most collaborators need an editable document. Converting from a
typeset source is a well-trodden path with a specific, nasty property: **its
failures are silent and its obvious verification method is blind to the worst
of them.**

## What vanishes

Each of these produced a correct PDF and a Word file missing content, with no
error:

| construct | what is lost |
|---|---|
| a boxed minipage | the entire box contents |
| a table wrapped in a resize box | the **whole table** |
| a full-width starred figure | the caption |
| a full-width starred **table** | **the whole table, without a trace** |

The last one is the worst: three data rows and a header, gone, leaving nothing
behind to notice. The rule that covers all four: **downgrade every starred
float and remove every resize wrapper before converting**, and handle boxes by
mapping them to a construct the converter understands.

## The verification method that is structurally blind

The natural check — unzip the document, strip the tags, read the text — cannot
see a block that is **absent**. When a table vanishes there is no text to
extract. On the run that lost a main results table, four independent checks were
green: page count, file size, image count, and extracted XML text.

**The check that works is to render the converted document back to PDF and
assert on the rendering:**

1. **no unresolved references** — a search for a word followed by a question
   mark must return nothing;
2. **every figure and table number present**, counted, `Fig. 1 … Fig. N` and
   every table label;
3. **table data-row keywords present**, row by row, for each main table.

Then look at the pages. Structural absence is visible to a renderer and
invisible to a parser.

## The preview renderer lies in both directions

- **It invents ugliness.** Substituted fonts and clumsy table rendering in a
  free previewer usually look correct in the real word processor. Do not hand-fix
  cosmetic problems you have only seen in a preview.
- **It hides real defects.** See the next section — the most damaging bug in
  this list renders perfectly in the previewer.

Use the preview to confirm content is *present*; confirm structure in the real
target viewer.

## Namespace prefixes, and figures that disappear only for some readers

If you post-process the document XML with a library that registers **one**
namespace, re-serialising renames every *other* namespace to generated prefixes.
Drawings, relationships and equations end up under non-standard prefixes.

Real word processors resolve by URI and display fine. The preview renderer
displays fine. **A strict web viewer shows neither the figures nor the
equations** — and that is how a collaborator opens it.

Register **every** namespace declared on the document root before serialising.
This is the clearest case of "the preview was too forgiving to catch it".

## Style drift between the two engines

Expect and fix, because a reviewer reads both:

- **fonts and line spacing** — the converter uses its own template; supply a
  reference document with the body font, size, spacing and alignment set;
- **citation style** — the converter defaults to author–year; pass the venue's
  CSL or the two documents will use different systems;
- **table grids** — converted tables can arrive with no column widths and
  collapse in the word processor; inject an even grid and an autofit layout;
- **page breaks** — a `\clearpage` is not carried over, so a one-figure-per-page
  PDF becomes several figures crammed onto one page;
- **bibliography position** — the converter tends to place it last, which
  reverses the order if the PDF has figures at the end;
- **heading colour and numbering**, which the default template sets differently
  from the typeset source;
- **run-in subheadings**, which become standalone headings and acquire deep
  numbering.

## Non-Latin text

A missing East Asian theme font in the reference document makes headings fall
back to something different from the body, which reads as broken. Set both the
major and minor East Asian theme fonts, and set a user-level font alias so the
document can keep the font names a collaborator's word processor expects while
still rendering here.

## The rule underneath

**The typeset source is authoritative; the converted document is a copy.** Do
not spend afternoons beautifying a preview. Spend them on the four checks above,
which catch the failures that are actually silent.
