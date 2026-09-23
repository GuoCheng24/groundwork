"""Tests. The ones that matter assert a refusal.

A gate that has never been seen refusing is decoration, so every blocking path
here is exercised with an input built to trip it - and the boundary cases that
must still pass are exercised too, because a gate that refuses everything is
also decoration.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from groundwork import attach, cluster, ledger, noise, reach, scaffold, stats  # noqa: E402
from groundwork import lit  # noqa: E402
from groundwork import check  # noqa: E402
from groundwork import probe  # noqa: E402
from groundwork import shard  # noqa: E402
from groundwork import watch  # noqa: E402
from groundwork import prereg  # noqa: E402
from groundwork import gate as gate_mod  # noqa: E402
from groundwork.gate import detectable_effect, required_se, verdict  # noqa: E402

# A throwaway repository created by a test is not anybody's work, so it gets a
# neutral identity. Some environments install a global hook that enforces a
# personal one; the documented escape hatch covers exactly this case.
IDENT = ["-c", "user.name=groundwork-test",
         "-c", "user.email=test@example.invalid"]
TEST_ENV = {**os.environ, "ALLOW_OTHER_GIT_IDENTITY": "1"}


class Gate(unittest.TestCase):
    def assertBlocks(self, phrase, **kw):
        go, _lines, facts = verdict(**kw)
        self.assertFalse(go, f"expected NO-GO for {kw}")
        self.assertTrue(any(phrase in b for b in facts["blocking"]),
                        f"{phrase!r} not in {facts['blocking']}")

    def test_an_oracle_that_does_not_beat_the_baseline(self):
        self.assertBlocks("does not beat", baseline=.80, oracle=.79, se=.01)

    def test_headroom_narrower_than_two_standard_errors(self):
        self.assertBlocks("under the 2 SE", baseline=.80, oracle=.815, se=.01)

    def test_headroom_the_split_cannot_resolve(self):
        self.assertBlocks("smaller than the smallest effect",
                          baseline=.50, oracle=.53, se=.011)

    def test_a_random_arm_that_matches_the_baseline(self):
        self.assertBlocks("random arm scores",
                          baseline=.80, oracle=.95, se=.01, random_arm=.80)

    def test_a_positive_control_that_does_not_recover(self):
        self.assertBlocks("measure the pipeline", baseline=.50, oracle=.75, se=.011,
                          positive_control=.52, positive_control_floor=.70)

    def test_a_direction_with_room_is_allowed(self):
        go, _l, facts = verdict(baseline=.50, oracle=.75, se=.011,
                                random_arm=.20, positive_control=.80,
                                positive_control_floor=.70)
        self.assertTrue(go, facts["blocking"])
        self.assertAlmostEqual(facts["headroom"], 0.25, places=6)

    def test_power_arithmetic_is_self_consistent(self):
        se = 0.013
        self.assertAlmostEqual(required_se(detectable_effect(se)), se, places=9)

    def test_the_cli_exit_code_carries_the_verdict(self):
        def run(*args):
            return subprocess.run([sys.executable, "-m", "groundwork",
                                   "gate", *args], capture_output=True, text=True).returncode
        self.assertEqual(run("--baseline", ".5", "--oracle", ".75", "--se", ".011"), 0)
        self.assertEqual(run("--baseline", ".8", "--oracle", ".81", "--se", ".01"), 1)


class Prereg(unittest.TestCase):
    @staticmethod
    def _repo():
        d = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        return d

    @staticmethod
    def _commit(d, *paths):
        subprocess.run(["git", "add", *paths], cwd=d, check=True)
        subprocess.run(["git", *IDENT, "commit", "-qm", "x"], cwd=d, check=True,
                       env=TEST_ENV)

    def _make(self, d, name="PREREG.md"):
        p = os.path.join(d, name)
        prereg.cmd_new(type("A", (), {"path": p, "title": "t", "when": "now", "force": True})())
        import re
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(re.sub(r"<!--.*?-->", "filled in.", s, flags=re.S))
        prereg.cmd_seal(type("A", (), {"path": p, "out": None})())
        return p

    def _verify(self, path, results=None):
        return prereg.cmd_verify(type("A", (), {"path": path, "seal": None,
                                                "results": results})())

    def test_the_template_alone_is_refused(self):
        d = self._repo()
        p = os.path.join(d, "PREREG.md")
        prereg.cmd_new(type("A", (), {"path": p, "title": "t", "when": "now", "force": True})())
        self.assertEqual(self._verify(p), 1)

    def test_results_committed_first_is_refused(self):
        d = self._repo()
        r = os.path.join(d, "results.json")
        open(r, "w").write("{}")
        self._commit(d, "results.json")
        p = self._make(d)
        import time
        time.sleep(1.1)
        self._commit(d, "PREREG.md", "PREREG.sha256")
        self.assertEqual(self._verify(p, [r]), 1)

    def test_prereg_committed_first_is_accepted(self):
        d = self._repo()
        p = self._make(d)
        self._commit(d, "PREREG.md", "PREREG.sha256")
        import time
        time.sleep(1.1)
        r = os.path.join(d, "results.json")
        open(r, "w").write("{}")
        self._commit(d, "results.json")
        self.assertEqual(self._verify(p, [r]), 0)

    def test_an_edit_after_sealing_is_caught(self):
        d = self._repo()
        p = self._make(d)
        self._commit(d, "PREREG.md", "PREREG.sha256")
        with open(p, "a", encoding="utf-8") as fh:
            fh.write("\none more thing\n")
        self.assertEqual(self._verify(p), 1)

    def test_an_uncommitted_preregistration_is_refused(self):
        d = self._repo()
        p = self._make(d)
        self.assertEqual(self._verify(p), 1)


class Literature(unittest.TestCase):
    """A silent index must not read as an empty literature.

    The primary index enforces a daily quota and answers 429 when it is spent.
    The first version of this tool degraded to a preprint-only search and
    printed the results as though the search were complete - which is the most
    expensive way to be wrong at the occupancy gate, because "nobody has done
    this" is exactly the answer a spent quota produces.
    """

    def setUp(self):
        lit.BACKENDS.clear()

    def test_occupancy_refuses_a_verdict_without_the_primary_index(self):
        lit.BACKENDS.update({"openalex": False, "arxiv": True})
        self.assertFalse(lit.primary_answered())
        self.assertIn("NO ANSWER", lit.backend_report())

    def test_the_primary_answering_is_what_allows_a_verdict(self):
        lit.BACKENDS.update({"openalex": True, "arxiv": True})
        self.assertTrue(lit.primary_answered())
        self.assertNotIn("NO ANSWER", lit.backend_report())

    def test_ranking_puts_the_on_topic_paper_first(self):
        q = "bfloat16 batch invariance importance ratio"
        on = {"title": "Batch invariance of bfloat16 importance ratios", "abstract": "", "year": 2026}
        off = {"title": "Batch scheduling with minimum batch size", "abstract": "", "year": 2025}
        self.assertGreater(lit._relevance(q, on), lit._relevance(q, off))

    def test_the_current_year_is_resolved_at_run_time(self):
        import datetime
        self.assertEqual(lit.CUR_YEAR, datetime.date.today().year)

    def test_a_weak_top_hit_is_refused_rather_than_returned(self):
        real = lit.multi_search
        try:
            lit.multi_search = lambda q, n=8, since=None, recency=False: [
                {"title": "An entirely unrelated doctoral thesis", "abstract": "", "year": 2011}]
            self.assertIsNone(lit.best_match("bfloat16 batch invariance importance ratio"))
        finally:
            lit.multi_search = real


class Cluster(unittest.TestCase):
    SURVEY = {
        "a": [{"node": "a", "index": 0, "name": "L40", "used_mb": 0,
               "total_mb": 46080, "free_mb": 46080, "util_pct": 0},
              {"node": "a", "index": 1, "name": "L40", "used_mb": 19000,
               "total_mb": 46080, "free_mb": 27080, "util_pct": 95}],
        "b": [{"node": "b", "index": 0, "name": "RTX 4090", "used_mb": 19000,
               "total_mb": 24564, "free_mb": 5564, "util_pct": 60}],
    }

    def test_a_card_with_somebody_elses_job_is_not_free_memory(self):
        fits = cluster.rank(self.SURVEY, need_gb=20, leave_free=0)
        self.assertNotIn(("b", 0), [(g["node"], g["index"]) for g in fits],
                         "a card with 5.4 GB free was offered for a 20 GB job")

    def test_one_card_per_node_is_held_back_and_it_is_an_idle_one(self):
        ranked = cluster.rank(self.SURVEY, need_gb=20, leave_free=1)
        held = [(g["node"], g["index"]) for g in ranked if g.get("held_back")]
        self.assertIn(("a", 0), held, "the idlest card should be the one left for others")

    def test_plan_refuses_to_split_one_arm_across_two_gpu_models(self):
        mixed = {"a": [dict(self.SURVEY["a"][0])],
                 "b": [{"node": "b", "index": 0, "name": "V100", "used_mb": 0,
                        "total_mb": 32768, "free_mb": 32768, "util_pct": 0}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(mixed, fh)
            path = fh.name
        try:
            args = type("A", (), {"nodes": [], "from_file": path, "need_gb": 20,
                                  "shards": 2, "leave_free": 0, "command": "run",
                                  "mixed": False})()
            self.assertEqual(cluster.cmd_plan(args), 1)
            args.mixed = True
            self.assertEqual(cluster.cmd_plan(args), 0)
        finally:
            os.unlink(path)


class Ledger(unittest.TestCase):
    """The taxonomy is closed on purpose; a free-text cause is one nobody can count."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        os.chdir(self.cwd)

    @staticmethod
    def _args(**kw):
        base = dict(id="x", cause="ceiling-too-low", what="w", settled_by="s",
                    cost=None, reopen_if=None, date=None)
        base.update(kw)
        return type("A", (), base)()

    def test_an_unknown_cause_is_refused_and_the_taxonomy_is_printed(self):
        self.assertEqual(ledger.cmd_kill(self._args(cause="something-new")), 2)

    def test_a_known_cause_is_recorded_under_the_working_directory(self):
        self.assertEqual(ledger.cmd_kill(self._args(id="a")), 0)
        self.assertTrue(os.path.exists(os.path.join("archive", "killed.json")))

    def test_the_same_direction_cannot_be_killed_twice(self):
        self.assertEqual(ledger.cmd_kill(self._args(id="a")), 0)
        self.assertEqual(ledger.cmd_kill(self._args(id="a")), 1)

    def test_a_defect_needs_a_layer_that_exists(self):
        args = type("A", (), dict(id="d", missed_by="nobody", what="w", why="y",
                                  check=None, date=None))()
        self.assertEqual(ledger.cmd_defect(args), 2)

    def test_a_defect_without_a_check_is_recorded_as_not_converting(self):
        args = type("A", (), dict(id="d", missed_by="mechanical", what="w", why="y",
                                  check=None, date=None))()
        self.assertEqual(ledger.cmd_defect(args), 0)
        with open(os.path.join("archive", "ledger.json"), encoding="utf-8") as fh:
            self.assertFalse(json.load(fh)["defects"][0]["converts"])

    def test_the_shipped_taxonomy_is_found_from_anywhere(self):
        self.assertTrue(os.path.exists(ledger.CAUSES), ledger.CAUSES)
        self.assertGreaterEqual(len(ledger._causes()), 10)


