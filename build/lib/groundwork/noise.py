#!/usr/bin/env python3
"""Measure your instrument before you quote a difference with it.

Every stage note here says some version of *a difference smaller than your
scorer's own spread is not a finding*, and nobody measures the spread, because
scoring feels deterministic. It usually is not: a language detector with a
global random state, a tokeniser, a model call, a set iterated in hash order.

An official benchmark scorer, run ten times on one unchanged file, spanned 0.37
points on its headline metric and disagreed with itself on 2 prompts of 541.
**Three runs had said it was stable.** Three draws were not enough to see it,
which is the reason the default here is ten.

    groundwork noise --n 10 --command 'python score.py --in generations.jsonl'

The command is expected to print `name value` lines - the same convention
`doubleblind trace --derive` uses - or a flat JSON object. Anything it prints
that is not a number is ignored.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys

PAIR = re.compile(r"^\s*([A-Za-z][\w .:/-]*?)\s*[:=]?\s*(-?\d+(?:\.\d+)?)\s*$")


def parse(text):
    """`name value` lines, or a flat JSON object. Returns {name: float}."""
    text = text.strip()
    if text.startswith("{"):
        try:
            d = json.loads(text)
            return {k: float(v) for k, v in d.items()
                    if isinstance(v, (int, float)) and not isinstance(v, bool)}
        except (ValueError, TypeError):
            pass
    out = {}
    for line in text.splitlines():
        m = PAIR.match(line)
        if m:
            out[m.group(1).strip()] = float(m.group(2))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork noise",
                                 description="How much does your scorer move on a file that "
                                             "never changes?")
    ap.add_argument("--command", required=True, help="a command that scores and prints numbers")
    ap.add_argument("--n", type=int, default=10,
                    help="repetitions (default 10; three is not enough - measured)")
    ap.add_argument("--json", help="write the table here")
    ap.add_argument("--fail-above", type=float,
                    help="exit non-zero if any metric's spread exceeds this")
    a = ap.parse_args(argv)

    runs = []
    for i in range(a.n):
        proc = subprocess.run(a.command, shell=True, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"run {i + 1} exited {proc.returncode}:\n{proc.stderr.strip()[:800]}",
                  file=sys.stderr)
            return 2
        vals = parse(proc.stdout)
        if not vals:
            print("the command printed no numbers this run. It should print `name value`\n"
                  "lines or a flat JSON object.", file=sys.stderr)
            return 2
        runs.append(vals)

    keys = sorted(set().union(*(set(r) for r in runs)))
    rows, moved = [], 0
    print(f"{a.n} runs of an unchanged input\n")
    for k in keys:
        vs = [r[k] for r in runs if k in r]
        if len(vs) < a.n:
            print(f"  {k:<40} appeared in only {len(vs)} of {a.n} runs")
        lo, hi = min(vs), max(vs)
        spread = hi - lo
        distinct = len(set(vs))
        moved += spread > 0
        rows.append({"metric": k, "min": lo, "max": hi, "spread": spread,
                     "distinct_values": distinct, "median": statistics.median(vs)})
        flag = "" if spread == 0 else f"   {distinct} distinct value(s)"
        print(f"  {k:<40} {lo:>12.6g} .. {hi:<12.6g} spread {spread:.6g}{flag}")

    print()
    if moved == 0:
        print("Nothing moved across these runs. That is evidence, not proof: three runs\n"
              "of one real scorer said the same thing and ten did not. If a verdict will\n"
              "rest on a small difference, run more.")
    else:
        print(f"{moved} of {len(keys)} metric(s) moved on an input that did not.\n"
              "Any arm-to-arm difference smaller than the spread above is not a finding\n"
              "about the arms. Quote the spread next to the difference.")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"command": a.command, "n": a.n, "metrics": rows}, fh, indent=1)
        print(f"\nwrote {a.json}")

    if a.fail_above is not None:
        worst = max((r["spread"] for r in rows), default=0.0)
        if worst > a.fail_above:
            print(f"\nworst spread {worst:.6g} exceeds --fail-above {a.fail_above}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
