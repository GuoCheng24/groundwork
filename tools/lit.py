#!/usr/bin/env python3
"""Literature that can be checked: real metadata, real DOIs, and an occupancy search.

Two jobs, and they are not the same job.

**Grounding.** A citation an agent produced is a claim about the world. This
resolves it against real indexes and refuses to hand back a BibTeX entry it is
not confident in, because a plausible-looking wrong citation is worse than none.

**Occupancy.** Before a direction is started, find the work that already
occupies it. This is the search that decides whether a week is spent, and it is
the one most likely to return a confident wrong answer.

Every behaviour below is there because the obvious version failed:

* **Focused keywords, not the claim sentence.** A whole sentence drags the query
  into adjacent fields; three to five terms naming the mechanism find the
  neighbourhood.
* **Word-hit re-ranking** (title x3, abstract x1). A broad index returns the
  right paper mixed with noise from other fields, and without re-ranking the
  right paper is on page three and you conclude it does not exist.
* **OpenAlex as the stable primary.** Semantic Scholar rate-limits hard without
  a key, so it is enrichment and never the thing a verdict rests on.
* **A dynamic current year.** An agent surveying from its own weights surveys
  the year its training stopped. `latest` exists because "recent work" sorted by
  relevance returns highly-cited old work.
* **`best_match` refuses weak matches.** Taking the first result when relevance
  is poor once returned a thesis in place of a survey - silently, with a
  correctly formatted BibTeX entry.
* **"Not found" is not "does not exist".** When every backend fails at once that
  is a network diagnosis, and `verify` says so instead of reporting a
  hallucination.

Standard library only. Set `PROOFGROUND_PROXY` for an http(s) proxy,
`PROOFGROUND_MAILTO` to be polite to the APIs, `PROOFGROUND_S2KEY` for a
Semantic Scholar key.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CUR_YEAR = datetime.date.today().year          # never hard-code a year; it rots
PROXY = os.environ.get("PROOFGROUND_PROXY")
MAILTO = os.environ.get("PROOFGROUND_MAILTO", "")
S2KEY = os.environ.get("PROOFGROUND_S2KEY")
DOI_RE = r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"
ARXIV_RE = r"\d{4}\.\d{4,5}(?:v\d+)?"
UA = "proofground-lit/0.1" + (f" (mailto:{MAILTO})" if MAILTO else "")

_NET_FAILURES = 0          # distinguishes "nothing found" from "nothing reachable"

# Which backends answered this run. The primary index enforces a daily quota and
# starts returning 429 when it is spent - and the first version of this tool
# degraded silently to a preprint-only search and printed the results as though
# the search were complete. A quota that answers with nothing looks exactly like
# a literature with nothing in it, which is the most expensive way to be wrong
# at this stage.
BACKENDS = {}


def _opener():
    if PROXY:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    return urllib.request.build_opener()


def _get(url, accept="application/json", retries=3, timeout=20):
    """Fetch, backing off on rate limits. Returns text or None, and counts failures."""
    global _NET_FAILURES
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    if S2KEY and "semanticscholar" in url:
        req.add_header("x-api-key", S2KEY)
    for k in range(retries):
        try:
            with _opener().open(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(2.0 * (k + 1))
                continue
            _NET_FAILURES += 1
            return None
        except Exception:                                     # noqa: BLE001
            time.sleep(1.0 * (k + 1))
    _NET_FAILURES += 1
    return None


def _json(url):
    t = _get(url)
    if not t:
        return None
    try:
        return json.loads(t)
    except ValueError:
        return None


# ------------------------------------------------------------------ ranking

_STOP = set("the a an of for and or to in on with via using from is are be that this we our by as "
            "at how when what which under over into onto not no".split())


def _tokens(s, minlen=4):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower())
            if len(w) >= minlen and w not in _STOP}


def _relevance(query, paper):
    """Word hits, title weighted 3x. The thing that makes a broad index usable."""
    q = _tokens(query)
    if not q:
        return 0.0
    t = _tokens(paper.get("title", ""))
    a = _tokens(paper.get("abstract", ""))
    return (3.0 * len(q & t) + 1.0 * len(q & a)) / (3.0 * len(q))


def _year_bonus(paper):
    """Keep new work from being buried by highly-cited old work."""
    y = paper.get("year") or 0
    if not y:
        return 0.0
    age = max(0, CUR_YEAR - y)
    return max(0.0, 0.35 - 0.07 * age)


# ----------------------------------------------------------------- backends

def _oa_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))[:1200]


def _oa_paper(w):
    ids = w.get("ids") or {}
    doi = (ids.get("doi") or "").replace("https://doi.org/", "") or None
    loc = (w.get("primary_location") or {}).get("source") or {}
    return {
        "title": w.get("title") or "",
        "year": w.get("publication_year"),
        "doi": doi,
        "venue": loc.get("display_name") or "",
        "cited_by": w.get("cited_by_count", 0),
        "abstract": _oa_abstract(w.get("abstract_inverted_index")),
        "oa_id": (ids.get("openalex") or "").rsplit("/", 1)[-1] or None,
        "source": "openalex",
    }


def _note(name, ok):
    BACKENDS[name] = BACKENDS.get(name, False) or ok
    BACKENDS.setdefault(name, ok)
    return ok


def backend_report():
    """A line naming which indexes answered, and whether the primary one did."""
    if not BACKENDS:
        return "no backend was queried"
    parts = ", ".join(f"{k}: {'ok' if v else 'NO ANSWER'}" for k, v in sorted(BACKENDS.items()))
    return parts


def primary_answered():
    return BACKENDS.get("openalex", False)


def search_openalex(query, n=8, since=None):
    q = urllib.parse.quote(query)
    url = (f"https://api.openalex.org/works?search={q}&per-page={max(n * 3, 15)}"
           f"&sort=relevance_score:desc")
    if since:
        url += f"&filter=from_publication_date:{since}-01-01"
    d = _json(url)
    _note("openalex", d is not None)
    return [_oa_paper(w) for w in (d or {}).get("results", [])]


def search_s2(query, n=8):
    q = urllib.parse.quote(query)
    url = (f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}"
           f"&limit={n}&fields=title,year,abstract,externalIds,venue,citationCount")
    d = _json(url)
    _note("semanticscholar", d is not None)
    out = []
    for p in (d or {}).get("data", []) or []:
        ext = p.get("externalIds") or {}
        out.append({"title": p.get("title") or "", "year": p.get("year"),
                    "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
                    "venue": p.get("venue") or "", "cited_by": p.get("citationCount", 0),
                    "abstract": (p.get("abstract") or "")[:1200], "source": "s2"})
    return out


def search_arxiv(query, n=8):
    q = urllib.parse.quote(query)
    url = (f"http://export.arxiv.org/api/query?search_query=all:{q}"
           f"&max_results={n}&sortBy=relevance")
    t = _get(url, accept="application/atom+xml")
    _note("arxiv", bool(t))
    if not t:
        return []
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", t, re.S):
        def grab(tag):
            m = re.search(rf"<{tag}>(.*?)</{tag}>", entry, re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        aid = grab("id").rsplit("/", 1)[-1]
        out.append({"title": grab("title"), "year": int((grab("published") or "0")[:4] or 0),
                    "doi": None, "arxiv": aid, "venue": "arXiv",
                    "cited_by": 0, "abstract": grab("summary")[:1200], "source": "arxiv"})
    return out


def multi_search(query, n=8, since=None, recency=False):
    """OpenAlex first, enriched by the others, de-duplicated and re-ranked."""
    papers, seen = [], set()

    def add(lst):
        for p in lst:
            key = (p.get("doi") or p.get("arxiv") or p.get("title", "")[:70]).lower()
            if key and key not in seen:
                seen.add(key)
                papers.append(p)

    add(search_openalex(query, n, since))
    add(search_s2(query, n))
    add(search_arxiv(query, n))
    for p in papers:
        p["score"] = _relevance(query, p) + (_year_bonus(p) if recency else 0.0)
    papers.sort(key=lambda p: -p["score"])
    return papers[:n]


def best_match(query, n=8, floor=0.5):
    """The single best paper, or None. Refuses when coverage is poor.

    Returning the top hit regardless of relevance once handed back a doctoral
    thesis in place of a well-known survey, formatted correctly enough that
    nobody looked twice.
    """
    hits = multi_search(query, n)
    if not hits:
        return None
    top = hits[0]
    return top if _relevance(query, top) >= floor else None


# ------------------------------------------------------------- subcommands

def _fmt(p, i=None):
    tag = f"{i:>2}. " if i is not None else "    "
    loc = p.get("doi") or (f"arXiv:{p['arxiv']}" if p.get("arxiv") else "")
    return (f"{tag}{p.get('year') or '????'}  {p.get('title', '')[:96]}\n"
            f"        {p.get('venue', '')[:44]:<44} cited {p.get('cited_by', 0):<6} {loc}")


def cmd_search(a):
    hits = multi_search(a.query, a.n, a.since, recency=a.recent)
    if not hits:
        print("no results" + (" - and every backend failed, which is a network diagnosis"
                              if _NET_FAILURES else ""))
        return 1
    for i, p in enumerate(hits, 1):
        print(_fmt(p, i))
    print(f"\n# backends: {backend_report()}")
    if not primary_answered():
        print("# WARNING: the primary index did not answer, so this is a partial search.")
        print("#          Its daily quota returns 429 when spent; set PROOFGROUND_MAILTO")
        print("#          to use the polite pool, or re-run later.")
    return 0


def cmd_latest(a):
    a.recent = True
    a.since = a.since or (CUR_YEAR - 1)
    print(f"# recent work, {a.since} onwards (current year resolved at run time: {CUR_YEAR})")
    return cmd_search(a)


def cmd_verify(a):
    """Does this exist? And is 'no' an answer or a network failure?"""
    before = _NET_FAILURES
    hits = multi_search(a.query, 5)
    top = hits[0] if hits else None
    rel = _relevance(a.query, top) if top else 0.0
    if top and rel >= 0.6:
        print("EXISTS")
        print(_fmt(top))
        print("\nThis is metadata from an index, which is strong evidence and not proof.")
        print("Before citing it, open the record itself and read the abstract - and ask")
        print("about the page neutrally. A question that states the title you expect")
        print("makes a reading model confirm the title you expect.")
        return 0
    if _NET_FAILURES > before:
        print("UNRESOLVED - and backends failed during this query.")
        print("This is not evidence of fabrication. A batch of failures at once is a")
        print("network diagnosis; re-run when the connection is healthy before drawing")
        print("any conclusion about whether this paper exists.")
        return 2
    if not primary_answered():
        print("UNRESOLVED - the primary index did not answer.")
        print("Its daily quota returns 429 when spent, and a spent quota looks exactly")
        print("like a paper that does not exist. This is not a verdict; re-run later.")
        return 2
    print("NOT FOUND in any backend, with the network healthy.")
    if top:
        print(f"\nclosest match (relevance {rel:.2f}, under the 0.60 floor):")
        print(_fmt(top))
    print("\nTreat as suspect, not as settled. An identifier that looks 'too recent to")
    print(f"be real' is not a test: today is {CUR_YEAR}, and that heuristic has")
    print("produced false accusations against real papers.")
    return 1


def cmd_bibtex(a):
    s = a.query.strip()
    doi = (re.search(DOI_RE, s) or [None])[0] if re.search(DOI_RE, s) else None
    if doi is None:
        m = re.search(DOI_RE, s)
        doi = m.group(0) if m else None
    if doi is None:
        p = best_match(s)
        if p is None:
            print("no confident match - refusing to emit a citation.")
            print("A plausible wrong citation is worse than none. Narrow the query.")
            return 1
        doi, arx = p.get("doi"), p.get("arxiv")
        if not doi and arx:
            key = re.sub(r"\W", "", (p.get("title") or "x").split()[0].lower()) + str(p.get("year") or "")
            print(f"@misc{{{key},\n  title  = {{{p['title']}}},\n"
                  f"  year   = {{{p.get('year')}}},\n  note   = {{arXiv:{arx}}},\n"
                  f"  eprint = {{{arx}}},\n  archivePrefix = {{arXiv}}\n}}")
            return 0
    t = _get(f"https://doi.org/{doi}", accept="application/x-bibtex")
    if not t or "@" not in t:
        print(f"could not retrieve a BibTeX record for {doi}")
        return 1
    print(t.strip())
    return 0


def cmd_occupancy(a):
    print(f"# occupancy search: {a.query!r}")
    print("# feed focused keywords naming the mechanism, not the whole claim sentence\n")
    hits = multi_search(a.query, a.n)
    if not hits:
        print("no neighbours found" + (" - every backend failed; this is a network result"
                                       if _NET_FAILURES else ""))
        return 1
    for i, p in enumerate(hits, 1):
        print(_fmt(p, i))
    recent = [p for p in multi_search(a.query, a.n, since=CUR_YEAR - 1, recency=True)]
    if recent:
        print(f"\n# recent neighbours ({CUR_YEAR - 1} onwards) - surveying from memory misses these")
        for i, p in enumerate(recent[:max(3, a.n // 2)], 1):
            print(_fmt(p, i))
    print(f"\n# backends: {backend_report()}")
    if not primary_answered():
        print("""
