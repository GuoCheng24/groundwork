# The invention disclosure — the document the attorney actually drafts from

Before there is a patent application there is a disclosure: the document you
write and the attorney turns into claims. Its quality decides the application's
quality, and **an error in it propagates into the claims where it is expensive**
— one such error, a reversed condition, originated in a disclosure and reached a
filed draft.

## Write it to the office's own template, section for section

Whatever form your attorney or office uses, follow it **completely**. The
sections exist because each is a question the drafter needs answered, and a
missing one comes back as a round trip. A typical structure, which is worth
matching even where no template is imposed:

1. **Front matter** — case name, contacts, the type of protection sought.
2. **Existing technology and its problems** — the field, the background, the
   specific problems, numbered, and the technical problem this solves. Numbered,
   because the claims will map onto them.
3. **Core idea** — the overall approach, the key steps, and the advantages.
   Short. This is what a drafter reads first.
4. **The detailed technical scheme** — the long section, and the one that
   determines what can be claimed. Step by step, with a figure per mechanism,
   and **after every formula, a paragraph defining each symbol**. A drafter who
   cannot resolve a symbol will either guess or ask.
5. **Technical effects** — numbered, each tied to a step above.
6. **Alternatives and variants** — this is the raw material for dependent
   claims, and it is the section people skip. Anything you might want to claim
   later must be described **now**; support cannot be added after filing.
7. **Terminology** and **references**.

The figures file is usually plain: figure number, a one-line description, the
image, then tables the same way. No document title, no commentary.

## The four ordering constraints, none of which can be undone

1. **Publication is prior art against your own later filing** in most
   jurisdictions. A paper, a preprint, a talk or a public repository describing
   the invention starts a clock or closes a door. **Decide once, early,
   explicitly** — by the time anyone notices it is a decision, it has been made
   by default.
2. **Claims can only be broadened before filing.** Section 6 above is therefore
   not optional.
3. **Every claim needs support in the specification.** A claim with no basis is
   not a narrow claim, it is an invalid one. Read the specification against
   every claim before filing, not after.
4. **Weighted, thresholded or parameterised limitations must match the
   specification exactly.** A weight that appears only in a claim is
   unsupported; a threshold that differs between the two is worse than either.

## Novelty here is a different search

Patent novelty is assessed against a different corpus and a different standard
from academic novelty. A mechanism can be entirely unpublished in the literature
and squarely inside an existing patent family. **Search the patent corpus
separately**, and never let an academic occupancy result stand in for it. See
[`../10-direction/occupancy.md`](../10-direction/occupancy.md) for the search
discipline, and apply it to a corpus that indexes claims rather than abstracts.

## Audit the disclosure like a manuscript

It is a technical document making claims, so the three layers apply
([`../30-claim/SKILL.md`](../30-claim/SKILL.md)): every number traceable, a
reader with no context asked what the evidence supports, and the figures audited
as rendered. The failure that matters most here is the ordinary one — **a
correct number inside a statement that does not follow** — because in a claim it
becomes a limitation that does not do what you think.

## Producing the document

- **Convert from a plain-text source**, so the content is diffable and the
  document is rebuildable. See
  [`../40-write/docx-from-latex.md`](../40-write/docx-from-latex.md).
- **Do not post-process the document XML** for a file containing equations
  unless you register every namespace — the failure is that equations render in
  the author's word processor and vanish in a strict viewer, which may be the
  office's.
- **Set the theme fonts for the script you are writing in.** A document whose
  headings fall back to a different family from its body reads as unfinished,
  and the cause is an empty theme font rather than anything in the text.
- **Render and read every page** before sending. See
  [`../50-submit/delivery.md`](delivery.md).

## What an agent should not decide

What to claim, when to file, where to file. Those are legal decisions with
deadlines that cannot be re-run. Surface them to a person with the constraint
stated plainly, and note that the publication decision in point 1 above is the
one most often made by accident.
