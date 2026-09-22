# Hardware is a variable, and it is not a small one

The assumption in almost every experimental report is that the machine is a
detail. Measured, it is not.

## What was measured

Same weights, same data with the same checksum, same batch size, same seed,
**greedy decoding** — no sampling noise at all — same scorer, same library
versions. Two different GPU models:

| | RTX 4090 | L40 |
|---|---|---|
| prompt-level strict accuracy, 541 prompts | **76.89%** | **75.42%** |

**1.48 points from changing nothing but the card.** The same arm repeated on a
second card of the *same* model reproduced **541 of 541** generations byte for
byte, so this is not run-to-run nondeterminism — within a machine, greedy
generation was exactly reproducible.

And on a numerical measurement rather than a benchmark, across three cards
spanning two architectures — including one with no native bfloat16 tensor cores
at all — the effect under study was present on **all three** and removed by
fp32 on **all three**, while its size moved by a fraction of a point between two
chips of the same architecture and by several points on the third.

## What follows for an experiment

1. **Record the card, not just the framework.** Device name, compute
   capability, streaming-multiprocessor count, driver and library versions, read
   from the runtime rather than typed. A results file that does not say which
   GPU produced it cannot be compared with anything.
2. **Never split one experimental arm across two GPU models.** It is a
   confounded arm. `proofground cluster plan` refuses unless told the split is
   only a throughput knob — and then it records that it was told.
3. **A difference smaller than the hardware spread is not a finding.** Before
   comparing arms run on different machines, you need the spread; if you have
   not measured it, you do not have a comparison.
4. **Run the same-machine repeat.** It costs one more run and it is what
   separates "these cards differ" from "any two runs differ". Without it the
   first claim is not available to you — a pre-registration that called a
   cross-card comparison "the clean hardware test" was wrong until that control
   existed.

## What this does not license

It does not license attributing every difference to hardware. The mechanism
above was established at the level of log probabilities under paired,
greedy conditions in a dedicated measurement. A benchmark score moving between
two machines is consistent with it and does not re-establish it, and a write-up
should say which of the two it is doing.