# ====================================================================
#  NO VERDICT AVAILABLE. The primary index did not answer, so this is
#  a preprint-only search. "Nothing occupies this" cannot be concluded
#  from it - a spent quota and an empty literature look identical.
#  Set PROOFGROUND_MAILTO for the polite pool, or re-run later.
# ====================================================================""")
        return 2
    print("""
# Closing the gate needs more than this list:
#   1. every candidate that matters gets its existence checked separately -
#      an occupancy search can invent a neighbour that does not exist;
#   2. read the closest two or three, not their abstracts - a verdict of
#      "already occupied" requires reading the thing that occupies it;
#   3. record the verdict either way in archive/, with the paper that settled
#      it. "Occupied, by this, which says this" is worth as much as a go.""")
    return 0


def cmd_citedby(a):
    p = best_match(a.query)
    if p is None or not p.get("oa_id"):
        print("no confident match with a resolvable id")
        return 1
    d = _json(f"https://api.openalex.org/works?filter=cites:{p['oa_id']}"
              f"&per-page={a.n}&sort=cited_by_count:desc")
    works = [_oa_paper(w) for w in (d or {}).get("results", [])]
    print(f"# work extending: {p['title'][:90]}\n")
    for i, w in enumerate(works, 1):
        print(_fmt(w, i))
    print("\n# if your extension is here, it is occupied")
    return 0 if works else 1


