#!/usr/bin/env python3
"""Attach the stages to whichever agent you use.

    groundwork install                 # Claude Code, into ./.claude/skills
    groundwork install --agent codex   # print what to run
    groundwork install --list          # the stages and what each decides

The stages are plain Markdown, so "installing" them means putting them where
your agent looks. Nothing is copied: they are linked, so updating this
repository updates every project that points at it.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Shipped INSIDE the package, so `groundwork install` works after a plain
# pip install. A stranger who cloned, installed and then ran it from a
# project directory could not find them when they lived at the repo root -
# and that is the one command whose whole job is to attach the pipeline.
_CANDIDATES = [os.path.join(HERE, "skills"),
               os.path.join(os.path.dirname(HERE), "skills")]
SKILLS = next((p for p in _CANDIDATES if os.path.isdir(p)), None)


def stages():
    if not SKILLS:
        return []
    out = []
    for d in sorted(glob.glob(os.path.join(SKILLS, "*/"))):
        main = os.path.join(d, "SKILL.md")
        if not os.path.exists(main):
            continue
        head = open(main, encoding="utf-8").read()
        m = re.search(r"^# (.+)$", head, re.M)
        notes = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(d, "*.md")))
                 if not f.endswith("SKILL.md")]
        out.append((os.path.basename(d.rstrip("/")), m.group(1) if m else "", d, notes))
    return out


def cmd_list():
    for name, title, _d, notes in stages():
        print(f"  {name:<14} {title}")
        if notes:
            print(f"                 {len(notes)} note(s): " + ", ".join(n[:-3] for n in notes))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork install")
    ap.add_argument("--agent", default="claude", choices=["claude", "codex", "other"])
    ap.add_argument("--dir", default=".", help="the project to attach them to")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)

    if SKILLS is None:
        print("cannot find the skills directory. Run this from a clone, or clone the\n"
              "repository - the stages are Markdown and are not shipped inside the wheel.")
        return 2
    if a.list:
        return cmd_list()

    if a.agent == "claude":
        target = os.path.join(os.path.abspath(a.dir), ".claude", "skills")
        os.makedirs(target, exist_ok=True)
        n = 0
        for name, _t, d, _notes in stages():
            link = os.path.join(target, f"groundwork-{name}")
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link) if os.path.islink(link) else None
            if not os.path.exists(link):
                os.symlink(os.path.abspath(d.rstrip("/")), link)
                n += 1
        print(f"linked {n} stage(s) into {target}")
        print("\nThey update when this repository does, because they are links rather")
        print("than copies. Ask for a stage by name, or run the tools directly.")
        return 0

    if a.agent == "codex":
        print("Codex CLI reads a file as the session's instructions:\n")
        for name, title, d, _n in stages():
            print(f"  codex exec --skip-git-repo-check < {os.path.join(d, 'SKILL.md')}"
                  f"   # {title[:46]}")
        print("\n`exec` starts a fresh session, which is what you want for a stage that")
        print("is meant to judge rather than continue.")
        return 0

    print("Any agent that reads Markdown: the stage file is the instruction, and the")
    print("tools are shell commands. Point it at:\n")
    for name, title, d, _n in stages():
        print(f"  {os.path.join(d, 'SKILL.md')}   # {title[:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
