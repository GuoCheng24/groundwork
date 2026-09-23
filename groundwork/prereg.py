#!/usr/bin/env python3
"""A pre-registration that a machine can check, including the part everyone skips.

"We pre-registered this" is usually a sentence in a paper. What makes it worth
anything is an artifact that existed, verifiably, before the run - and the
failure mode is not fraud, it is drift: the analysis gets written up after the
numbers are in, the stopping rule acquires an exception, and the document that
was going to fix all of that is edited one last time.

So this does three things:

    new     scaffold a pre-registration whose required sections are the ones
            that get quietly dropped - the stopping rule, the interpretation of
            *both* outcomes, and an honest note about what was already known
            when it was written
    seal    hash it, so a later edit is visible
    verify  check the hash, check the sections are actually filled in, and -
            the part that matters - check with git that the pre-registration was
            committed BEFORE the results it governs

That last check is the whole point. A pre-registration committed after its
results is a write-up, and no amount of careful wording changes that.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys

REQUIRED = [
    ("What is held fixed", "the model, data, decoding, scorer - everything the result must not depend on"),
    ("What changes", "the one thing under study, and nothing else"),
    ("Pre-stated analysis", "the test, the threshold, and what each number would mean"),
    ("Stopping rule", "when generation stops, and what is reported if it stops early"),
    ("Both outcomes", "what gets written if it comes out the other way - in advance"),
    ("What was known when this was written", "an honest note; say plainly if a partial result was already seen"),
]

TEMPLATE = """# Pre-registration — {title}

Written **{when}**, BEFORE any of the run below has been started.

## What is held fixed

<!-- the model, the data and its checksum, the decoding parameters, the scorer.
     Everything the result must not be allowed to depend on. -->

## What changes

<!-- The one thing under study. If there is more than one, this is not one
     experiment. -->

## Pre-stated analysis

<!-- The test, the threshold, the interval, and what each possible number would
     mean. Write the sentence you would publish for each outcome. -->

## Stopping rule

<!-- When generation stops. What is reported if it stops early, and under what
     label. A cap chosen after seeing a score is not a cap. -->

## Both outcomes

<!-- The outcome you expect, and the one you do not, each with the sentence that
     would be written. If you cannot write the second sentence now, you are not
     ready to run this. -->

## What was known when this was written

<!-- Say plainly whether any part of this result has already been seen, and what
     the reason for running it is. An arm launched after a partial score is not
     disqualified - an undisclosed one is. -->