class Reach(unittest.TestCase):
    """A body that is a bot wall must not be classified as content.

    This is the tier that matters: the request succeeded, the status code is
    fine, and anything checking only the status code will feed a challenge page
    into a literature step as though it were a paper.
    """

    def test_a_challenge_body_is_not_open(self):
        for marker in ("Just a moment...", "Checking your browser before",
                       "Please enable JavaScript to continue"):
            self.assertTrue(any(m in marker.lower() for m in reach.CHALLENGE_MARKERS),
                            f"{marker!r} would be read as content")

    def test_ordinary_content_is_not_a_challenge(self):
        body = "<html><body><h1>On the electrodynamics of moving bodies</h1></body></html>"
        self.assertFalse(any(m in body.lower() for m in reach.CHALLENGE_MARKERS))

    def test_rate_limiting_is_not_the_same_as_unavailable(self):
        import inspect
        src = inspect.getsource(reach._fetch)
        self.assertIn("429", src)
        self.assertIn("not the same as unavailable", src)

    def test_the_default_target_list_covers_the_indexes_the_pipeline_needs(self):
        for host in ("api.openalex.org", "arxiv.org", "doi.org"):
            self.assertIn(host, reach.DEFAULT_TARGETS)


class Stats(unittest.TestCase):
    """Checked against figures an independent implementation published."""

    def test_selftest_passes(self):
        self.assertEqual(stats._selftest(), 0)

    def test_the_interval_is_exact_not_normal(self):
        # at the end of the range the normal approximation goes outside [0, 1]
        lo, hi = stats.clopper_pearson(80, 80)
        self.assertEqual(hi, 1.0)
        self.assertGreater(lo, 0.95)

    def test_by_is_never_more_liberal_than_bh(self):
        ps = [0.0001, 0.006, 0.02, 0.04, 0.2, 0.9]
        self.assertTrue(stats.benjamini_yekutieli(ps) <= stats.benjamini_hochberg(ps))

    def test_mcnemar_with_no_discordant_pairs_is_one(self):
        self.assertEqual(stats.mcnemar_exact(0, 0), 1.0)

    def test_the_two_arms_of_the_real_comparison_reproduce(self):
        """The numbers this repository quotes elsewhere, recomputed here."""
        self.assertEqual(tuple(round(v * 100, 2) for v in stats.clopper_pearson(69, 80)),
                         (76.73, 92.93))
        self.assertEqual(tuple(round(v * 100, 2) for v in stats.clopper_pearson(72, 80)),
                         (81.24, 95.58))
        self.assertAlmostEqual(stats.mcnemar_exact(4, 7), 0.5488, places=4)


