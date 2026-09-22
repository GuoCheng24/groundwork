# Compliance — the venue's hard specs, as a file that fails

A whole class of rejection that costs nothing to avoid and that nobody checks
until late. In one manuscript programme, journal hard specifications had **zero
automated checks until the ninth review round**.

## Make it executable

Write `check_venue_compliance.py` for the target venue and run it on every
build. It should fail, loudly, on:

- word and page counts, counted the way the venue counts them — which is often
  not the way your build counts them (abstract included or not, references
  included or not, figure captions included or not);
- reference count and style;
- figure count, panel count, resolution, colour mode, file format;
- structured-abstract headings, exactly as named;
- anonymisation: author names, affiliations, acknowledgements, funding,
  self-citations phrased as "our previous work", metadata in every file;
- the declarations the submission portal will demand — data availability, ethics,
  conflicts, contributions.

Each check hard-codes the number from the call and cites where it came from. A
spec read once and remembered is a spec that will be wrong by the next revision.

## Get the spec from the venue, and expect not to be able to

The authoritative source is the venue's own page, and that page may sit behind a
bot wall that returns a challenge rather than content to anything automated. One
journal's guidelines were reachable **only through an archived snapshot**.

So: fetch the page, and *check that what you got is content*:

```bash
proofground reach --targets <venue host>
```

A `CHALLENGE` tier means the status code was fine and the body is a bot wall.
Anything that reads only the status code will treat that as the author
guidelines and you will build against nothing.

## Count in the built artifact, not the source

Pages, words and figures are properties of the **output**. A source that looks
like ten pages can build to eleven, and a converter version change alone has
moved a page count with no warning. Count what the editor will count.

## The declarations are content, not paperwork

Data availability, author contributions, conflicts and ethics statements are
read, and inconsistencies between them and the paper are noticed. Two recurring
ones: a contributions section that contradicts the author order, and a data
availability statement promising what the ethics approval forbids.

If the manuscript already contains a contributions block in the venue's own
format, **do not add a second one** in a different format. Editors read both.

## Before the portal

Do a dry run of the submission form itself and write down every field it asks
for. Several of them — suggested reviewers, a significance statement, a
plain-language summary — are writing tasks that people discover at midnight on
the deadline.