## No further amendment will be made on the basis of seeing these scores.
"""


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(args, cwd):
    try:
        p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def committed_at(path, first=True):
    """Unix time `path` entered version control (`first`), or last changed.

    Which one you ask for decides whether this test works at all. The question
    a pre-registration has to answer is *when did it enter the record* - and
    that is the FIRST commit. Asking for the last one makes any later edit to
    the document - a redaction, a typo, a broken link - move it forward past
    its own results, and the tool then calls a correctly pre-registered study a
    write-up. That happened here, to a real pre-registration, and it was the
    tool that was wrong.

    `first=False` gives the last-touched time, which is the right question for
    "was the plan modified after the results were known".
    """
    d = os.path.dirname(os.path.abspath(path)) or "."
    base = os.path.basename(path)
    if first:
        out = _git(["log", "--diff-filter=A", "--format=%ct", "--", base], d)
        if out:
            return int(out.splitlines()[-1])
        # no add recorded (a filtered or grafted history): fall back to the
        # oldest commit that touches it, and say nothing more confident
        out = _git(["log", "--format=%ct", "--", base], d)
        return int(out.splitlines()[-1]) if out else None
    out = _git(["log", "-1", "--format=%ct", "--", base], d)
    return int(out) if out and out.isdigit() else None


def sections(text):
    found = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            cur = m.group(1)
            found[cur] = []
        elif cur is not None:
            found[cur].append(line)
    return {k: "\n".join(v) for k, v in found.items()}


def _filled(body):
    """Section content with HTML comments and blank lines removed."""
    return re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()


def cmd_new(a):
    if os.path.exists(a.path) and not a.force:
        sys.exit(f"{a.path} exists; pass --force to overwrite")
    import datetime
    when = a.when or datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    os.makedirs(os.path.dirname(os.path.abspath(a.path)), exist_ok=True)
    with open(a.path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE.format(title=a.title, when=when))
    print(f"wrote {a.path}")
    print("Fill every section, then: groundwork prereg seal " + a.path)
    print("Commit it BEFORE the run. `verify` checks that with git and there is")
    print("no flag to turn that off.")
    return 0


def cmd_seal(a):
    digest = sha256_of(a.path)
    out = a.out or (os.path.splitext(a.path)[0] + ".sha256")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"{digest}  {os.path.basename(a.path)}\n")
    print(f"{digest}  {os.path.basename(a.path)}")
    print(f"wrote {out}")
    return 0


def cmd_verify(a):
    problems, notes = [], []
    text = open(a.path, encoding="utf-8").read()

    seal = a.seal or (os.path.splitext(a.path)[0] + ".sha256")
    if os.path.exists(seal):
        want = open(seal, encoding="utf-8").read().split()[0]
        got = sha256_of(a.path)
        if got != want:
            problems.append(f"the document has changed since it was sealed\n"
                            f"      sealed {want}\n      now    {got}")
        else:
            notes.append(f"hash matches {seal}")
    else:
        problems.append(f"no seal at {seal} - run `prereg seal` and commit it")

    have = sections(text)
    for name, why in REQUIRED:
        match = next((k for k in have if k.lower().startswith(name.lower()[:18])), None)
        if match is None:
            problems.append(f"missing section {name!r} - {why}")
        elif not _filled(have[match]):
            problems.append(f"section {name!r} is still the template - {why}")
    if have:
        notes.append(f"{len(have)} sections, all filled in"
                     if not any("section" in p for p in problems) else f"{len(have)} sections")

    pre_t = committed_at(a.path)
    pre_last = committed_at(a.path, first=False)
    if pre_t is None:
        problems.append(f"{a.path} is not committed - a pre-registration that exists only in a "
                        "working tree can be edited with no trace")
    for res in a.results or []:
        if not os.path.exists(res):
            problems.append(f"{res} does not exist")
            continue
        res_t = committed_at(res)
        stamp = res_t if res_t is not None else int(os.path.getmtime(res))
        how = "committed" if res_t is not None else "last modified"
        if pre_t is not None and stamp < pre_t:
            problems.append(
                f"{res} was {how} BEFORE the pre-registration was committed "
                f"({stamp} < {pre_t}). A pre-registration written after its results is a "
                f"write-up.")
        elif pre_t is not None:
            notes.append(f"{res} {how} {(stamp - pre_t) / 60:.0f} min after the pre-registration")
            if pre_last is not None and pre_last > stamp:
                notes.append(
                    f"{a.path} was edited {(pre_last - stamp) / 60:.0f} min AFTER "
                    f"{res} - the order is still right, and the seal above is what says "
                    "the plan itself did not change")

    for n in notes:
        print(f"  ok   {n}")
    for p in problems:
        print(f"  FAIL {p}")
    print()
    if problems:
        print(f"{len(problems)} problem(s). This is not a pre-registration yet.")
        return 1
    print("Sealed, complete, and committed before the results it governs.")
    print("What it cannot check: whether the analysis you pre-stated is the one")
    print("that answers the question. Nothing mechanical can.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork prereg")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="scaffold a pre-registration")
    n.add_argument("path")
    n.add_argument("--title", default="an experiment")
    n.add_argument("--when")
    n.add_argument("--force", action="store_true")
    n.set_defaults(func=cmd_new)
    s = sub.add_parser("seal", help="hash it")
    s.add_argument("path")
    s.add_argument("--out")
    s.set_defaults(func=cmd_seal)
    v = sub.add_parser("verify", help="hash, sections, and commit order against the results")
    v.add_argument("path")
    v.add_argument("--seal")
    v.add_argument("--results", nargs="*", help="result files this pre-registration governs")
    v.set_defaults(func=cmd_verify)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