class Noise(unittest.TestCase):
    def test_name_value_lines_are_parsed(self):
        self.assertEqual(noise.parse("accuracy 0.75\nn 541"), {"accuracy": 0.75, "n": 541.0})

    def test_a_flat_json_object_is_parsed(self):
        self.assertEqual(noise.parse('{"acc": 0.5, "name": "x", "ok": true}'), {"acc": 0.5})

    def test_prose_is_ignored_rather_than_guessed_at(self):
        self.assertEqual(noise.parse("scoring 541 prompts, please wait"), {})

    def test_a_scorer_that_moves_is_reported_and_one_that_does_not_is_not(self):
        import io
        from contextlib import redirect_stdout

        def run(cmd):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = noise.main(["--n", "4", "--command", cmd])
            return rc, buf.getvalue()

        rc, out = run(f'{sys.executable} -c "print(\'acc 0.75\')"')
        self.assertEqual(rc, 0)
        self.assertIn("Nothing moved", out)

        rc, out = run(f'{sys.executable} -c "import random;'
                      f' print(f\'acc {{random.choice([0.75, 0.76])}}\')"')
        self.assertEqual(rc, 0)

    def test_a_command_that_fails_is_not_a_measurement(self):
        rc = noise.main(["--n", "2", "--command", f'{sys.executable} -c "import sys;sys.exit(3)"'])
        self.assertEqual(rc, 2)


