# Theory — attacking a stated open problem across days

A theory track has a different failure mode from an empirical one: not a wrong
number, but months on a statement that was already known, already false, or true
and uninteresting.

## Attack a *stated* open problem

The highest-yield target is a specific open question stated in a recent paper by
the people who could not solve it. They have already done the occupancy check,
they have said what is hard, and they will read your solution.

"Improve the bounds in this area" is not that. "Extend the lower bound to the
regime the authors say is open" is.

## Occupancy is harder here, and the failure is worse

A theoretical result can be occupied by a paper in a different field using
different vocabulary, decades ago. Three separate routes in one programme
collapsed onto results that were already known: a failure mode reduced to a
known balance condition under a change of variables; a statistical-computational
gap collapsed back onto a classical problem; a core construction turned out to be
pre-announced in a section of a paper that had been cited but not read past the
abstract.

**Before the first serious attempt**: write the statement in its simplest
equivalent form, search *that*, and read the two nearest papers in full.

## Ceiling applies here too

A bound can be improvable and the improvement can be uninteresting. Ask, before
starting: what is the strongest version of this result, and which venue prints
that statement? One programme's matrix route was genuinely closed by prior work;
the vector version survived, at a smaller venue, and knowing that early changed
the writing rather than the year.

## Verify the proof mechanically where you can

- **check every lemma on a small case numerically** before believing the general
  argument. One monotonicity claim in a programme was refuted by a
  three-element counterexample found in an afternoon, after the argument had
  been written;
- **state every constant and every regime**. A constant that is "absolute" in
  the write-up and depends on a parameter in the proof is the error a referee
  finds;
- **an activation, an assumption or a smoothness condition that is only used in
  one step** should be stated at that step, not in the preamble. It is often the
  step where the result is actually narrower than claimed.

## Write the statement before the proof

A theorem statement that is hard to write is usually a theorem that is not yet
true. Write it, write what it would imply, and check that the implication is the
thing you wanted. Several results survive their proofs and do not survive that
question.
