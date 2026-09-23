#!/usr/bin/env python3
"""The record that makes the next project cheaper: what died, and what got through.

Two files, two jobs, and they compound differently.

**`archive/`** is the list of directions that were killed, each with the cause
and the cheap test that settled it. Its value is entirely in being read *before*
a direction is started - a NO-GO nobody wrote down is one you pay for twice,
usually by re-proposing it yourself in four months.

**the ledger** is the list of defects that got through, each with the layer that
missed it and why that layer could not have seen it. Its value is that entries
convert: a finding that stays prose is worth one catch, the same finding as a
check that fails on a deliberately broken input is worth every future one. The
entries that *cannot* convert are worth recording too, because they are the map
of where the mechanical layer stops.

    groundwork ledger kill   --id topo-repair --cause ceiling-too-low \
                              --what "oracle beat the baseline by 1.7 points" \
                              --settled-by "oracle + strongest baseline, one afternoon"
    groundwork ledger defect --id stale-pdf --missed-by mechanical \
                              --what "the built PDF quoted replaced figures" \
                              --why "every check read the source" \
                              --check "re-extract from the artifact and match"
    groundwork ledger roll
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The record belongs to YOUR project, so it is written under ./archive/ in the
# directory you run from - not into wherever this package happens to be
# installed. The taxonomy is the opposite: it ships with the package, because a
# closed taxonomy that each project edits separately stops being countable.
ARCHIVE = os.path.join("archive", "killed.json")
LEDGER = os.path.join("archive", "ledger.json")
_CAUSE_CANDIDATES = [
    os.path.join(HERE, "causes-of-death.json"),                     # installed
    os.path.join(os.path.dirname(HERE), "archive", "causes-of-death.json"),  # repo
    os.path.join("archive", "causes-of-death.json"),                # your own copy
]
CAUSES = next((p for p in _CAUSE_CANDIDATES if os.path.exists(p)), _CAUSE_CANDIDATES[0])
LAYERS = ("mechanical", "reviewer", "figure", "both", "all")


def _load(path, key):
    if not os.path.exists(path):
        return {"schema": f"groundwork-{key}/1", key: []}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def _causes():
    with open(CAUSES, encoding="utf-8") as fh:
        return {c["id"]: c for c in json.load(fh)["causes"]}


def cmd_kill(a):
    known = _causes()
    if a.cause not in known:
        print(f"unknown cause {a.cause!r}. The taxonomy is closed on purpose - a new "
              f"cause means a new entry in archive/causes-of-death.json, not a free-text "
              f"field nobody can count.\n\nknown causes:")
        for cid, c in known.items():
            print(f"  {cid:<28} {c['name']}")
        return 2
    data = _load(ARCHIVE, "killed")
    if any(e["id"] == a.id for e in data["killed"]):
        print(f"{a.id} is already in the archive. A direction is killed once; if it is "
              f"being revisited, that is a new entry with a new id and a reference to "
              f"this one.")
        return 1
    data["killed"].append({
        "id": a.id,
        "date": a.date or datetime.date.today().isoformat(),
        "cause": a.cause,
        "what_happened": a.what,
        "settled_by": a.settled_by,
        "cost": a.cost or known[a.cause]["cost_when_missed"],
        "reopen_if": a.reopen_if or "",
    })
    _save(ARCHIVE, data)
    print(f"recorded {a.id} as {a.cause} ({known[a.cause]['name']})")
    print(f"archive now holds {len(data['killed'])} killed direction(s)")
    print("\nRead this before the next direction, not after it.")
    return 0


def cmd_defect(a):
    if a.missed_by not in LAYERS:
        print(f"--missed-by must be one of {', '.join(LAYERS)}")
        return 2
    data = _load(LEDGER, "defects")
    if any(e["id"] == a.id for e in data["defects"]):
        print(f"{a.id} is already in the ledger")
        return 1
    data["defects"].append({
        "id": a.id,
        "date": a.date or datetime.date.today().isoformat(),
        "missed_by": a.missed_by,
        "what_shipped": a.what,
        "why_invisible": a.why,
        "check_now": a.check or "",
        "converts": bool(a.check),
    })
    _save(LEDGER, data)
    n = len(data["defects"])
    conv = sum(1 for e in data["defects"] if e["converts"])
    print(f"recorded {a.id}; ledger holds {n} defect(s), {conv} converted into checks")
    if not a.check:
        print("\nNo check given. That is a real answer for some defects - a correct number")
        print("in a false sentence has no mechanical equivalent - but if one exists, the")
        print("entry is worth ten times more with it. Add it with --check.")
    return 0


def cmd_roll(a):
    killed = _load(ARCHIVE, "killed")["killed"]
    defects = _load(LEDGER, "defects")["defects"]
    causes = _causes()

    print(f"archive: {len(killed)} direction(s) killed")
    if killed:
        by = {}
        for e in killed:
            by.setdefault(e["cause"], []).append(e["id"])
        for cause, ids in sorted(by.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(ids):>3}  {causes[cause]['name']}")
            if a.verbose:
                for i in ids:
                    print(f"        {i}")
        top = max(by.items(), key=lambda kv: len(kv[1]))
        print(f"\n  The one that keeps happening: {causes[top[0]]['name']}")
        print(f"  Cheap test: {causes[top[0]]['cheap_test']}")
        print(f"  Gate: {causes[top[0]]['gate']}")

    print(f"\nledger: {len(defects)} defect(s) that got through")
    if defects:
        by = {}
        for e in defects:
            by.setdefault(e["missed_by"], []).append(e["id"])
        for layer, ids in sorted(by.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(ids):>3}  missed by {layer}")
        conv = sum(1 for e in defects if e["converts"])
        print(f"\n  {conv} of {len(defects)} converted into a check that fails on a broken input.")
        unconverted = [e for e in defects if not e["converts"]]
        if unconverted:
            print(f"  {len(unconverted)} did not, which is the map of where the mechanical")
            print("  layer stops - not a backlog:")
            for e in unconverted[:5]:
                print(f"      {e['id']}: {e['why_invisible'][:72]}")
    if not killed and not defects:
        print("\nNothing recorded yet. The first entry is usually the one you were about")
        print("to not write down.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)

    k = sub.add_parser("kill", help="record a direction that died, with its cause")
    k.add_argument("--id", required=True)
    k.add_argument("--cause", required=True, help="an id from archive/causes-of-death.json")
    k.add_argument("--what", required=True, help="what actually happened")
    k.add_argument("--settled-by", required=True, help="the cheap test that ended it")
    k.add_argument("--cost")
    k.add_argument("--reopen-if", help="what would make this worth revisiting")
    k.add_argument("--date")
    k.set_defaults(func=cmd_kill)

    d = sub.add_parser("defect", help="record a defect that got through, and the layer that missed it")
    d.add_argument("--id", required=True)
    d.add_argument("--missed-by", required=True, help=f"one of {', '.join(LAYERS)}")
    d.add_argument("--what", required=True)
    d.add_argument("--why", required=True, help="why that layer could not have seen it")
    d.add_argument("--check", help="the mechanical check that catches it now, if one exists")
    d.add_argument("--date")
    d.set_defaults(func=cmd_defect)

    r = sub.add_parser("roll", help="what the record says, grouped")
    r.add_argument("-v", "--verbose", action="store_true")
    r.set_defaults(func=cmd_roll)

    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
