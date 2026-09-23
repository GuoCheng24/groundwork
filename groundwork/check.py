#!/usr/bin/env python3
"""Run every gate this project is subject to, and say which ones do not apply.

The gates in this repository each catch one thing, and each of them has been
skipped at least once because nobody remembered it existed at the moment it was
relevant. `check` walks a project and runs all of them.

The design decision that matters is the third verdict. A check over a project
with no pre-registrations must not print a green tick: a check that passes
because there was **nothing to check** has told you the opposite of the truth.
So there are three outcomes, and `n/a` is printed as loudly as `fail`:

    ok    the thing was there and it was right
    FAIL  the thing was there and it was wrong
    n/a   there was nothing to check - which may be the finding

    groundwork check                 # this directory
    groundwork check --dir ../other
    groundwork check --json

Exit code is non-zero if anything failed. `n/a` does not fail: it reports.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

from . import prereg

OK, FAIL, NA, WAIVED = "ok", "FAIL", "n/a", "waived"

# A gate that genuinely does not apply to a project can be waived - in a file,
# with a reason, and the waived row is printed exactly as loudly as the others.
# A flat allow-list that only says "skip this" is how a repository disarms its
# own checks: an exemption written for one document silently exempted a second
# one that was deliberately broken, and the step asserting failure started
# passing. So a waiver names the check AND gives a reason, and the reason is
# shown every time.
WAIVERS = os.path.join("archive", "waivers.json")

# Anything that should never reach a public repository. Each is a pattern plus
# what it would leak; all of these have been found in a tracked file at least
# once, which is why the list is short and specific rather than a regex zoo.
PRIVATE = [
    (r"/(?:public|home|Users)/[a-z][a-z0-9_.-]{2,}/", "an absolute home path, which names the account"),
    (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "a session id"),
    (r"\b[A-Za-z0-9._%+-]+@(?!example\.|.*\.invalid)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
     "an email address"),
    (r"\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}\b", "a GitHub token"),
    (r"\bpypi-[A-Za-z0-9_-]{16,}\b", "a PyPI token"),
]
# What counts as private is partly project-specific: a cluster's node names, an
# internal ticket prefix, a collaborator's initials. A project declares its own
# in archive/private-patterns.json, and `check` reports how many patterns it
# applied - so a file that is missing or empty reads as a narrower scan rather
# than as a clean one.
#
# The patterns file is scanned like every other file, deliberately - writing the
# secret itself in there instead of a regex is the obvious mistake, and a scan
# that skipped its own configuration would be the one place it could hide. What
# IS removed before scanning is the `regex` values themselves: a pattern written
# to match another account's directory contains that directory's prefix by
# construction, and a scanner that flags its own rules teaches you to turn it
# off.
PATTERNS_FILE = os.path.join("archive", "private-patterns.json")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
TEXT_EXT = {".md", ".py", ".sh", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg", ".tex"}


def _git(args, cwd):
    try:
        p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=20)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _tracked(root):
    """Files git would carry: tracked, plus untracked-and-not-ignored.

    Scanning only tracked files passes right up to the moment you `git add`,
    which is the moment the scan exists for. Ignored files stay out - that is
    what .gitignore is for, and a scan that shouted about a 30 GB generations
    file would be turned off.
    """
    out = _git(["ls-files"], root)
    if out is None:
        return None
    files = [f for f in out.splitlines() if f]
    new = _git(["ls-files", "--others", "--exclude-standard"], root)
    if new:
        files += [f for f in new.splitlines() if f]
    return files


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield os.path.join(dirpath, f)


# ---------------------------------------------------------------- the checks

def check_gate(root):
    doc = os.path.join(root, "PROJECT.md")
    if not os.path.exists(doc):
        return NA, "no PROJECT.md, so no recorded gate", "groundwork init --name ..."
    with open(doc, encoding="utf-8") as fh:
        secs = prereg.sections(fh.read())
    gate = next((v for k, v in secs.items() if "gate" in k.lower()), None)
    if gate is None:
        return NA, "PROJECT.md has no gate section", "groundwork init writes one, first"
    if not prereg._filled(gate):
        if _has_results(root):
            return (FAIL, "the gate section is empty and results already exist",
                    "the gate is decided before the first real experiment, not after")
        return (NA, "the gate section is there and empty, and nothing has run yet",
                "groundwork gate --baseline ... --oracle ... --se ...")
    if not re.search(r"\d", gate):
        # `groundwork init` writes this section as a template, on purpose. A
        # template is not a filled section, and calling a freshly scaffolded
        # project a failure teaches people to ignore the sweep on day one.
        if _has_results(root):
            return (FAIL, "results exist and the gate section still has no numbers in it",
                    "a ceiling and a baseline are numbers; a sentence is not a gate")
        return (NA, "the gate section is still the template, and nothing has run yet",
                "groundwork gate --baseline ... --oracle ... --se ...")
    return OK, "the gate is recorded, with numbers", ""


def _has_results(root):
    return any(glob.glob(os.path.join(root, p))
               for p in ("results/*.json", "results/*.md", "results/*/*.json"))


def _seal_for(path, text):
    """Find the seal, wherever it was put.

    A seal has to be **outside** the document: a file cannot contain its own
    digest. So a sha256 appearing in the text is a digest of something else -
    the dataset, the scorer, the pre-registration this one amends - and taking
    it as a self-seal passes an unsealed plan. It did, here, until the sweep
    was checked against a document whose inline digest belonged to its
    predecessor.

    Two places are valid: the sidecar `prereg seal` writes, and a quotation in
    a later document that names this file. The second is the stronger one.
    """
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0].lower()
    d = os.path.dirname(os.path.abspath(path)) or "."
    for cand in os.listdir(d):
        if cand.lower().endswith(".sha256") and \
                os.path.splitext(cand)[0].lower().lstrip("_-") in (stem, stem.lstrip("_-")):
            return os.path.join(d, cand)
    # A seal can live in a later document. An amendment that opens by naming
    # the plan it amends and quoting its digest has sealed it more strongly
    # than a sidecar does: the reference is in the record next to the reason.
    digest = _sha256(path)
    for cand in sorted(os.listdir(d)):
        c = os.path.join(d, cand)
        if not cand.lower().endswith(".md") or os.path.samefile(c, path):
            continue
        try:
            with open(c, encoding="utf-8", errors="replace") as fh:
                other = fh.read(200_000)
        except OSError:
            continue
        for m in re.finditer(r"\b[0-9a-f]{64}\b", other):
            window = other[max(0, m.start() - 300):m.end() + 300]
            if base in window and m.group(0) == digest:
                return f"quoted in {cand}"
    return None


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def check_prereg(root):
    files = sorted(glob.glob(os.path.join(root, "prereg", "PREREG*.md")))
    if not files:
        if _has_results(root):
            return (FAIL, "results exist and there is no pre-registration",
                    "groundwork prereg new prereg/PREREG_x.md, before the next run")
        return (NA, "no pre-registration in prereg/ yet",
                "groundwork prereg new prereg/PREREG_run1.md")
    bad, unjudged = [], []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        if not _seal_for(f, text):
            bad.append(f"{os.path.basename(f)}: no seal - "
                       f"groundwork prereg seal {os.path.relpath(f, root)}")
            continue
        secs = prereg.sections(text)
        named = {n for n, _w in prereg.REQUIRED
                 if any(n.lower() in k.lower() for k in secs)}
        if len(named) < 4:
            # Written to another template. Whether its prose answers the six
            # questions is not something a name match can decide - and deciding
            # it anyway produces accusations against documents that do answer
            # them, in words the matcher does not know. See CLAIMS below.
            unjudged.append(f"{os.path.basename(f)} ({len(secs)} sections, other template)")
            continue
        empty = [n for n, _w in prereg.REQUIRED
                 if any(n.lower() in k.lower() for k in secs)
                 and not prereg._filled(next(v for k, v in secs.items() if n.lower() in k.lower()))]
        if empty:
            bad.append(f"{os.path.basename(f)}: section(s) present but empty: "
                       + ", ".join(empty))
        elif len(named) < len(prereg.REQUIRED):
            bad.append(f"{os.path.basename(f)}: no section named "
                       + ", ".join(f"'{n}'" for n, _w in prereg.REQUIRED if n not in named))
    if bad:
        return FAIL, "; ".join(bad[:3]), "groundwork prereg verify <file> --results <results>"
    if unjudged and len(unjudged) == len(files):
        return (NA, f"{len(unjudged)} sealed pre-registration(s), none written to this "
                f"template: {', '.join(unjudged[:2])}",
                "whether their prose answers the six questions is not a name match. "
                "Read them, or ask one by one: groundwork prereg verify <file>")
    msg = f"{len(files) - len(unjudged)} sealed pre-registration(s), every required section filled"
    if unjudged:
        msg += f"; {len(unjudged)} written to another template and not judged by name"
    return OK, msg, ""


def _tag(prereg_path):
    """`prereg/PREREG_run3_addendum_3d.md` -> `run3`.

    The tag is how a pre-registration says which results it governs. Without
    one, a sweep ends up comparing a plan for run 3 against an environment
    dump committed during run 1 and calling the plan a write-up - an
    accusation made about a file the plan never mentioned.
    """
    base = os.path.basename(prereg_path)
    base = re.sub(r"^PREREG[_-]?", "", base, flags=re.I)
    base = os.path.splitext(base)[0]
    return base.split("_")[0] if base else ""


def check_prereg_order(root):
    """Version control, not the document, decides which came first.

    Compares first-commit times: asking when a file was *last* touched makes a
    later redaction move a pre-registration past its own results.
    """
    files = sorted(glob.glob(os.path.join(root, "prereg", "PREREG*.md")))
    if not files or _tracked(root) is None:
        return NA, "no pre-registration under version control", ""
    results = [r for r in glob.glob(os.path.join(root, "results", "**", "*"), recursive=True)
               if os.path.isfile(r)]
    late, checked, unassociated = [], 0, []
    for f in files:
        tag = _tag(f)
        mine = [r for r in results if tag and tag.lower() in os.path.basename(r).lower()]
        if not mine:
            unassociated.append(f"{os.path.basename(f)} (tag {tag!r})")
            continue
        t_pre = prereg.committed_at(f)
        if t_pre is None:
            late.append(f"{os.path.basename(f)}: never committed")
            continue
        for r in mine:
            t_res = prereg.committed_at(r)
            if t_res is not None and t_res < t_pre:
                late.append(f"{os.path.basename(f)} entered the record after "
                            f"results/{os.path.relpath(r, os.path.join(root, 'results'))}")
                break
        checked += 1
    if late:
        return FAIL, "; ".join(late[:3]), \
            "a pre-registration committed after its results it governs is a write-up"
    if not checked:
        return NA, ("no results could be matched to a pre-registration by name: "
                    + ", ".join(unassociated[:3])), \
            "name results after the run their pre-registration names, or pass them " \
            "explicitly: groundwork prereg verify <prereg> --results <file>"
    msg = f"{checked} pre-registration(s) entered the record before the results they govern"
    if unassociated:
        msg += f"; {len(unassociated)} had no matching results and were not judged"
    return OK, msg, ""


def check_noise(root):
    """A difference smaller than the instrument is not a finding about the arms."""
    have = glob.glob(os.path.join(root, "results", "*noise*.json")) + \
        glob.glob(os.path.join(root, "results", "*", "*noise*.json"))
    if have:
        return OK, f"a scorer-noise measurement is on disk ({os.path.basename(have[0])})", ""
    if not _has_results(root):
        return NA, "no results yet, so nothing is being compared", ""
    return FAIL, "results are being compared with no measured noise floor", \
        "groundwork noise --n 10 --command '<your scorer>'  - ten scorings of one " \
        "unchanged file spanned 0.37 points here, and three runs had said it was stable"


def check_runs(root):
    """A run whose process is gone but whose flag says running is a run nobody read."""
    d = os.path.join(root, "archive", "runs")
    metas = sorted(glob.glob(os.path.join(d, "*.json")))
    if not metas:
        return NA, "no runs recorded under archive/runs/", "groundwork watch start ..."
    unread, trouble = [], []
    for m in metas:
        name = os.path.basename(m)[:-5]
        flag = os.path.join(d, name + ".DONE")
        if os.path.exists(flag):
            with open(flag, encoding="utf-8") as fh:
                v = json.load(fh).get("verdict", "")
            if v != "ended":
                trouble.append(f"{name}: {v}")
            continue
        with open(m, encoding="utf-8") as fh:
            pid = json.load(fh).get("pid")
        try:
            os.kill(int(pid), 0)
        except (OSError, TypeError, ValueError):
            unread.append(name)
    if trouble:
        return FAIL, "run(s) ended badly: " + "; ".join(trouble[:3]), \
            "read the log before writing any sentence about the run"
    if unread:
        return (FAIL, "run(s) whose process is gone and whose end was never recorded: "
                + " ".join(unread[:4]), "groundwork watch status")
    return OK, f"{len(metas)} run(s) recorded, all accounted for", ""


def check_ledger(root):
    f = os.path.join(root, "archive", "killed.json")
    if not os.path.exists(f):
        return NA, "nothing has been killed yet, or nothing was written down", \
            "groundwork ledger kill --id ... --cause ...  - a direction that dies " \
            "unrecorded gets re-opened"
    with open(f, encoding="utf-8") as fh:
        rows = json.load(fh)
    rows = rows.get("killed", rows) if isinstance(rows, dict) else rows
    free = [r.get("id", "?") for r in rows if not r.get("cause")]
    if free:
        return FAIL, f"{len(free)} entry/entries with no cause from the taxonomy", \
            "a cause that is free text cannot be counted, so it teaches nothing"
    return OK, f"{len(rows)} recorded death(s), each with a cause", ""


def check_raw_gitignored(root):
    gi = os.path.join(root, ".gitignore")
    raw = [f for f in glob.glob(os.path.join(root, "results", "**", "*.jsonl"), recursive=True)]
    tracked = _tracked(root)
    if tracked is None:
        return NA, "not a git repository", ""
    if not raw:
        return NA, "no raw generation files to worry about", ""
    big = [f for f in raw if os.path.getsize(f) > 5_000_000]
    rel = {os.path.relpath(f, root) for f in big}
    leaked = sorted(rel & set(tracked))
    if leaked:
        return FAIL, f"{len(leaked)} raw generation file(s) tracked: {leaked[0]}", \
            "track the scored table, not the generations; " \
            "a repository that carries them stops being clonable"
    if not os.path.exists(gi):
        return FAIL, "raw generations exist and there is no .gitignore", "groundwork init writes one"
    return OK, f"{len(raw)} raw file(s), none of the large ones tracked", ""


def _without_rules(text):
    """The patterns file with its own `regex` values blanked out."""
    try:
        d = json.loads(text)
    except ValueError:
        return text
    for row in d.get("patterns", []):
        row.pop("regex", None)
    return json.dumps(d, indent=1)


def project_patterns(root):
    """Extra patterns this project declares. Returns (patterns, problems)."""
    f = os.path.join(root, PATTERNS_FILE)
    if not os.path.exists(f):
        return [], []
    try:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError) as exc:
        return [], [f"{PATTERNS_FILE} could not be read ({exc}); no project patterns applied"]
    out, bad = [], []
    for row in d.get("patterns", []):
        rx, what = row.get("regex"), row.get("what")
        if not rx or not what:
            bad.append(f"{PATTERNS_FILE}: an entry with no regex or no description")
            continue
        try:
            re.compile(rx)
        except re.error as exc:
            bad.append(f"{PATTERNS_FILE}: {rx!r} is not a regex ({exc})")
            continue
        out.append((rx, what))
    return out, bad


def check_private(root):
    tracked = _tracked(root)
    in_git = tracked is not None
    files = [os.path.join(root, f) for f in tracked] if in_git else \
        [f for f in _walk(root) if os.path.splitext(f)[1] in TEXT_EXT]
    extra, pattern_problems = project_patterns(root)
    patterns = PRIVATE + extra
    hits = list(pattern_problems)
    for f in files:
        if os.path.splitext(f)[1] not in TEXT_EXT or not os.path.exists(f):
            continue
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read(400_000)
        except OSError:
            continue
        if os.path.abspath(f) == os.path.abspath(os.path.join(root, PATTERNS_FILE)):
            text = _without_rules(text)
        found = []
        for pat, what in patterns:
            m = re.search(pat, text)
            if m:
                line = text[:m.start()].count("\n") + 1
                found.append(f"{os.path.relpath(f, root)}:{line} {what}")
        # all of them, not the first: a file that leaks a node name and an
        # internal address has two problems, and fixing the one that happened
        # to sort first leaves the report looking the same next run
        hits += found
    what = "file(s) git would carry" if in_git else "file(s) in the working tree (not a git repository)"
    how = (f"{len(patterns)} pattern(s): {len(PRIVATE)} built in"
           + (f" + {len(extra)} declared in {PATTERNS_FILE}" if extra
              else f", none declared in {PATTERNS_FILE}"))
    if not files:
        return NA, f"no {what} to scan", ""
    if hits:
        more = f" (+{len(hits) - 3} more)" if len(hits) > 3 else ""
        return FAIL, f"{len(hits)} finding(s): " + "; ".join(hits[:3]) + more, \
            "redact before pushing; git history keeps what a later commit removes"
    return OK, f"{len(files)} {what} scanned against {how}; nothing found", \
        ("" if extra else
         "what counts as private is partly project-specific - a node name, a "
         f"ticket prefix, initials. Declare them in {PATTERNS_FILE}")


def check_skills(root):
    d = os.path.join(root, ".claude", "skills")
    if not os.path.isdir(d):
        return NA, "the stages are not attached to an agent here", "groundwork install"
    linked = [n for n in os.listdir(d) if n.startswith("groundwork-")]
    if len(linked) < 7:
        return FAIL, f"only {len(linked)} of the stages are attached", "groundwork install"
    return OK, f"{len(linked)} stages attached", ""


CHECKS = [
    ("gate", "is there a recorded ceiling and baseline", check_gate),
    ("prereg", "is every pre-registration sealed and complete", check_prereg),
    ("prereg-order", "did version control see the plan before the results", check_prereg_order),
    ("noise", "is the instrument's spread measured before differences are quoted", check_noise),
    ("runs", "did every long run get read", check_runs),
    ("ledger", "is every dead direction recorded with a countable cause", check_ledger),
    ("raw-data", "are raw generations kept out of the repository", check_raw_gitignored),
    ("private", "is anything private about to be pushed", check_private),
    ("skills", "are the stages attached to the agent working here", check_skills),
]


def waivers(root):
    f = os.path.join(root, WAIVERS)
    if not os.path.exists(f):
        return {}
    try:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    d = d.get("waived", d) if isinstance(d, dict) else {}
    return {k: v for k, v in d.items() if isinstance(v, str) and v.strip()}


def run(root):
    out = []
    waived = waivers(root)
    for name, question, fn in CHECKS:
        try:
            verdict, detail, fix = fn(root)
        except Exception as exc:                       # a broken check is not a pass
            verdict, detail, fix = FAIL, f"the check itself raised {exc!r}", \
                "fix the check before trusting the sweep"
        if verdict == FAIL and name in waived:
            verdict, detail, fix = WAIVED, waived[name], ""
        out.append({"check": name, "question": question, "verdict": verdict,
                    "detail": detail, "fix": fix})
    return out


def report(rows, root):
    L = [f"{os.path.abspath(root)}", ""]
    for r in rows:
        mark = {OK: "ok  ", FAIL: "FAIL", NA: "n/a ", WAIVED: "waiv"}[r["verdict"]]
        L.append(f"  {mark}  {r['check']:<13} {r['detail']}")
        if r["fix"] and r["verdict"] != OK:
            L.append(f"        {' ' * 13} -> {r['fix']}")
    n_fail = sum(1 for r in rows if r["verdict"] == FAIL)
    n_na = sum(1 for r in rows if r["verdict"] == NA)
    n_w = sum(1 for r in rows if r["verdict"] == WAIVED)
    L.append("")
    L.append(f"  {len(rows) - n_fail - n_na - n_w} ok, {n_fail} failed, "
             f"{n_na} not applicable"
             + (f", {n_w} waived" if n_w else ""))
    if n_w:
        L.append("")
        L.append(f"  A waiver is a claim, written down in {WAIVERS} and printed here every")
        L.append("  time. If the reason above has stopped being true, the waiver is a lie")
        L.append("  the sweep now repeats for you.")
    if n_na:
        L.append("")
        L.append("  `n/a` is not a pass. It means the gate had nothing to look at, which")
        L.append("  for a project that is under way is usually the finding, not the relief.")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork check",
                                 description="run every gate over a project; n/a is not a pass")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = run(a.dir)
    print(json.dumps(rows, indent=1) if a.json else report(rows, a.dir))
    return 1 if any(r["verdict"] == FAIL for r in rows) else 0


if __name__ == "__main__":      # pragma: no cover
    sys.exit(main())
