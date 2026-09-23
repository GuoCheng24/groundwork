#!/usr/bin/env python3
"""What this machine can actually do — measured, not assumed.

An agent that lands on an unfamiliar node plans its work from assumptions, and
the assumptions are usually wrong in the same three ways:

1. **`which X` says nothing, so X is declared unavailable.** LibreOffice was
   installed on this machine the whole time, eight directories deep under a
   shared mount that was not on `PATH`; two sessions worked around its absence
   before anyone looked. A negative from `which` is a statement about `PATH`,
   not about the machine. On a cluster the real catalogue is usually the module
   system, which answers in a second - while a filesystem crawl over a shared
   mount does not finish at all, and an unfinished crawl is not an absence.
2. **"No root, so no containers."** Unprivileged user namespaces, `bwrap` and
   `fuse-overlayfs` were all available to an ordinary user here. That single
   measurement reopened a direction that had been written off.
3. **Free memory is read off the wrong number.** `/dev/shm` is memory: a
   dataloader that fills it is using RAM that `free` will happily show as
   cached. And when the kernel runs out, the OOM killer names the *last*
   process to allocate, not the one holding the most — so the name in `dmesg`
   is usually not the culprit.

    groundwork probe                    everything, as a report
    groundwork probe --json             the same, machine-readable
    groundwork probe --tool pandoc --tool soffice     look for these too

Every negative in the output says where it looked, because a negative that does
not is not a measurement.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# The tools a research loop actually reaches for. Grouped by what breaks when
# the tool turns out to be missing *after* the plan depends on it.
WANTED = [
    ("git", "version control"),
    ("ssh", "reaching other nodes"),
    ("rsync", "moving results without re-running them"),
    ("nvidia-smi", "seeing the GPUs"),
    ("gcc", "building anything with a compiled extension"),
    ("ninja", "the JIT backends several inference stacks shell out to"),
    ("pandoc", "manuscript conversion"),
    ("tectonic", "LaTeX without a system TeX install"),
    ("latexmk", "LaTeX with one"),
    ("soffice", "rendering Word and PowerPoint to check the layout"),
    ("libreoffice", "the same thing under its other name"),
    ("gh", "GitHub without a browser"),
    ("jq", "reading JSON in a shell loop"),
]

# Where things get installed on a shared machine that are not on anyone's PATH.
# $HOME last: it is the slowest and the least likely.
ROOTS = ["/opt", "/usr/local", "/usr/lib", "/opt/software", "/share", "/apps"]
DEPTH = 8                   # a bundled install sits ~8 deep; depth is not the
                            # knob to economise on - the time budget is
SEARCH_BUDGET = 20          # seconds; a crawl of a shared mount will exceed it
PRUNE = (".git", "node_modules", "site-packages", "pkgs", ".cache", "__pycache__")


def _run(cmd, timeout=10):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except (subprocess.TimeoutExpired, OSError):
        return 124, "", "timeout"


def find_off_path(names, roots, budget=SEARCH_BUDGET, depth=None):
    """Look for executables that exist but are not on PATH.

    Returns (found, roots_searched, truncated). `truncated` matters: a search
    that ran out of time has not shown the tool is absent, and the report says
    so rather than printing a clean 'no'.
    """
    roots = [r for r in roots if os.path.isdir(r)]
    if not names or not roots:
        return {}, roots, False
    expr = " -o ".join(f"-name {n}" for n in names)
    prune = " -o ".join(f"-name {p}" for p in PRUNE)
    cmd = (f"find {' '.join(roots)} -maxdepth {depth or DEPTH} \\( {prune} \\) -prune -o "
           f"-type f \\( {expr} \\) -perm -u+x -print 2>/dev/null")
    rc, out, _ = _run(cmd, timeout=budget)
    found = {}
    for line in out.splitlines():
        found.setdefault(os.path.basename(line), []).append(line)
    return found, roots, rc == 124


def tools(extra=(), roots=None, budget=SEARCH_BUDGET, depth=None):
    seen = {n for n, _w in WANTED}
    wanted = list(WANTED) + [(t, "asked for on the command line")
                             for t in dict.fromkeys(extra) if t not in seen]
    on_path, missing = [], []
    for name, why in wanted:
        p = shutil.which(name)
        (on_path if p else missing).append((name, why, p))
    off, searched, truncated = find_off_path([n for n, _w, _p in missing],
                                             roots or ROOTS, budget, depth)
    return {"depth": depth or DEPTH,
            "on_path": [{"name": n, "path": p, "why": w} for n, w, p in on_path],
            "off_path": {n: v for n, v in off.items()},
            "absent": [n for n, _w, _p in missing if n not in off],
            "searched": searched, "truncated": truncated}


def _size(gb):
    return f"{gb / 1024:.0f} TB" if gb >= 1024 else f"{gb:.0f} GB"


def uncrawled_mounts(searched, min_gb=200):
    """Big mounts that the crawl did not cover.

    Reporting "not found" without saying that a two-terabyte shared mount was
    never looked at is the failure this whole command exists to prevent - so
    when the crawl skips one, the crawl says so.
    """
    skip_types = {"proc", "sysfs", "devtmpfs", "tmpfs", "devpts", "cgroup", "cgroup2",
                  "securityfs", "pstore", "bpf", "debugfs", "tracefs", "configfs",
                  "fusectl", "mqueue", "hugetlbfs", "autofs", "squashfs", "overlay",
                  "binfmt_misc", "rpc_pipefs", "selinuxfs"}
    out = []
    try:
        with open("/proc/mounts", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return out
    for line in lines:
        f = line.split()
        if len(f) < 3 or f[2] in skip_types:
            continue
        mp = f[1]
        if mp == "/" or any(mp == r or mp.startswith(r.rstrip("/") + "/") for r in searched):
            continue
        try:
            st = os.statvfs(mp)
        except OSError:
            continue
        size = st.f_blocks * st.f_frsize / 2**30
        if size >= min_gb:
            out.append({"path": mp, "size_gb": size})
    seen, uniq = set(), []
    for m in sorted(out, key=lambda x: -x["size_gb"]):
        if m["path"] in seen:       # one path, several mount entries
            continue
        seen.add(m["path"])
        uniq.append(m)
    return uniq[:6]


def _segment_match(entry, name):
    """`gcc` matches `compiler/gcc/11.3.0`, not `apps/amber/24-gcc-openmpi`.

    A substring match turns a catalogue into noise and hides the real hit
    underneath four false ones.
    """
    for seg in entry.lower().split("/"):
        if seg == name.lower() or re.match(rf"{re.escape(name.lower())}[^a-z]", seg):
            return True
    return False


def modules(names=()):
    """The software catalogue of an HPC cluster, which is deliberately not on PATH.

    `module avail` is how a cluster tells you what it has; `which` is how it
    tells you what your shell has. They are different questions, and asking the
    second one and reporting the first answer is how a machine with fifty
    installed toolchains gets described as bare.

    `module` is a shell function, not a binary, so this goes through a login
    shell. The listing is written to stderr.
    """
    rc, out, err = _run("module avail 2>&1", timeout=30)
    text = out + "\n" + err
    if rc != 0 or "not found" in text.lower() and "module" in text.lower()[:200]:
        return None
    entries = []
    for line in text.splitlines():
        if line.startswith("-") or not line.strip():
            continue
        entries += [tok for tok in line.split() if "/" in tok]
    hits = {}
    for n in dict.fromkeys(names):
        m = [e for e in entries if _segment_match(e, n)]
        if m:
            hits[n] = sorted(m)[:4]
    restricted = sorted({e for e in entries
                         if e.lower().startswith(("apps/anaconda", "anaconda"))})
    return {"count": len(entries), "hits": hits, "restricted": restricted,
            "sample": sorted(entries)[:8]}


def isolation():
    """Can this user build an isolated environment without root?

    "No root, so no containers" was wrong here, and the cost of believing it
    was a direction closed for a month.
    """
    out = {}
    rc, _o, _e = _run("unshare --user --map-root-user true")
    out["unprivileged_userns"] = (rc == 0)
    sysctl = "/proc/sys/kernel/unprivileged_userns_clone"
    if os.path.exists(sysctl):
        with open(sysctl, encoding="utf-8") as fh:
            out["userns_sysctl"] = fh.read().strip()
    for tool in ("bwrap", "fuse-overlayfs", "podman", "apptainer", "singularity", "proot"):
        out[tool] = shutil.which(tool) or None
    out["kvm"] = os.path.exists("/dev/kvm") and os.access("/dev/kvm", os.R_OK)
    deleg = "/sys/fs/cgroup/cgroup.subtree_control"
    out["cgroup_v2_delegated"] = os.access(deleg, os.W_OK) if os.path.exists(deleg) else False
    return out


def _meminfo():
    m = {}
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                k, _, v = line.partition(":")
                m[k] = int(v.split()[0]) / 1048576.0        # kB -> GiB
    except OSError:
        pass
    return m


def memory():
    m = _meminfo()
    shm = None
    try:
        st = os.statvfs("/dev/shm")
        shm = {"size_gb": st.f_blocks * st.f_frsize / 2**30,
               "used_gb": (st.f_blocks - st.f_bfree) * st.f_frsize / 2**30}
    except OSError:
        pass
    return {"total_gb": m.get("MemTotal"), "available_gb": m.get("MemAvailable"),
            "shm": shm, "cpus": os.cpu_count(),
            "loadavg": os.getloadavg() if hasattr(os, "getloadavg") else None}


def gpus():
    if not shutil.which("nvidia-smi"):
        return None
    rc, out, _ = _run("nvidia-smi --query-gpu=index,name,memory.used,memory.total,"
                      "utilization.gpu --format=csv,noheader,nounits", timeout=25)
    if rc != 0:
        return None
    cards = []
    for line in out.splitlines():
        f = [x.strip() for x in line.split(",")]
        if len(f) < 5:
            continue
        used, total = float(f[2]) / 1024, float(f[3]) / 1024
        cards.append({"index": int(f[0]), "name": f[1], "free_gb": total - used,
                      "total_gb": total, "util": int(f[4])})
    return cards


def disk(paths=(".", os.path.expanduser("~"), "/tmp")):
    out = []
    for p in dict.fromkeys(paths):
        try:
            st = os.statvfs(p)
        except OSError:
            continue
        out.append({"path": p, "free_gb": st.f_bavail * st.f_frsize / 2**30,
                    "size_gb": st.f_blocks * st.f_frsize / 2**30})
    return out


def collect(extra=(), roots=None, budget=SEARCH_BUDGET, depth=None):
    t = tools(extra, roots, budget, depth)
    t["uncrawled"] = uncrawled_mounts(t["searched"])
    return {"host": os.uname().nodename, "gpus": gpus(), "memory": memory(),
            "disk": disk(), "tools": t,
            "modules": modules(list(dict.fromkeys(t["absent"] + [n for n, _w in WANTED]))),
            "isolation": isolation()}


def report(d):
    L = []
    L.append(f"{d['host']}")
    g = d["gpus"]
    if g is None:
        L.append("  GPU        nvidia-smi did not answer - this is not a statement about the hardware")
    else:
        idle = [c for c in g if c["util"] < 10 and c["free_gb"] > 0.9 * c["total_gb"]]
        L.append(f"  GPU        {len(g)} card(s), {len(idle)} idle")
        for c in g:
            mark = "  idle" if c in idle else ""
            L.append(f"             [{c['index']}] {c['name']:<28} "
                     f"{c['free_gb']:5.1f} GB free of {c['total_gb']:5.1f}  util {c['util']:3d}%{mark}")
        if g and not idle:
            L.append("             nothing is free here. Other nodes usually are: groundwork cluster survey")
    m = d["memory"]
    if m["total_gb"]:
        L.append(f"  memory     {m['available_gb']:.0f} GB available of {m['total_gb']:.0f}, "
                 f"{m['cpus']} cpus, load {m['loadavg'][0]:.1f}" if m["loadavg"] else "")
    if m["shm"]:
        L.append(f"  /dev/shm   {m['shm']['size_gb']:.0f} GB, {m['shm']['used_gb']:.1f} GB used "
                 f"- this is RAM, and it is charged to you")
    for dd in d["disk"]:
        L.append(f"  disk       {dd['path']:<28} {dd['free_gb']:8.1f} GB free of {dd['size_gb']:.0f}")

    t = d["tools"]
    L.append(f"  on PATH    {' '.join(x['name'] for x in t['on_path']) or '(none of the ones looked for)'}")
    if t["off_path"]:
        L.append("  INSTALLED BUT NOT ON PATH - `which` says no and the machine says yes:")
        for name, paths in sorted(t["off_path"].items()):
            L.append(f"             {name}: {paths[0]}")
            for p in paths[1:3]:
                L.append(f"             {' ' * len(name)}  {p}")
    mods = d.get("modules")
    if mods:
        L.append(f"  modules    {mods['count']} in `module avail` - a catalogue that is deliberately not on PATH")
        for n, hits in sorted(mods["hits"].items()):
            L.append(f"             {n}: {' '.join(hits)}")
        if mods["restricted"]:
            L.append(f"             {' '.join(mods['restricted'])} is Anaconda's distribution: its")
            L.append("             licence covers commercial use of `defaults`/`repo.anaconda.com`.")
            L.append("             Prefer a miniforge module, or conda-forge, unless you have checked.")
    if t["absent"]:
        L.append(f"  not found  {' '.join(t['absent'])}")
        L.append(f"             looked on PATH and under {', '.join(t['searched']) or '(no search roots exist)'} "
                 f"to depth {t.get('depth', DEPTH)}"
                 + (", and in `module avail`" if mods else ""))
        if t.get("uncrawled"):
            L.append("             NOT crawled, and software on a cluster usually lives here:")
            for mm in t["uncrawled"]:
                L.append(f"                 {mm['path']}  ({_size(mm['size_gb'])})")
            L.append(f"             --root {t['uncrawled'][0]['path']} --search-seconds 120, "
                     "or ask the catalogue:")
            L.append(f"                 module avail 2>&1 | grep -i {t['absent'][0]}")
        if t["truncated"]:
            L.append("             THE FILESYSTEM SEARCH RAN OUT OF TIME - on a shared mount it usually does.")
            L.append("             These are unfinished searches, not absences. Ask the catalogue instead:")
            L.append(f"                 module avail 2>&1 | grep -i {t['absent'][0]}")
            L.append("             or narrow the crawl: --root /where/software/lives --search-seconds 120")

    iso = d["isolation"]
    have = [k for k in ("bwrap", "fuse-overlayfs", "podman", "apptainer", "singularity", "proot")
            if iso.get(k)]
    L.append(f"  isolation  unprivileged user namespaces: {'yes' if iso['unprivileged_userns'] else 'no'}"
             + (f"; {' '.join(have)}" if have else ""))
    L.append(f"             /dev/kvm {'yes' if iso['kvm'] else 'no'}, "
             f"cgroup v2 delegation {'yes' if iso['cgroup_v2_delegated'] else 'no'}")
    if iso["unprivileged_userns"] and not iso["kvm"]:
        L.append("             so: file-system and process isolation without root, but no VM.")
    L.append("")
    L.append("  A `not found` above is a statement about PATH and the directories listed,")
    L.append("  not about the machine. `which soffice` answered nothing here for months")
    L.append("  while LibreOffice sat in a shared directory; two sessions planned around")
    L.append("  its absence. Look before concluding.")
    return "\n".join(x for x in L if x)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork probe",
                                 description="what this machine can actually do, measured")
    ap.add_argument("--tool", action="append", default=[],
                    help="also look for this executable (repeatable)")
    ap.add_argument("--root", action="append", default=[],
                    help="also search here for off-PATH installs (repeatable)")
    ap.add_argument("--search-seconds", type=int, default=SEARCH_BUDGET)
    ap.add_argument("--depth", type=int, default=DEPTH,
                    help=f"how deep to crawl (default {DEPTH}; bundled installs sit about there)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    d = collect(a.tool, (a.root + ROOTS) if a.root else None, a.search_seconds, a.depth)
    print(json.dumps(d, indent=1) if a.json else report(d))
    return 0


if __name__ == "__main__":      # pragma: no cover
    sys.exit(main())
