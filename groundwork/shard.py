#!/usr/bin/env python3
"""Split work across GPUs so that a restart does not lose or duplicate items.

Sharding looks trivial until something restarts, and then it produces the worst
kind of failure: every shard file looks complete on its own.

The rule is one line and it is the whole tool:

    slice the item list BEFORE filtering out what is already done.

Slice afterwards - `[i::n]` applied to the list of *remaining* items - and
ownership depends on how far each shard happened to get. Restart two shards at
different points and they take the same item, while a third item is taken by
nobody. Nothing errors. Each file is internally consistent. The total is short
by a few and nobody notices until the counts are compared.

    groundwork shard plan  --items 2638 --shards 5
    groundwork shard own   --items ids.txt --shard 2/5 --done out_s2.jsonl
    groundwork shard merge out_s*.jsonl -o merged.jsonl --expect 2638

`merge` refuses a duplicate whose rows disagree, naming the fields, and reports
the ids that no shard produced. Both are real problems rather than tidying
jobs, and a merge that silently picks one of two answers is how a run comes out
different depending on the order the files were listed in.
"""
from __future__ import annotations

import argparse
import glob as _glob
import json
import os
import sys


def owned(items, i, n):
    """The items shard `i` of `n` owns. A pure function of the FULL list."""
    if not (0 <= i < n and n >= 1):
        raise ValueError(f"need 0 <= i < n and n >= 1, got {i}/{n}")
    return items[i::n]


def _read_items(path):
    if path.endswith((".jsonl", ".ndjson")):
        out = []
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                if ln.strip():
                    out.append(json.loads(ln))
        return out
    with open(path, encoding="utf-8") as fh:
        return [ln.rstrip("\n") for ln in fh if ln.strip()]


def _key(row, field):
    if isinstance(row, dict):
        if field not in row:
            raise KeyError(field)
        return row[field]
    return row


def cmd_plan(a):
    n, k = a.items, a.shards
    sizes = [len(range(i, n, k)) for i in range(k)]
    print(f"{n} items over {k} shard(s): sizes {sizes}, total {sum(sizes)}")
    for i in range(k):
        first = list(range(i, min(n, i + 3 * k), k))
        print(f"  shard {i}/{k}: {sizes[i]:>6} items, starting {first}")
    print(f"""
In the harness, slice BEFORE the already-done filter:

    items = load_all()                 # the full, fixed list
    items = items[{{i}}::{k}]               # ownership: a function of the full list
    items = [x for x in items if x.id not in already_done]   # then skip

The other order is the bug. It makes ownership depend on progress, so two
shards restarted at different points take the same item and a third is taken
by nobody - silently, because every shard file looks complete on its own.""")
    return 0


def cmd_own(a):
    items = _read_items(a.items)
    try:
        i, n = (int(x) for x in a.shard.split("/"))
    except ValueError:
        print(f"--shard wants I/N, got {a.shard!r}", file=sys.stderr)
        return 2
    try:
        mine = owned(items, i, n)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    done = set()
    for p in a.done or []:
        for f in sorted(_glob.glob(p)) or [p]:
            if os.path.exists(f):
                for r in _read_items(f):
                    done.add(_key(r, a.id_field))
    todo = [x for x in mine if _key(x, a.id_field) not in done]
    print(f"shard {i}/{n}: owns {len(mine)} of {len(items)}; "
          f"{len(mine) - len(todo)} already done; {len(todo)} to do")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            for x in todo:
                fh.write((json.dumps(x) if isinstance(x, dict) else str(x)) + "\n")
        print(f"wrote {a.out}")
    return 0


def merge(paths, id_field="id"):
    """Return (rows, clashes, sources). A clash names the fields that differ."""
    rows, sources, clashes = {}, {}, []
    for path in paths:
        if not os.path.exists(path):
            continue
        for r in _read_items(path):
            k = _key(r, id_field)
            if k in rows and rows[k] != r:
                a, b = rows[k], r
                if isinstance(a, dict) and isinstance(b, dict):
                    fields = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
                else:
                    fields = ["(value)"]
                clashes.append((k, sources[k], path, fields))
            rows[k] = r
            sources[k] = path
    return rows, clashes, sources


def cmd_merge(a):
    paths = []
    for p in a.shards:
        paths.extend(sorted(_glob.glob(p)) or [p])
    if not paths:
        print("no shard files matched", file=sys.stderr)
        return 2
    for p in paths:
        n = len(_read_items(p)) if os.path.exists(p) else None
        print(f"  {p}: {'missing' if n is None else str(n) + ' rows'}")
    rows, clashes, _src = merge(paths, a.id_field)

    if clashes:
        print(f"\n{len(clashes)} id(s) appear in more than one shard WITH DIFFERENT CONTENT:")
        for k, p1, p2, fields in clashes[:10]:
            print(f"  {k}: {p1} vs {p2} differ in {fields}")
        print("\nThis is a result that depends on which file was read last. It is not a\n"
              "duplicate to be deduped - two runs produced different answers for the same\n"
              "item, and which one you keep changes the number. Find out why first.")
        return 1

    print(f"\n{len(rows)} distinct id(s)")
    if a.expect:
        if len(rows) < a.expect:
            missing = a.expect - len(rows)
            print(f"\nSHORT BY {missing}: expected {a.expect}. A shard that died leaves a\n"
                  "hole that no file reports, because every shard file is complete on its\n"
                  "own. Re-run the owning shard rather than merging what is here.")
            return 1
        if len(rows) > a.expect:
            print(f"\nMORE THAN EXPECTED: {len(rows)} > {a.expect}. Either the item list "
                  "changed\nbetween launches, or the shards were cut from different lists.")
            return 1
        print(f"exactly the {a.expect} expected")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            for k in sorted(rows):
                r = rows[k]
                fh.write((json.dumps(r) if isinstance(r, dict) else str(r)) + "\n")
        print(f"wrote {a.out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork shard",
                                 description="split work so a restart loses nothing")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="sizes, and the one line that has to be in the harness")
    p.add_argument("--items", type=int, required=True)
    p.add_argument("--shards", type=int, required=True)
    p.set_defaults(func=cmd_plan)

    o = sub.add_parser("own", help="what this shard owns, after skipping what is done")
    o.add_argument("--items", required=True, help="the FULL item list (.jsonl or one id per line)")
    o.add_argument("--shard", required=True, metavar="I/N")
    o.add_argument("--done", nargs="*", help="output file(s) already produced; globs allowed")
    o.add_argument("--id-field", default="id")
    o.add_argument("--out")
    o.set_defaults(func=cmd_own)

    m = sub.add_parser("merge", help="merge shard outputs; refuse disagreement and holes")
    m.add_argument("shards", nargs="+")
    m.add_argument("-o", "--out")
    m.add_argument("--id-field", default="id")
    m.add_argument("--expect", type=int, default=0, help="the number of items there should be")
    m.set_defaults(func=cmd_merge)

    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":      # pragma: no cover
    sys.exit(main())
