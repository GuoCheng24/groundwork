# Data hygiene — the preprocessing that silently happens twice

Two failure shapes, both of which produce numbers that look fine.

## Normalised twice

A public dataset shipped with its matrix **already log-normalised**, and the raw
counts kept in a separate layer. Five of six scripts in one project normalised
it again on load, because that is what the standard recipe does.

**Two conclusions of that project changed** when it was fixed.

The rule: before the first analysis, open the object and establish, in writing,
**what state each field is already in** — normalised or raw, log or linear,
per-sample or global, already filtered or not. Put that in the project notes,
not in your head, because the second script will be written by somebody who did
not read the first.

And when a dataset ships both, name the layer explicitly at every read. A
default that picks "the main matrix" is a default that changes meaning between
datasets.

## The view that is not a copy

Array slicing in the usual numerical libraries returns a **view**. Writing to it
mutates the original. A normalisation applied to a slice, in a loop, over
successive folds, silently corrupts the data for every fold after the first, and
the result is a plausible number rather than an error.

`.copy()` at the point of slicing, always, unless you specifically want the
aliasing. The cost is memory you can afford; the alternative is a result you
cannot explain six weeks later.

## Fields that look usable and are not

Check, before building features on them:

- **physical units** — a scan collection may carry intensity values in units
  that differ per site, making every absolute-value feature meaningless across
  sites even though they compute fine;
- **spacing and geometry** — if voxel spacing is unreliable, every distance,
  area and volume feature is unreliable with it;
- **batch structure** — if site or scanner predicts the outcome, a model will
  learn it, and cross-validation that splits randomly will reward it.

One collection failed all three: units and spacing both unusable, and batch
confounding at 95.8%. Everything downstream of those three checks was work that
did not need doing.

## Where the copy lives

A shared filesystem copy of a dataset is **not** a superset of your home copy,
and neither is a backup. Before deleting anything, push the authoritative
version somewhere durable and verify it arrived — checksum, not listing.

## The cheap discipline

Numbers go to disk before sentences are written about them, and a preprocessing
step goes into a function with a test before it goes into five scripts.
