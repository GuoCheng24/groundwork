#!/usr/bin/env python3
"""Every number in the README, re-derived.

This repository tells people to keep a check that recomputes the figures on
their front page. It did not have one, and by the time this was written two of
its numbers were stale: the sibling ledger had grown from 20 findings to 21 and
its human-eye count from 9 to 10. Nothing was wrong with the sentences; the
files they described had moved on.

Two kinds of number, checked differently.

**Internal** - stages, notes, tools, causes, commands - are recomputed from
this repository on every run, so they cannot drift at all.

**External** - numbers that live in a sibling repository - are checked against
`archive/external-facts.json`, which records the value, the repository, the
file and how it is derived. That keeps CI hermetic. And whenever the sibling
repository happens to be checked out next to this one, every external fact is
re-derived from it as well, which is where drift is actually caught.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
README = os.path.join(ROOT, "README.md")
FACTS = os.path.join(ROOT, "archive", "external-facts.json")
SIBLINGS = {                      # repository name -> where it is cloned here
    "ifeval-reproduction": ("gh-ifeval", "ifeval-reproduction"),
    "doubleblind": ("doubleblind",),
    "taichu-eval-reproduction": ("taichu-eval-reproduction",),
}


def readme():
    with open(README, encoding="utf-8") as fh:
        return fh.read()


def _sibling(name):
    """The sibling repository, if somebody happens to have it checked out."""
    parent = os.path.dirname(ROOT)
    for d in SIBLINGS.get(name, (name,)):
        p = os.path.join(parent, d)
        if os.path.isdir(os.path.join(p, ".git")):
            return p
    return None


def _derive(fact, repo_dir):
    """Re-derive one fact from its source file.

    The rules are spelled out here rather than in a query language in the JSON:
    there are eight of them, and a language nobody can read is a place for a
    mistake to hide.
    """
    with open(os.path.join(repo_dir, fact["path"]), encoding="utf-8") as fh:
        d = json.load(fh)
    i = fact["id"]
    if i == "scorer_spread_points":
        return round(d["metrics"]["prompt_level_strict_acc"]["spread_points"], 2)
    if i == "scorer_n_scorings":
        return d["n_scorings"]
    if i == "hardware_points":
        k = next(k for k in d if k.startswith("HARDWARE"))
        return abs(round(d[k]["metrics"]["prompt_level_strict_acc"]["points"], 2))
    if i == "byte_identical":
        k = next(k for k in d if k.startswith("DETERMINISM"))
        return d[k]["byte_identical_responses"]
    rows = d.get("findings", d) if isinstance(d, dict) else d
    if i == "ledger_findings":
        return len(rows)
    if i == "ledger_human_eye":
        return sum(1 for r in rows if r.get("caught_by") == "human eye")
    if i == "fresh_eyes_returned":
        return d["context"]["fresh_eyes_run_1"]["findings_returned"]
    if i == "fresh_eyes_verified":
        return d["context"]["fresh_eyes_run_1"]["findings_verified"]
    if i == "taichu_unclosed_credited":
        return round((d["accuracy_pct"] - d["accuracy_unclosed_as_wrong_pct"])
                     * d["n"] / 100)
    if i == "taichu_mv_n":
        return d["n"]
    raise AssertionError(f"no derivation for {i!r} - add one rather than skipping it")


class Internal(unittest.TestCase):
    def test_the_stage_and_file_counts_are_the_ones_on_disk(self):
        stages = len(glob.glob(os.path.join(ROOT, "groundwork", "skills", "*/")))
        notes = len(glob.glob(os.path.join(ROOT, "groundwork", "skills", "*", "*.md")))
        m = re.search(r"Seven stages, (\d+) files", readme())
        self.assertIsNotNone(m, "the README no longer states its own file count")
        self.assertEqual(stages, 7, "'Seven stages' and the directory count disagree")
        self.assertEqual(int(m.group(1)), notes)



    def test_the_readme_has_no_relative_links(self):
        """This README becomes the PyPI project page, where a relative link is
        a dead link — and a release's description cannot be changed without a
        new version. 51 of its 64 links were relative when that was noticed.

        The stage notes keep THEIR relative links: they are read next to each
        other, on GitHub and inside the installed package.
        """
        # `[![badge](img-url)](target)` nests brackets, and a pattern that
        # stops at the first `]` matches the IMAGE url and never sees the
        # target. The licence badge pointed at a bare `LICENSE` and this check
        # reported zero relative links. Every `](...)` is examined instead.
        rel = [t for t in re.findall(r"\]\(([^)\s]+)\)", readme())
               if not t.startswith(("http://", "https://", "#", "mailto:"))]
        self.assertEqual(rel, [], "relative links in the README are dead on PyPI")

    def test_the_committed_inventory_matches_what_is_on_disk(self):
        """`archive/inventory.json` exists so that a page elsewhere can check a
        count it cannot compute: raw.githubusercontent.com serves files, not
        directory listings, so a profile quoting "43 stage notes" is quoting
        memory unless the number is committed. This is what makes it evidence.
        """
        with open(os.path.join(ROOT, "archive", "inventory.json"), encoding="utf-8") as fh:
            inv = json.load(fh)
        md = glob.glob(os.path.join(ROOT, "groundwork", "skills", "*", "*.md"))
        skills = [f for f in md if os.path.basename(f) == "SKILL.md"]
        from groundwork import cli
        self.assertEqual(inv["stages"], len(skills))
        self.assertEqual(inv["markdown_files"], len(md))
        self.assertEqual(inv["notes"], len(md) - len(skills))
        self.assertEqual(inv["n_commands"], len(cli.COMMANDS))
        self.assertEqual(sorted(inv["commands"]), sorted(cli.COMMANDS))
        with open(os.path.join(ROOT, "archive", "causes-of-death.json"), encoding="utf-8") as fh:
            self.assertEqual(inv["causes_of_death"], len(json.load(fh)["causes"]))

    def test_the_archive_really_records_ten_causes(self):
        with open(os.path.join(ROOT, "archive", "causes-of-death.json"), encoding="utf-8") as fh:
            causes = json.load(fh)["causes"]
        self.assertEqual(len(causes), 10)
        self.assertIn("records ten", readme())

    def test_every_command_in_the_table_exists(self):
        from groundwork import cli
        quoted = set(re.findall(r"`groundwork (\w+)`", readme()))
        self.assertTrue(quoted)
        for name in quoted:
            self.assertIn(name, cli.COMMANDS, f"the README documents `groundwork {name}`, "
                                              "which is not a command")

    def test_every_command_is_documented(self):
        from groundwork import cli
        quoted = set(re.findall(r"`groundwork (\w+)`", readme()))
        missing = sorted(set(cli.COMMANDS) - quoted)
        self.assertEqual(missing, [], "commands that exist and are not in the README")


class External(unittest.TestCase):
    def setUp(self):
        with open(FACTS, encoding="utf-8") as fh:
            self.facts = json.load(fh)["facts"]

    def test_every_recorded_fact_is_quoted_in_the_document_it_names(self):
        """Every entry names its document.

        A fact file whose entries float free of any page stops being checked
        the first time a page is rewritten - and the same shape, an exemption
        that names no document, once disarmed a whole repository's checks in a
        sibling project.
        """
        for f in self.facts:
            path = os.path.join(ROOT, f["used_in"])
            self.assertTrue(os.path.exists(path), f"{f['id']}: names {f['used_in']}, "
                                                  "which does not exist")
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn(f["rendered"], text,
                          f"{f['id']}: recorded as used in {f['used_in']} and not "
                          "found there")

    def test_each_fact_names_a_repository_a_file_and_a_derivation(self):
        for f in self.facts:
            for k in ("id", "value", "rendered", "what", "repo", "path", "derive",
                      "as_of", "used_in"):
                self.assertTrue(f.get(k) not in (None, ""), f"{f.get('id')}: empty {k}")

    def test_facts_are_re_derived_from_the_siblings_when_they_are_present(self):
        checked = []
        for f in self.facts:
            repo = _sibling(f["repo"])
            if repo is None or not os.path.exists(os.path.join(repo, f["path"])):
                continue
            self.assertEqual(_derive(f, repo), f["value"],
                             f"{f['id']} has drifted from {f['repo']}/{f['path']}")
            checked.append(f["id"])
        if not checked:
            self.skipTest("no sibling repository checked out beside this one; "
                          "the recorded values were checked, the sources were not")


class InstallLines(unittest.TestCase):
    """What the README and the plugin manifest tell a reader to type.

    The README once said `pip install groundwork-research` for a package that
    had never been published: PyPI returned 404, and the plugin marketplace
    description said the same thing, so both routes a reader might take ended
    in "No matching distribution found". It is published now, so the rule is
    no longer "must not name it" but "must name it exactly" - a hyphen for an
    underscore is the same 404.
    """

    def _dist_name(self):
        with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as fh:
            return re.search(r'^\s*name\s*=\s*"([^"]+)"', fh.read(), re.M).group(1)

    def test_every_install_line_names_this_package_exactly(self):
        name = self._dist_name()
        claimed = set(re.findall(r"pip install ([A-Za-z][A-Za-z0-9_.-]+)", readme()))
        wrong = sorted(c for c in claimed if c.lower().replace("_", "-")
                       == name.lower().replace("_", "-") and c != name)
        self.assertEqual(wrong, [], f"the README writes {wrong} where PyPI has {name!r}; "
                                    "a hyphen for an underscore is still a 404")
        self.assertIn(name, claimed,
                      f"the README no longer tells anyone how to install {name}")


    def test_no_shipped_file_tells_anyone_to_install_the_wrong_package(self):
        """The guard looked at README.md while the wheel ships fifty more.

        `30-claim/SKILL.md` said `pip install doubleblind`, which is an
        unrelated project on PyPI by another author, and that file went out
        inside 0.1.0 — a published package telling its readers to install
        somebody else's. Every markdown file that ships is checked now, and
        every install target must be a package this project actually means.
        """
        known = {"groundwork-research", "doubleblind-audit"}
        offenders = []
        # skills ship in the wheel; docs ship in the sdist; the README ships in
        # both. The first version of this check covered the first and the
        # third and missed a `pip install doubleblind` in docs/worked-example.md
        # - the same blind spot, one directory over.
        for f in sorted(glob.glob(os.path.join(ROOT, "groundwork", "skills", "*", "*.md"))
                        + glob.glob(os.path.join(ROOT, "docs", "*.md"))
                        + [README]):
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
            for m in re.finditer(r"pip install ([A-Za-z][A-Za-z0-9_.\[\]-]+)", text):
                pkg = m.group(1).split("[")[0]
                if pkg not in known:
                    line = text[:m.start()].count("\n") + 1
                    offenders.append(f"{os.path.relpath(f, ROOT)}:{line} -> {pkg}")
        self.assertEqual(offenders, [], "shipped files naming a package that is not ours: "
                                        + "; ".join(offenders))

    def test_the_plugin_manifest_says_the_same_thing(self):
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"),
                  encoding="utf-8") as fh:
            desc = json.load(fh)["plugins"][0]["description"]
        self.assertIn(f"pip install {self._dist_name()}", desc)

    def test_the_manifest_lists_the_commands_that_exist(self):
        """It listed twelve of fifteen, and the missing one was the newest.

        A hand-kept list in prose is a list that goes stale; `init` and
        `install` are left out on purpose because they are not tools you reach
        for mid-project.
        """
        from groundwork import cli
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"),
                  encoding="utf-8") as fh:
            desc = json.load(fh)["plugins"][0]["description"]
        for c in cli.COMMANDS:
            if c in ("init", "install"):
                continue
            self.assertIn(c, desc, f"`groundwork {c}` exists and the manifest omits it")



if __name__ == "__main__":
    unittest.main(verbosity=2)