class Scaffold(unittest.TestCase):
    def test_the_gate_section_comes_first_and_is_empty(self):
        d = tempfile.mkdtemp()
        self.assertEqual(scaffold.main(["--dir", d, "--name", "t"]), 0)
        body = open(os.path.join(d, "PROJECT.md"), encoding="utf-8").read()
        first = [ln for ln in body.splitlines() if ln.startswith("## ")][0]
        self.assertIn("gate", first.lower(),
                      "the first section of a project document must be the gate")
        self.assertIn("|  |  |", body.replace(" | | |", " |  |  |"),
                      "the gate table must ship empty")

    def test_it_refuses_to_overwrite_without_force(self):
        d = tempfile.mkdtemp()
        self.assertEqual(scaffold.main(["--dir", d]), 0)
        self.assertEqual(scaffold.main(["--dir", d]), 1)
        self.assertEqual(scaffold.main(["--dir", d, "--force"]), 0)

    def test_raw_generations_are_gitignored_but_scored_tables_are_not(self):
        d = tempfile.mkdtemp()
        scaffold.main(["--dir", d])
        gi = open(os.path.join(d, ".gitignore"), encoding="utf-8").read()
        self.assertIn("generations*.jsonl", gi)
        self.assertNotIn("per_prompt", gi)


class Attach(unittest.TestCase):
    def test_every_stage_is_discoverable_with_a_title(self):
        found = attach.stages()
        self.assertGreaterEqual(len(found), 7)
        for name, title, _d, _notes in found:
            self.assertTrue(title, f"{name} has no title line")

    def test_linking_is_idempotent(self):
        d = tempfile.mkdtemp()
        self.assertEqual(attach.main(["--dir", d]), 0)
        first = sorted(os.listdir(os.path.join(d, ".claude", "skills")))
        self.assertEqual(attach.main(["--dir", d]), 0)
        self.assertEqual(sorted(os.listdir(os.path.join(d, ".claude", "skills"))), first)
        self.assertTrue(all(os.path.islink(os.path.join(d, ".claude", "skills", n))
                            for n in first), "stages must be linked, not copied")


class GateRecord(unittest.TestCase):
    def test_the_verdict_goes_into_the_gate_section_not_the_end_of_the_file(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "PROJECT.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# p\n\n## 1. The gate\n\n_(paste it here)_\n\n## 2. Later\n\nkeep me\n")
        go, lines, facts = verdict(0.50, 0.75, 0.011, None, None, None, 2.0)
        gate_mod.record(p, lines, go, facts)
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        head = text.index("## 1. The gate")
        nxt = text.index("## 2. Later")
        self.assertIn("Verdict: GO", text[head:nxt], "the verdict landed outside the gate section")
        self.assertIn("keep me", text, "a later section was destroyed")
        self.assertNotIn("_(paste it here)_", text, "the template was left next to the verdict")

    def test_a_no_go_records_what_blocked_it_and_where_it_goes(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "PROJECT.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# p\n\n## The gate\n\n_(here)_\n")
        go, lines, facts = verdict(0.812, 0.830, 0.019, None, None, None, 2.0)
        self.assertFalse(go)
        gate_mod.record(p, lines, go, facts)
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("NO-GO", text)
        self.assertIn("blocking:", text)
        self.assertIn("ledger kill", text)

    def test_a_document_with_no_gate_section_is_not_silently_rewritten(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "PROJECT.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# p\n\n## Notes\n\nx\n")
        before = open(p, encoding="utf-8").read()
        msg = gate_mod.record(p, ["a"], True, {"blocking": []})
        self.assertIn("no section", msg)
        self.assertEqual(open(p, encoding="utf-8").read(), before)



