# Implementation — making the thing you are testing actually be the thing

Between a method on paper and a number in a table there is code, and the code is
where claims quietly become about something else.

## Check that the component you are testing ever runs

One project's central contribution was an attention mechanism. Its sequence
length was **1**. The query–key–value computation had therefore never done
anything at all, across every experiment in the project, and every reported
number was about the rest of the architecture.

Nothing failed. The shapes were valid, the losses went down, the ablations
looked ordered.

**So: assert the thing exists at run time.** A component that is meant to mix
across positions asserts that there is more than one position; a component that
is meant to gate asserts that its gate takes more than one value; a loss term
that is meant to bind asserts that its gradient is non-zero. One assertion at
the top of the forward pass, permanently, not a debugging session.

## A/B against the genuinely original code

When fixing something, compare against the code as it was, not against your
memory of it. A behaviour matrix needs three kinds of row:

- **must block** — the broken input the fix exists for;
- **must pass** — the legitimate case that must not be caught;
- **unchanged** — the old behaviour that should be preserved exactly.

A surprise in the matrix means checking the test harness first and the fix
second. A harness that reports success on a deliberately broken input is a
harness reporting on itself.

## Commit the verified patch immediately

Work left in a working tree is destroyed by the next stash or checkout during
A/B testing. Commit to a branch the moment it verifies; a commit costs nothing
and re-deriving a lost fix costs an afternoon.

## Line endings and other people's files

Before editing a file you did not write, check its line endings and preserve
them byte for byte. A file rewritten from one convention to the other turns a
two-line diff into a three-hundred-line one that no maintainer will read, and
the change itself becomes invisible inside it.

## Never edit a manuscript or a source file in place with a stream editor

Two separate incidents, one of which destroyed a manuscript. Read, transform in
memory, write — and the guard belongs on the *action*, not on a judgement about
whether this particular file is important enough. Reclassifying the file as
"temporary" is how the second incident happened.
