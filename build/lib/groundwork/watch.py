#!/usr/bin/env python3
"""Launch a long run and keep watching it after the session that started it ends.

The three things that go wrong with an overnight run, in the order they bite:

1. **It dies with the terminal.** So it is launched detached.
2. **It was never alive.** A job that fails to load its weights looks identical
   at launch to one that is training. So this waits, checks the process is still
   there, and prints the head of the log where the configuration is echoed - a
   run with a wrong flag looks exactly like a run with the right one until it
   finishes.
3. **Nobody looks again.** A watch set up *inside* an agent session dies with
   that session, and its silence is indistinguishable from "nothing has
   happened". One such watch went unread for forty hours.

So the durable part is a **flag file**. `watch` writes one when the run ends,
with the verdict in it, and prints the line to put in the project notes. An
agent reads a file; it does not remember an intention.

    groundwork watch start --name run1 -- python train.py --epochs 30
    groundwork watch status
    groundwork watch status --wait          # block until it ends
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time

DIR = os.path.join("archive", "runs")
ALIVE_AFTER = 90          # seconds; long enough for weights to fail to load


def _paths(name):
    return (os.path.join(DIR, f"{name}.json"),
            os.path.join(DIR, f"{name}.log"),
            os.path.join(DIR, f"{name}.DONE"))


def _read(name):
    meta, _log, _flag = _paths(name)
    with open(meta, encoding="utf-8") as fh:
        return json.load(fh)


def _running(pid):
    """Is this pid a process that is still doing something?

    `os.kill(pid, 0)` succeeds for a process that has exited and not been
    reaped, so a job that died a second after launch reported as alive - the
    exact failure this tool exists to catch, produced by the tool itself.
    A zombie is not running.
    """
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
            # the state letter is the field after the comm field, which may
            # itself contain spaces and is parenthesised
            state = fh.read().rsplit(")", 1)[1].split()[0]
        return state != "Z"
    except OSError:
        return True          # no procfs: fall back to the signal test


def cmd_start(a):
    if not a.command:
        print("nothing to run. Put the command after `--`.", file=sys.stderr)
        return 2
    os.makedirs(DIR, exist_ok=True)
    meta_p, log_p, flag_p = _paths(a.name)
    if os.path.exists(meta_p) and not a.force:
        print(f"{meta_p} exists; pass --force to start over")
        return 1
    for p in (flag_p,):
        if os.path.exists(p):
            os.remove(p)

    cmd = " ".join(shlex.quote(c) for c in a.command)
    with open(log_p, "w") as log:
        proc = subprocess.Popen(cmd, shell=True, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)   # Popen dups the fd
    meta = {"name": a.name, "pid": proc.pid, "command": cmd,
            "started": datetime.datetime.now().astimezone().isoformat(),
            "log": log_p, "flag": flag_p}
    with open(meta_p, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    print(f"started {a.name} (pid {proc.pid})\n  {cmd}\n  log: {log_p}")

    # 2 - confirm it is alive AFTER it has had time to fail
    wait = a.alive_after
    print(f"\nwaiting {wait}s before believing it started...")
    time.sleep(wait)
    if proc.poll() is not None or not _running(proc.pid):
        print(f"\nIT IS ALREADY GONE (exit {proc.returncode}). The head of its log:\n")
        print(_head(log_p))
        _flag(flag_p, meta, "died-before-" + str(wait) + "s")
        return 1
    head = _head(log_p)
    print("still alive. The head of the log, where the configuration is echoed:\n")
    print(head)
    if "(nothing yet)" in head:
        print("""
  Nothing has reached the log. Usually that is BUFFERING, not silence: a
  process whose output is not a terminal buffers it, so a run that is working
  looks identical to one that has produced nothing - and a crash then loses
  everything that was in the buffer. Relaunch with unbuffered output:

      PYTHONUNBUFFERED=1 groundwork watch start --name NAME -- <command>

  or make the harness flush after every record it writes.""")
    print(f"""
Now make it durable. This watch ends with this shell; the flag file does not:

  echo 'first thing on resuming: check {flag_p}' >> PROJECT.md

and, if you want to be told rather than to remember:

  (while kill -0 {proc.pid} 2>/dev/null; do sleep 300; done; \\
   groundwork watch status --name {a.name}) &
""")
    return 0


def _head(path, n=20):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return "".join(f"  | {ln}" for ln in fh.readlines()[:n]) or "  | (nothing yet)"
    except OSError:
        return "  | (no log)"


def _tail(path, n=12):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return "".join(f"  | {ln}" for ln in fh.readlines()[-n:]) or "  | (empty)"
    except OSError:
        return "  | (no log)"


def _flag(path, meta, verdict, extra=None):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({**meta, "verdict": verdict,
                   "ended": datetime.datetime.now().astimezone().isoformat(),
                   **(extra or {})}, fh, indent=1)


TROUBLE = re.compile(r"Traceback|CUDA out of memory|OutOfMemory|Killed|"
                     r"^\s*assert|Segmentation fault|NaN|nan\b", re.M)


def cmd_status(a):
    names = [a.name] if a.name else sorted(
        f[:-5] for f in os.listdir(DIR) if f.endswith(".json")) if os.path.isdir(DIR) else []
    if not names:
        print(f"no runs recorded under {DIR}/")
        return 1
    rc = 0
    for name in names:
        meta_p, log_p, flag_p = _paths(name)
        if not os.path.exists(meta_p):
            print(f"{name}: no record")
            rc = 1
            continue
        meta = _read(name)
        while True:
            alive = _running(meta["pid"])
            if alive and a.wait:
                time.sleep(a.interval)
                continue
            break
        size = os.path.getsize(log_p) if os.path.exists(log_p) else 0
        trouble = False
        if os.path.exists(log_p):
            with open(log_p, encoding="utf-8", errors="replace") as fh:
                trouble = bool(TROUBLE.search(fh.read()[-40000:]))
        state = "running" if alive else "ended"
        print(f"{name}: {state}  pid {meta['pid']}  log {size / 1024:.0f} KB"
              + ("   TROUBLE IN THE LOG" if trouble else ""))
        print(f"  {meta['command']}")
        print(_tail(log_p))
        if not alive:
            verdict = "trouble-in-log" if trouble else "ended"
            _flag(flag_p, meta, verdict)
            print(f"  wrote {flag_p} ({verdict})")
            if trouble:
                rc = 1
        if trouble:
            print("\n  A run is finished when its output has been SCORED and the numbers\n"
                  "  are on disk, not when the process exited. Check before writing any\n"
                  "  sentence about it.")
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork watch")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="launch detached, confirm it is alive, read the log head")
    s.add_argument("--name", required=True)
    s.add_argument("--alive-after", type=int, default=ALIVE_AFTER)
    s.add_argument("--force", action="store_true")
    s.add_argument("command", nargs=argparse.REMAINDER,
                   help="the command, after --")
    s.set_defaults(func=cmd_start)
    t = sub.add_parser("status", help="what happened, and write the flag file")
    t.add_argument("--name")
    t.add_argument("--wait", action="store_true", help="block until it ends")
    t.add_argument("--interval", type=int, default=60)
    t.set_defaults(func=cmd_status)
    a = ap.parse_args(argv)
    if getattr(a, "command", None) and a.command and a.command[0] == "--":
        a.command = a.command[1:]
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