class Check(unittest.TestCase):
    """The sweep, and the three ways a sweep lies: a vacuous pass, a false
    accusation, and an exemption that quietly disarms the check."""

    def _proj(self):
        d = tempfile.mkdtemp()
        for sub in ("prereg", "results", "archive"):
            os.makedirs(os.path.join(d, sub))
        return d

    def _seal(self, path):
        import hashlib
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        with open(os.path.splitext(path)[0] + ".sha256", "w", encoding="utf-8") as fh:
            fh.write(f"{h}  {os.path.basename(path)}\n")

    def test_an_empty_project_is_not_all_green(self):
        rows = check.run(self._proj())
        self.assertFalse(any(r["verdict"] == check.OK for r in rows),
                         "a project with nothing in it must not report passes")
        self.assertTrue(all(r["verdict"] in (check.NA, check.FAIL) for r in rows))

    def test_na_is_reported_as_loudly_as_a_pass(self):
        out = check.report(check.run(self._proj()), ".")
        self.assertIn("not applicable", out)
        self.assertIn("`n/a` is not a pass", out)

    def test_results_without_a_preregistration_fail(self):
        d = self._proj()
        with open(os.path.join(d, "results", "metrics_run1.json"), "w", encoding="utf-8") as fh:
            json.dump({"acc": 0.5}, fh)
        row = next(r for r in check.run(d) if r["check"] == "prereg")
        self.assertEqual(row["verdict"], check.FAIL)

    def test_a_document_cannot_seal_itself(self):
        """A sha256 inside a document is a digest of something else."""
        d = self._proj()
        p = os.path.join(d, "prereg", "PREREG_a.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# plan\n\nThe dataset sha256 is " + "0" * 64 + "\n")
        self.assertIsNone(check._seal_for(p, open(p, encoding="utf-8").read()),
                          "an inline digest was accepted as a self-seal")

    def test_a_seal_quoted_by_a_later_document_counts(self):
        import hashlib
        d = self._proj()
        p = os.path.join(d, "prereg", "PREREG_a.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# plan a\n\n## What changes\n\nthe budget\n")
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        with open(os.path.join(d, "prereg", "PREREG_b.md"), "w", encoding="utf-8") as fh:
            fh.write(f"# amendment\n\nThis amends `PREREG_a.md`, sha256 `{h}`.\n")
        self.assertIn("PREREG_b.md", check._seal_for(p, open(p, encoding="utf-8").read()))

    def test_a_stale_quoted_seal_does_not_count(self):
        d = self._proj()
        p = os.path.join(d, "prereg", "PREREG_a.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# plan a\n")
        with open(os.path.join(d, "prereg", "PREREG_b.md"), "w", encoding="utf-8") as fh:
            fh.write("This amends `PREREG_a.md`, sha256 `" + "a" * 64 + "`.\n")
        self.assertIsNone(check._seal_for(p, open(p, encoding="utf-8").read()),
                          "a quoted digest that does not match was accepted")

    def test_a_plan_written_to_another_template_is_not_accused_of_being_empty(self):
        d = self._proj()
        p = os.path.join(d, "prereg", "PREREG_x.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# plan\n\n## Fixed settings\n\ngreedy, seed 0\n\n"
                     "## The two arms\n\n4096 and 8192\n")
        self._seal(p)
        row = next(r for r in check.run(d) if r["check"] == "prereg")
        self.assertEqual(row["verdict"], check.NA)
        self.assertNotIn("empty", row["detail"])

    def test_a_preregistration_is_only_compared_with_results_it_names(self):
        self.assertEqual(check._tag("prereg/PREREG_run3_addendum_3d.md"), "run3")
        self.assertEqual(check._tag("PREREG_budget.md"), "budget")

    def test_a_waiver_must_carry_a_reason(self):
        d = self._proj()
        with open(os.path.join(d, "results", "m.json"), "w", encoding="utf-8") as fh:
            json.dump({"acc": 1}, fh)
        with open(os.path.join(d, "archive", "waivers.json"), "w", encoding="utf-8") as fh:
            json.dump({"noise": "", "prereg": "measured bit-exact instead"}, fh)
        rows = {r["check"]: r for r in check.run(d)}
        self.assertEqual(rows["noise"]["verdict"], check.FAIL,
                         "an empty reason disarmed the check")
        self.assertEqual(rows["prereg"]["verdict"], check.WAIVED)

    def test_a_waived_row_still_prints_its_reason_every_time(self):
        d = self._proj()
        with open(os.path.join(d, "results", "m.json"), "w", encoding="utf-8") as fh:
            json.dump({"acc": 1}, fh)
        with open(os.path.join(d, "archive", "waivers.json"), "w", encoding="utf-8") as fh:
            json.dump({"prereg": "a demonstration, not a test against a threshold"}, fh)
        out = check.report(check.run(d), d)
        self.assertIn("a demonstration, not a test against a threshold", out)
        self.assertIn("waived", out)

    def test_a_waiver_cannot_turn_a_pass_or_an_na_into_something_else(self):
        d = self._proj()
        with open(os.path.join(d, "archive", "waivers.json"), "w", encoding="utf-8") as fh:
            json.dump({"gate": "not applicable, honest", "private": "trust me"}, fh)
        rows = {r["check"]: r for r in check.run(d)}
        self.assertEqual(rows["gate"]["verdict"], check.NA, "a waiver rewrote an n/a")

    def test_a_private_path_in_a_tracked_file_is_caught(self):
        # Composed rather than written out: a fixture for a scanner must not be
        # a hit for that scanner in its own repository, or the check fires on
        # its own test and the only way out is an exemption - and an exemption
        # written for one file is how a repository stops checking itself.
        bait = "/" + "public/home/" + "someuser" + "/project"
        d = self._proj()
        with open(os.path.join(d, "notes.md"), "w", encoding="utf-8") as fh:
            fh.write(f"run it from {bait}\n")
        row = next(r for r in check.run(d) if r["check"] == "private")
        self.assertEqual(row["verdict"], check.FAIL)
        self.assertIn("notes.md", row["detail"])

    def test_a_check_that_raises_is_a_failure_not_a_pass(self):
        broken = [("boom", "does it explode", lambda root: 1 / 0)]
        saved = check.CHECKS
        try:
            check.CHECKS = broken
            row = check.run(self._proj())[0]
        finally:
            check.CHECKS = saved
        self.assertEqual(row["verdict"], check.FAIL)
        self.assertIn("the check itself raised", row["detail"])



