#!/usr/bin/env python3
"""What can this machine actually fetch, and through which door?

An agent doing literature work on a locked-down cluster spends a surprising
amount of time discovering, one failure at a time, that a source is unreachable.
Worse, the failures are not uniform: a host can resolve and refuse, resolve and
hang, or return a page that is a challenge screen rather than content - and the
last one looks like success to anything that only checks the status code.

This classifies each target once, into a tier, so the pipeline can decide rather
than retry:

    OPEN        fetched, and the body looks like content
    CHALLENGE   answered, but the body is a bot check or a consent wall
    BLOCKED     connected and refused (401/403), or refused at the transport
    DNS         the name does not resolve
    TIMEOUT     no answer within the budget
    PROXY-ONLY  fails directly, succeeds through the configured proxy

    groundwork reach --targets arxiv.org api.openalex.org doi.org
    groundwork reach --targets-file targets.txt --proxy socks5h://127.0.0.1:1080
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request

DEFAULT_TARGETS = [
    "arxiv.org", "api.openalex.org", "api.crossref.org", "api.semanticscholar.org",
    "doi.org", "raw.githubusercontent.com", "api.github.com", "pypi.org",
]

CHALLENGE_MARKERS = (
    "just a moment", "enable javascript", "cf-browser-verification", "cf_chl",
    "checking your browser", "captcha", "access denied", "are you a robot",
    "consent", "cookie policy",
)


def _fetch(url, timeout, proxy=None):
    """Return (tier, detail). Never raises."""
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        opener = urllib.request.build_opener(handler)
    else:
        opener = urllib.request.build_opener()
    req = urllib.request.Request(url, headers={"User-Agent": "groundwork-reach/0.1"})
    try:
        with opener.open(req, timeout=timeout) as r:
            body = r.read(4096).decode("utf-8", "replace").lower()
            low = body.strip()
            if any(m in low for m in CHALLENGE_MARKERS):
                return "CHALLENGE", f"{r.status}, body looks like a challenge or consent page"
            return "OPEN", f"{r.status}, {len(body)} bytes sampled"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 451):
            return "BLOCKED", f"HTTP {e.code}"
        if e.code == 429:
            return "BLOCKED", "HTTP 429 - rate limited, which is not the same as unavailable"
        return "OPEN", f"HTTP {e.code} (answered)"
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, socket.gaierror):
            return "DNS", str(reason)
        if isinstance(reason, socket.timeout) or "timed out" in str(reason).lower():
            return "TIMEOUT", str(reason)
        return "BLOCKED", str(reason)
    except socket.timeout:
        return "TIMEOUT", "timed out"
    except Exception as e:                                   # noqa: BLE001
        return "BLOCKED", f"{type(e).__name__}: {e}"


def classify(target, timeout=12, proxy=None):
    url = target if "://" in target else f"https://{target}"
    tier, detail = _fetch(url, timeout)
    if tier in ("OPEN", "CHALLENGE"):
        return tier, detail
    if proxy:
        ptier, pdetail = _fetch(url, timeout, proxy)
        if ptier in ("OPEN", "CHALLENGE"):
            return "PROXY-ONLY", f"direct: {detail}; via proxy: {ptier} {pdetail}"
    return tier, detail


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork reach")
    ap.add_argument("--targets", nargs="*", default=None)
    ap.add_argument("--targets-file")
    ap.add_argument("--proxy", help="try this proxy when a target fails directly")
    ap.add_argument("--timeout", type=float, default=12)
    ap.add_argument("--json", help="write the table here")
    a = ap.parse_args(argv)

    targets = list(a.targets or [])
    if a.targets_file:
        with open(a.targets_file, encoding="utf-8") as fh:
            targets += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if not targets:
        targets = DEFAULT_TARGETS

    rows = []
    for t in targets:
        tier, detail = classify(t, a.timeout, a.proxy)
        rows.append({"target": t, "tier": tier, "detail": detail})
        print(f"  {tier:<11} {t:<34} {detail[:60]}")

    by = {}
    for r in rows:
        by.setdefault(r["tier"], []).append(r["target"])
    print()
    print("  ".join(f"{k} {len(v)}" for k, v in sorted(by.items())))
    if "CHALLENGE" in by:
        print("\nCHALLENGE is the one to watch: the request succeeded and the body is not")
        print("content, so anything checking only the status code will treat a bot wall as")
        print("a paper. Never let an automated literature step consume a CHALLENGE body.")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
