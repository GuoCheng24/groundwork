#!/usr/bin/env python3
"""Run a night's work unattended, and stop at the first gate that says stop.

The overnight research loop is the headline feature of every toolkit in this
space, and the thing they all optimise is *not stopping*. That is backwards.
A night is expensive because of what it commits you to in the morning, not
because of the GPU hours: an arm that ran all night on a wrong flag produces a
table, and the table gets believed.

So this runs a plan, in order, and **the first step that exits non-zero ends
the night**. Every tool here is built to exit non-zero at the right moment -
`gate` on a direction with no headroom, `prereg verify` on a plan younger than
its results, `shard merge` on a hole or a disagreement, `check` on a gate with
nothing behind it - and `night` is what makes those exits matter while you are
asleep.

A plan is a text file, one step per line:

    # taichu full set
    [prereg]  groundwork prereg verify prereg/PREREG_fullset.md --results results/
    [cv]      bash scripts/run_fullset_shard.sh cvbench 5
    [merge]   groundwork shard merge 'results/*_FCV_s*.jsonl' --expect 2638
    [check]   groundwork check

    groundwork night run plan.txt
    groundwork night report                # what happened, and what to decide

    groundwork night run plan.txt --notify \\
        'curl -sf -X POST "$WEBHOOK" -d "$GROUNDWORK_SUMMARY"'

No messaging vendor is built in: a webhook is a `curl`, and a tool that ships
one integration ships a token to store. The command gets the verdict in its
environment, and its exit code is reported - a notification that failed
silently is worse than none, because you are then waiting for a message that
is not coming.

What you read in the morning is `archive/night/<run>/REPORT.md`: what ran, how
long each step took, where it stopped, and the lines from the log that say why.
A night that ends at a gate is the night working.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

DIR = os.path.join("archive", "night")
STEP = re.compile(r"^\s*\[([A-Za-z0-9_.-]+)\]\s*(.+?)\s*$")


def parse(path):
    """Return [(name, command)], or raise ValueError naming the line."""
    steps, seen = [], set()
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = STEP.match(line)
            if not m:
                raise ValueError(f"{path}:{n}: expected `[name] command`, got {line.strip()!r}")
            name, cmd = m.group(1), m.group(2)
            if name in seen:
                raise ValueError(f"{path}:{n}: step {name!r} appears twice; "
                                 "a report that names a step twice cannot be read")
            seen.add(name)
            steps.append((name, cmd))
    if not steps:
        raise ValueError(f"{path}: no steps")
    return steps


def _tail(path, n=15):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return [ln.rstrip("\n") for ln in fh.readlines()[-n:]]
    except OSError:
        return []


def _why(lines):
    """The lines a person would actually read to find out what stopped it."""
    signal = re.compile(r"NO-GO|FAIL|SHORT BY|DIFFERENT CONTENT|Traceback|"
                        r"out of memory|Killed|not a pre-registration|problem")
    hits = []
    for i, ln in enumerate(lines):
        if signal.search(ln):
            hits.append(ln)
            # a verdict is followed by its reasons, and a verdict without them
            # sends the reader back to the log anyway
            for nxt in lines[i + 1:i + 4]:
                if re.match(r"\s*[*\-|]", nxt) and nxt not in hits:
                    hits.append(nxt)
    return hits[-8:] or lines[-6:]


def notify(command, env, where):
    """Run the user's notification command, and say if it failed.

    No vendor is built in. A webhook is a `curl`, a message is a `mail`, a
    desktop bell is a `notify-send` - all of them are one shell command, and a
    tool that ships one integration ships a token to store and a vendor to
    follow. What it does instead is hand the command five environment
    variables and report its exit code, because **a notification that failed
    silently is worse than none**: you are now waiting for a message that is
    never coming, and the flag file that would have told you is the thing you
    stopped checking.

    The flag file and the report remain the durable record. This is the
    convenience on top of them, not a replacement.
    """
    e = dict(os.environ)
    e.update(env)
    try:
        rc = subprocess.call(command, shell=True, env=e)
    except OSError as exc:
        print(f"  notification could not run: {exc}", file=sys.stderr)
        return 1
    if rc != 0:
        print(f"  NOTIFICATION FAILED (exit {rc}). Nothing was sent, so the only\n"
              f"  record of this night is {where} - go and read it.", file=sys.stderr)
    else:
        print(f"  notified: {command.split()[0]}")
    return rc


def cmd_run(a):
    try:
        steps = parse(a.plan)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if a.dry_run:
        for i, (n, c) in enumerate(steps, 1):
            print(f"  {i:2d}. [{n}] {c}")
        print(f"\n{len(steps)} step(s). The first non-zero exit ends the night.")
        return 0

    start_at = 0
    if a.start_from:
        names = [n for n, _c in steps]
        if a.start_from not in names:
            print(f"no step named {a.start_from!r}; plan has {' '.join(names)}", file=sys.stderr)
            return 2
        start_at = names.index(a.start_from)

    run = a.name or datetime.datetime.now().strftime("%Y%m%d-%H%M")
    out = os.path.join(DIR, run)
    os.makedirs(out, exist_ok=True)
    record = {"run": run, "plan": os.path.abspath(a.plan),
              "started": datetime.datetime.now().astimezone().isoformat(),
              "steps": []}
    print(f"night {run}: {len(steps) - start_at} step(s), log in {out}/")

    stopped = None
    for i, (name, cmd) in enumerate(steps):
        if i < start_at:
            record["steps"].append({"name": name, "command": cmd, "status": "skipped"})
            continue
        log = os.path.join(out, f"{name}.log")
        t0 = time.time()
        print(f"\n[{name}] {cmd}", flush=True)
        with open(log, "w", encoding="utf-8") as fh:
            rc = subprocess.call(cmd, shell=True, stdout=fh, stderr=subprocess.STDOUT)
        dt = time.time() - t0
        tail = _tail(log)
        record["steps"].append({"name": name, "command": cmd, "rc": rc,
                                "seconds": round(dt, 1), "log": log,
                                "status": "ok" if rc == 0 else "stopped"})
        print(f"  rc={rc}  {dt / 60:.1f} min  -> {log}", flush=True)
        if rc != 0:
            for ln in _why(tail):
                print(f"  | {ln}", flush=True)
            stopped = name
            for j in range(i + 1, len(steps)):
                # the steps that did NOT run are the point of the report: they
                # are what the morning is free to reconsider
                record["steps"].append({"name": steps[j][0], "command": steps[j][1],
                                        "status": "not reached"})
            break

    record["ended"] = datetime.datetime.now().astimezone().isoformat()
    record["stopped_at"] = stopped
    with open(os.path.join(out, "night.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    report = write_report(out, record)
    print(f"\n{report}")
    if a.notify:
        summary = (f"night {run}: STOPPED at [{stopped}]" if stopped
                   else f"night {run}: all {len(steps) - start_at} step(s) passed")
        notify(a.notify, {"GROUNDWORK_RUN": run,
                          "GROUNDWORK_STATUS": "stopped" if stopped else "ok",
                          "GROUNDWORK_STEP": stopped or "",
                          "GROUNDWORK_REPORT": os.path.abspath(report),
                          "GROUNDWORK_SUMMARY": summary}, report)
    if stopped:
        print(f"\nThe night stopped at [{stopped}]. That is the tool working: the step\n"
              "exited non-zero and nothing downstream ran on top of it.")
        return 1
    print("\nEvery step passed. Note that this says the commands succeeded, not that\n"
          "the result is right - run the claim stage before writing a sentence.")
    return 0


def write_report(out, record):
    path = os.path.join(out, "REPORT.md")
    L = [f"# Night {record['run']}", "",
         f"Plan `{record['plan']}`  ", f"{record['started']} → {record.get('ended', '')}", ""]
    done = [s for s in record["steps"] if s.get("status") in ("ok", "stopped")]
    total = sum(s.get("seconds", 0) for s in done)
    L += ["| step | result | minutes |", "|---|---|---|"]
    for s in record["steps"]:
        st = s.get("status")
        mark = {"ok": "ok", "stopped": "**STOPPED**", "skipped": "skipped",
                "not reached": "did not run"}[st]
        L.append(f"| `{s['name']}` | {mark} | {s.get('seconds', 0) / 60:.1f} |")
    unrun = [s for s in record["steps"] if s.get("status") == "not reached"]
    L += ["", f"{len(done)} step(s) ran, {total / 60:.0f} minutes total."
          + (f" {len(unrun)} did not run." if unrun else ""), ""]
    if record.get("stopped_at"):
        s = next(x for x in record["steps"] if x["name"] == record["stopped_at"])
        L += [f"## It stopped at `{s['name']}`", "",
              f"```\n{s['command']}\n```", "",
              "exited " + str(s["rc"]) + ". From its log:", "", "```"]
        L += _why(_tail(s["log"]))
        L += ["```", "",
              "**Decide this before anything else runs on top of it.** The step that",
              "stopped is upstream of everything that did not run, so a fix applied",
              "further down would be a fix to a number this never produced.", "",
              f"To continue after fixing it:", "",
              f"```bash\ngroundwork night run {record['plan']} --from {s['name']}\n```"]
    else:
        L += ["## Every step passed", "",
              "Which says the commands succeeded, not that the result is right.",
              "Run the claim stage before writing a sentence about any of it."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def cmd_report(a):
    if not os.path.isdir(DIR):
        print(f"no nights recorded under {DIR}/")
        return 1
    runs = sorted(d for d in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, d)))
    if a.name:
        runs = [r for r in runs if r == a.name]
    if not runs:
        print("no such night")
        return 1
    path = os.path.join(DIR, runs[-1], "REPORT.md")
    if not os.path.exists(path):
        print(f"{runs[-1]}: no report - it may still be running")
        return 1
    with open(path, encoding="utf-8") as fh:
        print(fh.read())
    with open(os.path.join(DIR, runs[-1], "night.json"), encoding="utf-8") as fh:
        return 1 if json.load(fh).get("stopped_at") else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork night",
                                 description="run a plan unattended; stop at the first gate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the plan")
    r.add_argument("plan")
    r.add_argument("--name", help="what to call this night (default: the timestamp)")
    r.add_argument("--from", dest="start_from", metavar="STEP",
                   help="resume from this step, after fixing what stopped it")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--notify", metavar="CMD",
                   help="shell command to run when the night ends. It is given "
                        "GROUNDWORK_RUN, GROUNDWORK_STATUS (ok|stopped), "
                        "GROUNDWORK_STEP, GROUNDWORK_REPORT and GROUNDWORK_SUMMARY, "
                        "and its exit code is reported - a notification that fails "
                        "silently is worse than none")
    r.set_defaults(func=cmd_run)
    p = sub.add_parser("report", help="read the morning report")
    p.add_argument("--name")
    p.set_defaults(func=cmd_report)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":      # pragma: no cover
    sys.exit(main())
