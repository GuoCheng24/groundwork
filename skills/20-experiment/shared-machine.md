# Sharing a machine with people who are not you

An agent that treats a shared cluster as its own will get results and make
enemies, and the second one eventually costs more than the first.

## Never hard-code a device

A script with `cuda:0` in it will sit behind somebody else's job forever. Pick
the idlest card at start-up, by free memory **and** utilisation, and fall back
rather than crash:

```bash
proofground cluster pick --nodes node16 node17 node18 --need-gb 20 --count 1
```

And do not default a small model to the CPU to be polite. The CPU is shared too,
it is slower, and occupying it interferes with other people's ordinary processes.
An idle GPU is the courteous choice as well as the fast one.

## Memory etiquette, which is the one everybody forgets

GPU etiquette is well known. Host memory is not, and it is where the incident
happens.

One node's kernel log recorded *"claude invoked oom-killer"*, and the process it
killed belonged to another user. The reading that looks obvious is wrong in both
directions:

> **"X invoked oom-killer" means the system was already out of memory when X
> asked for some.** X is the last straw, not the main consumer.

At that moment the agent's own processes held about 2.5 GB in total. But the
account *was* the node's largest consumer overall — roughly 28 GB — and almost
all of it was its own experiments: four concurrent runs at 3.5–3.7 GB each, plus
two more at 5.5 GB.

So: neither plead guilty on seeing your name, nor claim innocence. **Check the
whole-node ranking.**

```bash
free -g
ps -eo user,rss --no-headers | awk '{s[$1]+=$2} END {for (u in s) if (s[u]>1048576)
  printf "%-12s %6.1f GB\n", u, s[u]/1048576}' | sort -k2 -rn | head
```

Rules that follow:

1. check free memory **and** the per-user ranking before launching anything
   concurrent — do not default to filling the machine;
2. size concurrency as *remaining memory ÷ per-process RSS ÷ 2*, leaving room
   for other people;
3. for anything running over an hour, **check again during the run**, not only
   at launch;
4. `/dev/shm` counts as memory. A process with a large shared-memory footprint
   is the single biggest risk on a node, and it will not look large in a naive
   process listing.

## Leave something behind you

`proofground cluster` holds back one idle card per node by default, and holds
back an *idle* one rather than the scraps. If you take everything every night,
the next request for capacity is a conversation rather than a command.