class Probe(unittest.TestCase):
    """What the machine can do, and - harder - what the report is allowed to claim."""

    def test_a_module_name_matches_a_segment_not_a_substring(self):
        self.assertTrue(probe._segment_match("compiler/gcc/11.3.0", "gcc"))
        self.assertTrue(probe._segment_match("apps/gromacs/2025.1-4090", "gromacs"))
        # the noise case: a substring match buries the real hit under false ones
        self.assertFalse(probe._segment_match("apps/amber/24-gcc-openmpi", "gcc"))
        self.assertFalse(probe._segment_match("mathlib/fftw/3.3.9", "ff"))

    def test_an_executable_below_path_depth_is_found(self):
        d = tempfile.mkdtemp()
        deep = os.path.join(d, "share", "group", "tools", "lo", "opt", "program")
        os.makedirs(deep)
        exe = os.path.join(deep, "soffice")
        with open(exe, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\n")
        os.chmod(exe, 0o755)
        found, _roots, trunc = probe.find_off_path(["soffice"], [d], budget=30)
        self.assertFalse(trunc)
        self.assertIn("soffice", found, "an install below PATH depth was missed")
        self.assertEqual(found["soffice"][0], exe)

    def test_a_pruned_directory_is_not_searched(self):
        d = tempfile.mkdtemp()
        junk = os.path.join(d, "x", "site-packages", "bin")
        os.makedirs(junk)
        exe = os.path.join(junk, "ninja")
        with open(exe, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\n")
        os.chmod(exe, 0o755)
        found, _r, _t = probe.find_off_path(["ninja"], [d], budget=30)
        self.assertEqual(found, {})

    def test_a_search_that_ran_out_of_time_is_not_an_absence(self):
        d = tempfile.mkdtemp()
        found, _r, truncated = probe.find_off_path(["anything"], [d], budget=0)
        self.assertTrue(truncated, "a timed-out crawl must be marked, not reported as clean")
        self.assertEqual(found, {})

    def test_the_report_says_where_it_looked_whenever_it_says_not_found(self):
        d = {"host": "h", "gpus": None, "memory": {"total_gb": None, "shm": None,
             "cpus": 4, "loadavg": None}, "disk": [], "modules": None,
             "tools": {"on_path": [], "off_path": {}, "absent": ["soffice"],
                       "searched": ["/opt"], "truncated": False, "uncrawled": []},
             "isolation": {"unprivileged_userns": False, "kvm": False,
                           "cgroup_v2_delegated": False}}
        out = probe.report(d)
        self.assertIn("not found", out)
        self.assertIn("/opt", out, "a negative that does not say where it looked is not a measurement")
        self.assertIn("statement about PATH", out)

    def test_a_truncated_report_offers_the_catalogue_instead_of_a_verdict(self):
        d = {"host": "h", "gpus": None, "memory": {"total_gb": None, "shm": None,
             "cpus": 4, "loadavg": None}, "disk": [], "modules": None,
             "tools": {"on_path": [], "off_path": {}, "absent": ["soffice"],
                       "searched": ["/opt"], "truncated": True,
                       "uncrawled": [{"path": "/shared", "size_gb": 4096}]}}
        d["isolation"] = {"unprivileged_userns": True, "kvm": False,
                          "cgroup_v2_delegated": False}
        out = probe.report(d)
        self.assertIn("RAN OUT OF TIME", out)
        self.assertIn("module avail", out)
        self.assertIn("/shared", out)
        self.assertIn("4 TB", out)

    def test_an_uncrawled_mount_is_listed_once_and_only_if_unsearched(self):
        rows = probe.uncrawled_mounts(["/"], min_gb=1)
        self.assertEqual(rows, [], "everything is under / and / was searched")

    def test_a_tool_asked_for_twice_is_reported_once(self):
        t = probe.tools(extra=["git", "git"], roots=["/nonexistent-xyz"], budget=5)
        names = [x["name"] for x in t["on_path"]] + t["absent"]
        self.assertEqual(len(names), len(set(names)))



class Shard(unittest.TestCase):
    """Ownership, and the restart that silently loses items."""

    def test_ownership_is_a_partition_of_the_full_list(self):
        items = list(range(2638))
        parts = [shard.owned(items, i, 5) for i in range(5)]
        flat = [x for p in parts for x in p]
        self.assertEqual(sorted(flat), items)
        self.assertEqual(len(flat), len(set(flat)), "an item is owned twice")

    def test_slicing_after_the_done_filter_loses_and_duplicates_items(self):
        """The bug this tool exists for, demonstrated rather than asserted.

        Two shards restart at different points. Slicing the REMAINING items
        makes ownership depend on progress; slicing the full list does not.
        """
        items = list(range(20))
        done = {0: set(range(0, 8)), 1: set(range(0, 3))}   # shard 0 got further

        wrong = {}
        for i in (0, 1):
            remaining = [x for x in items if x not in done[i]]
            wrong[i] = set(remaining[i::2])
        overlap = wrong[0] & wrong[1]
        covered = wrong[0] | wrong[1] | done[0] | done[1]
        self.assertTrue(overlap, "the wrong order should produce items owned twice")
        self.assertTrue(set(items) - covered, "the wrong order should orphan items")

        right = {i: set(shard.owned(items, i, 2)) for i in (0, 1)}
        self.assertEqual(right[0] & right[1], set(), "correct order overlapped")
        self.assertEqual(right[0] | right[1], set(items), "correct order orphaned an item")

    def test_a_shard_index_out_of_range_is_refused(self):
        with self.assertRaises(ValueError):
            shard.owned([1, 2, 3], 5, 5)
        with self.assertRaises(ValueError):
            shard.owned([1, 2, 3], -1, 3)

    def test_merge_refuses_two_answers_for_one_item(self):
        d = tempfile.mkdtemp()
        a = os.path.join(d, "a.jsonl")
        b = os.path.join(d, "b.jsonl")
        with open(a, "w", encoding="utf-8") as fh:
            fh.write('{"id":"q1","ans":"A"}\n')
        with open(b, "w", encoding="utf-8") as fh:
            fh.write('{"id":"q1","ans":"B"}\n')
        rows, clashes, _ = shard.merge([a, b])
        self.assertEqual(len(clashes), 1)
        self.assertEqual(clashes[0][3], ["ans"], "the clash must name the field")
        self.assertEqual(shard.main(["merge", a, b]), 1)

    def test_an_identical_duplicate_is_not_a_clash(self):
        """Shard files are often pre-seeded with what an earlier run produced,
        so the same id legitimately appears twice. Only disagreement is a
        problem."""
        d = tempfile.mkdtemp()
        a, b = (os.path.join(d, n) for n in ("a.jsonl", "b.jsonl"))
        for p in (a, b):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write('{"id":"q1","ans":"A"}\n')
        rows, clashes, _ = shard.merge([a, b])
        self.assertEqual(clashes, [])
        self.assertEqual(len(rows), 1)

    def test_a_hole_is_reported_because_no_shard_file_shows_it(self):
        d = tempfile.mkdtemp()
        a = os.path.join(d, "a.jsonl")
        with open(a, "w", encoding="utf-8") as fh:
            fh.write('{"id":"q1"}\n{"id":"q2"}\n')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = shard.main(["merge", a, "--expect", "5"])
        self.assertEqual(rc, 1)
        self.assertIn("SHORT BY 3", out.getvalue())

    def test_more_items_than_expected_is_also_refused(self):
        d = tempfile.mkdtemp()
        a = os.path.join(d, "a.jsonl")
        with open(a, "w", encoding="utf-8") as fh:
            fh.write('{"id":"q1"}\n{"id":"q2"}\n')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = shard.main(["merge", a, "--expect", "1"])
        self.assertEqual(rc, 1)
        self.assertIn("MORE THAN EXPECTED", out.getvalue())

    def test_own_skips_what_is_done_without_changing_what_is_owned(self):
        d = tempfile.mkdtemp()
        allf = os.path.join(d, "all.jsonl")
        with open(allf, "w", encoding="utf-8") as fh:
            for i in range(20):
                fh.write(json.dumps({"id": f"q{i}"}) + "\n")
        donef = os.path.join(d, "done.jsonl")
        with open(donef, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"id": "q3"}) + "\n")     # q3 is shard 3 of 5's
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            shard.main(["own", "--items", allf, "--shard", "3/5", "--done", donef])
        self.assertIn("owns 4 of 20", out.getvalue())
        self.assertIn("1 already done", out.getvalue())
        self.assertIn("3 to do", out.getvalue())

    def test_plan_states_the_rule_that_has_to_be_in_the_harness(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            shard.main(["plan", "--items", "100", "--shards", "4"])
        text = out.getvalue()
        self.assertIn("BEFORE the already-done filter", text)
        self.assertIn("[25, 25, 25, 25]", text)



class Watch(unittest.TestCase):
    """The watcher's own failure modes.

    Two of these are regressions for bugs this file found: a process that has
    exited but not been reaped still answers `os.kill(pid, 0)`, so the first
    version called a dead job alive; and a child that buffers its output looks
    exactly like a child that has produced nothing.
    """

    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.d)

    def tearDown(self):
        os.chdir(self.cwd)

    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = watch.main(argv)
        return rc, out.getvalue()

    def test_a_job_that_dies_at_once_is_not_reported_alive(self):
        rc, out = self._run(["start", "--name", "d", "--alive-after", "3", "--",
                             sys.executable, "-c", "raise SystemExit('weights not found')"])
        self.assertEqual(rc, 1)
        self.assertIn("ALREADY GONE", out)
        self.assertNotIn("still alive", out)       # the zombie regression
        self.assertIn("weights not found", out)    # its log, not just a verdict

    def test_the_death_is_recorded_where_a_later_session_will_find_it(self):
        self._run(["start", "--name", "d", "--alive-after", "3", "--",
                   sys.executable, "-c", "raise SystemExit(1)"])
        flag = os.path.join("archive", "runs", "d.DONE")
        self.assertTrue(os.path.exists(flag), "no flag file: the watch dies with the session")
        with open(flag, encoding="utf-8") as fh:
            self.assertIn("died-before", json.load(fh)["verdict"])

    def test_a_live_job_shows_the_config_echoed_in_its_log_head(self):
        rc, out = self._run(["start", "--name", "a", "--alive-after", "3", "--",
                             sys.executable, "-u", "-c",
                             "print('lr=3e-4 epochs=30'); import time; time.sleep(30)"])
        self.assertEqual(rc, 0)
        self.assertIn("still alive", out)
        self.assertIn("lr=3e-4 epochs=30", out)
        self.assertNotIn("BUFFERING", out)
        os.kill(watch._read("a")["pid"], 9)

    def test_an_empty_log_head_is_called_buffering_not_silence(self):
        rc, out = self._run(["start", "--name", "b", "--alive-after", "3", "--",
                             sys.executable, "-c",
                             "print('lr=3e-4'); import time; time.sleep(30)"])
        self.assertEqual(rc, 0)
        self.assertIn("BUFFERING", out)
        self.assertIn("PYTHONUNBUFFERED=1", out)
        os.kill(watch._read("b")["pid"], 9)

    def test_status_calls_trouble_in_the_log_a_failure(self):
        self._run(["start", "--name", "t", "--alive-after", "3", "--",
                   sys.executable, "-u", "-c",
                   "print('step 1'); raise MemoryError('CUDA out of memory')"])
        rc, out = self._run(["status", "--name", "t"])
        self.assertEqual(rc, 1, "an OOM in the log must not be reported as a clean end")
        self.assertIn("TROUBLE IN THE LOG", out)
        self.assertIn("SCORED", out)   # exited != finished
        with open(os.path.join("archive", "runs", "t.DONE"), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["verdict"], "trouble-in-log")

    def test_a_clean_end_is_recorded_as_a_clean_end(self):
        self._run(["start", "--name", "c", "--alive-after", "3", "--",
                   sys.executable, "-u", "-c", "print('wrote metrics.json')"])
        rc, out = self._run(["status", "--name", "c"])
        self.assertEqual(rc, 0)
        self.assertIn("ended", out)
        self.assertNotIn("TROUBLE", out)

    def test_a_name_is_not_silently_reused(self):
        self._run(["start", "--name", "x", "--alive-after", "3", "--",
                   sys.executable, "-c", "pass"])
        rc, out = self._run(["start", "--name", "x", "--alive-after", "3", "--",
                             sys.executable, "-c", "pass"])
        self.assertEqual(rc, 1)
        self.assertIn("--force", out)

    def test_an_empty_command_is_refused(self):
        self.assertEqual(watch.main(["start", "--name", "n"]), 2)



if __name__ == "__main__":
    unittest.main(verbosity=2)
