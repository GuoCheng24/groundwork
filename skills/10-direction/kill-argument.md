# Kill-argument — steelman it, then try to end it today

Before a direction is worked on, spend an hour trying to destroy it. Not to be
rigorous; because the destruction is cheap now and expensive later, and because
a direction that survives an honest attempt is one you can defend for a year.

## Steelman first, or you are killing a strawman

Write the **strongest** version of the idea: the most favourable setting, the
most generous assumptions, the best-case result. If the strongest version is not
interesting, stop — no amount of work improves it, and this takes ten minutes.

## Then the five kills, cheapest first

1. **It is occupied.** Search the mechanism and your own prior output.
2. **It reduces.** Write the quantity in its simplest equivalent form and try to
   reduce it to something known. Failing is the first real evidence of novelty.
3. **The ceiling is closed.** An oracle beats the tuned trivial baseline by less
   than the split can resolve.
4. **A random arm wins.** Shuffle the thing the method exploits.
5. **The venue has no room.** The strongest supportable sentence lands in a slice
   too small to publish into, and the subfield is small *because* of that.

Each is an afternoon at most. All five together cost less than the first week of
real work.

## The rule that makes this honest

**Decide, before looking, what result would end it.** Write that sentence down
and put it in the project's first commit. Without it, every outcome becomes
evidence for continuing, and it does so through reasoning that feels careful.

## And the symmetric rule

A kill needs the same evidence as a go. A direction abandoned on a surface
reading — "this looks occupied", "this cannot work" — gets re-proposed later by
somebody with the same good taste that proposed it the first time, and they will
not find your reasoning because you did not write it down.

So a kill is recorded with:

- the cause, from the closed taxonomy in `archive/causes-of-death.json`;
- the cheap test that settled it;
- **what would make it worth revisiting.** Hardware moved, a dataset appeared, a
  bound was improved. Several directions killed for lack of compute were
  genuinely revivable the moment a bigger machine was free, and the ones that
  said so got revived.

```bash
proofground ledger kill --id <slug> --cause ceiling-too-low \
    --what "..." --settled-by "..." --reopen-if "a split large enough to resolve 2 points"
```