def cmd_journal(a):
    q = urllib.parse.quote(a.query)
    d = _json(f"https://api.openalex.org/sources?search={q}&per-page=5")
    rows = (d or {}).get("results", [])
    if not rows:
        print("no such source found")
        return 1
    for s in rows[:3]:
        st = s.get("summary_stats") or {}
        print(f"  {s.get('display_name', '')[:60]}")
        print(f"     2-year mean citedness {st.get('2yr_mean_citedness', 0):.2f}   "
              f"h-index {st.get('h_index', 0)}   works {s.get('works_count', 0)}")
        print(f"     {s.get('homepage_url') or ''}")
    print("""
# These are citation-based proxies, NOT the official impact factor. Measured
# against one journal's official figure the proxy was off by a factor of three.
# Quote the proxy with its name and its source, or look the official number up.
# What you must not do is quote either from memory: one such recollection
# mis-set a venue choice by a factor of two.""")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="proofground lit",
        description="Literature grounding and occupancy search that can be checked.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, help, recent=False):
        sp = sub.add_parser(name, help=help)
        sp.add_argument("query")
        sp.add_argument("-n", type=int, default=8)
        sp.add_argument("--since", type=int, default=None)
        sp.set_defaults(recent=recent)
        return sp

    add("search", "multi-source search, re-ranked by word hits").set_defaults(func=cmd_search)
    add("latest", "recent work; an agent surveying from memory misses it", recent=True).set_defaults(func=cmd_latest)
    add("verify", "does this paper exist, and is 'no' an answer or a network failure").set_defaults(func=cmd_verify)
    add("bibtex", "a real entry, or a refusal").set_defaults(func=cmd_bibtex)
    add("occupancy", "who already occupies this claim").set_defaults(func=cmd_occupancy)
    add("citedby", "who extended it - is your extension occupied").set_defaults(func=cmd_citedby)
    add("journal", "current metrics for a venue, with the caveat attached").set_defaults(func=cmd_journal)

    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
