#!/usr/bin/env python3
"""Find the idle GPUs on a shared cluster, and plan work across them.

An autonomous research loop that assumes one machine will spend most of its
night queued behind somebody else's job. A shared academic cluster usually has
far more capacity than the node you habitually use - the constraint is knowing
where it is at 1 a.m. and being a good enough neighbour to be allowed back.

    groundwork cluster survey  --nodes gpu01 gpu02 gpu03
    groundwork cluster pick    --nodes gpu01 gpu02 gpu03 --need-gb 20 --count 4
    groundwork cluster plan    --nodes gpu01 gpu02 gpu03 --need-gb 20 --shards 4

Three habits are built in, each of them learnt the hard way:

* **Somebody else's job is not free memory.** A card with 19 GB in use and 5 GB
  free is not an idle card, and a job placed there dies of out-of-memory at 3
  a.m. after the queue has moved on. `pick` ranks by free memory and refuses
  what does not fit with a margin.
* **Leave something.** By default one GPU per node is left alone, so the next
  person still has somewhere to run. Shared clusters are social.
* **Architecture is a variable, not a detail.** The same weights on two
  different cards do not always produce the same number. `survey` reports the
  GPU name next to the memory, and `plan` refuses to split one arm across
  different GPU models unless told to.

Reads `nvidia-smi` over ssh and nothing else, so it works wherever passwordless
ssh does. `--from-file` replays a saved survey, which is how the tests run.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

QUERY = "--query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits"


def probe(node, timeout=25):
    """Return a list of GPU dicts for `node`, or None if it is unreachable."""
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", node,
           f"nvidia-smi {QUERY}"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    gpus = []
    for line in p.stdout.strip().splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 5:
            continue
        try:
            idx, name, used, total, util = int(parts[0]), parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        except ValueError:
            continue
        gpus.append({"node": node, "index": idx, "name": name,
                     "used_mb": used, "total_mb": total, "free_mb": total - used,
                     "util_pct": util})
    return gpus


def survey(nodes, from_file=None):
    if from_file:
        with open(from_file, encoding="utf-8") as fh:
            return json.load(fh)
    out = {}
    for n in nodes:
        g = probe(n)
        out[n] = g if g is not None else []
    return out


def rank(surveyed, need_gb, leave_free=1, occupied_mb=500):
    """Cards that fit `need_gb`, best first, with `leave_free` per node held back.

    "Best" is free memory, then low utilisation: a card with another user's job
    on it may still have room, but it will be slower and it is somebody else's.
    """
    need_mb = int(need_gb * 1024)
    chosen = []
    for node, gpus in surveyed.items():
        usable = [g for g in gpus if g["free_mb"] >= need_mb]
        usable.sort(key=lambda g: (-g["free_mb"], g["util_pct"], g["index"]))
        idle = [g for g in gpus if g["used_mb"] < occupied_mb]
        # Hold back the idlest cards, not the busiest - leaving somebody the
        # scraps is not leaving them anything.
        hold = {(g["node"], g["index"]) for g in
                sorted(idle, key=lambda g: (-g["free_mb"], g["index"]))[:leave_free]}
        for g in usable:
            if (g["node"], g["index"]) in hold:
                g = dict(g, held_back=True)
            chosen.append(g)
    chosen.sort(key=lambda g: (bool(g.get("held_back")), -g["free_mb"], g["util_pct"]))
    return chosen


def cmd_survey(a):
    s = survey(a.nodes, a.from_file)
    total_idle = 0
    for node, gpus in s.items():
        if not gpus:
            print(f"{node}: unreachable or no GPUs")
            continue
        print(f"{node}:")
        for g in gpus:
            idle = g["used_mb"] < 500
            total_idle += idle
            print(f"   [{g['index']}] {g['name']:<26} {g['free_mb'] / 1024:6.1f} GB free "
                  f"of {g['total_mb'] / 1024:5.1f}   util {g['util_pct']:3d}%"
                  + ("   idle" if idle else ""))
    print(f"\n{total_idle} idle card(s) across {len([n for n, g in s.items() if g])} reachable node(s).")
    if a.save:
        with open(a.save, "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=1)
        print(f"wrote {a.save}")
    return 0


def cmd_pick(a):
    s = survey(a.nodes, a.from_file)
    ranked = rank(s, a.need_gb, a.leave_free)
    usable = [g for g in ranked if not g.get("held_back")]
    if not usable:
        print(f"Nothing with {a.need_gb} GB free, once {a.leave_free} card(s) per node are "
              f"left for other people.")
        return 1
    for g in usable[:a.count]:
        print(f"{g['node']} gpu {g['index']}  {g['name']}  {g['free_mb'] / 1024:.1f} GB free")
    if len(usable) < a.count:
        print(f"\nonly {len(usable)} of the {a.count} requested are available")
    return 0


def cmd_plan(a):
    s = survey(a.nodes, a.from_file)
    ranked = [g for g in rank(s, a.need_gb, a.leave_free) if not g.get("held_back")]
    take = ranked[:a.shards]
    if not take:
        print("no card fits; nothing to plan")
        return 1
    models = {g["name"] for g in take}
    if len(models) > 1 and not a.mixed:
        print("These cards are not all the same model:")
        for m in sorted(models):
            print(f"   {m}")
        print("\nThe same weights on two different cards do not always produce the same\n"
              "number, so one arm split across them is a confounded arm. Pass --mixed if\n"
              "the split really is only a throughput knob for this job, and record it.")
        return 1
    label = take[0]["name"] if len(models) == 1 else " + ".join(sorted(models)) + "  (MIXED)"
    print(f"# {len(take)} shard(s), {label}")
    for i, g in enumerate(take):
        print(f"ssh {g['node']} 'CUDA_VISIBLE_DEVICES={g['index']} "
              f"{a.command} --shard {i}/{len(take)}' &")
    print("\n# shards own items[i::n] of the fixed item list, sliced BEFORE the")
    print("# already-done filter, so a restarted shard keeps the items it had.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork cluster")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, help):
        # --nodes takes a list, so it has to live on the subcommand: a top-level
        # nargs="+" swallows the subcommand name itself.
        sp = sub.add_parser(name, help=help)
        sp.add_argument("--nodes", nargs="+", default=[])
        sp.add_argument("--from-file", help="replay a saved survey instead of probing")
        return sp

    s = add("survey", "what is free, everywhere")
    s.add_argument("--save")
    s.set_defaults(func=cmd_survey)
    p = add("pick", "the idlest cards that fit")
    p.add_argument("--need-gb", type=float, required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--leave-free", type=int, default=1)
    p.set_defaults(func=cmd_pick)
    q = add("plan", "a shard plan across the idlest cards")
    q.add_argument("--need-gb", type=float, required=True)
    q.add_argument("--shards", type=int, required=True)
    q.add_argument("--leave-free", type=int, default=1)
    q.add_argument("--command", default="python run.py")
    q.add_argument("--mixed", action="store_true", help="allow different GPU models in one arm")
    q.set_defaults(func=cmd_plan)
    a = ap.parse_args(argv)
    if not a.nodes and not a.from_file:
        ap.error("need --nodes or --from-file")
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
