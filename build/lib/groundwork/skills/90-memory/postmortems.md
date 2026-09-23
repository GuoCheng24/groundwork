# Post-mortems — the failures that repeat

A ledger of individual defects is useful. A ledger grouped into **families** is
what lets you catch the next one, because the next one will not look like any
entry you have but will belong to a family you have.

These are the recurring families from a few dozen recorded reasoning failures.
Each is stated as the shape of the mistake, not as the instance.

## 1. A pass rate read as a coverage rate

"96% of cases pass" answers a different question from "96% of the space is
covered". The first is about the tests you have; the second is about the ones
you do not. A high pass rate on a suite nobody stress-tested is evidence about
the suite.

## 2. One instance extrapolated

A mechanism confirmed on one dataset, one model or one seed, then written as a
property of the method. The tell is a sentence with no scope in it. Add the
scope and the sentence usually stops being interesting — which is the
information.

## 3. The check shares the author's blind spot

The person who wrote the artifact wrote the check, so the check tests what they
already thought of. Measured: a guard printed "every number is re-derived" while
passing a document with eight figures falsified into it, because it searched the
*document* for each computed number and a fabricated figure appears nowhere.

Guards need a second, differently-shaped layer. See `30-claim`.

## 4. Declared dead too shallowly

A direction abandoned on a surface reading — "this is occupied", "this cannot
work" — that a later look overturns. The discipline is symmetric with the gate:
a kill needs the same evidence as a go, and the cheap test that settled it goes
into `archive/` so the reversal is possible.

## 5. The correction is also wrong

Over-correction after being caught once. A subsample mean called biased when it
was unbiased; a bound loosened past what the data required. Corrections are
self-marked too, and they are harder to catch because they sound cautious.

## 6. A number that is right in a sentence that is not

The single most common defect that survives mechanical checking. The quantity
matches the file; the causal claim, the ranking or the framing around it does
not follow. Four of five findings from one zero-context review were this.

## 7. Verified in the wrong place

Reading a configuration file instead of the running process, an XML instead of
the rendering, a source instead of the built artifact. The rule: **verify where
the reader will be**, not where the data is.

## 8. A silent limit

A cap that drops rather than errors: a context or index that truncates, a
quota that starts returning empty, a cleanup that deletes by timestamp. The
failure looks like "nothing to report". Anything with a limit gets a check that
the limit has not been hit.

## How to use this file

When something goes wrong, name the family before fixing the instance. If it is
a new family, add it — and if the fix is mechanisable, the fix belongs in a
check, not in this file. A post-mortem that stays prose is worth one catch.
