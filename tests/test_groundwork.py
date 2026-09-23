"""Tests. The ones that matter assert a refusal.

A gate that has never been seen refusing is decoration, so every blocking path
here is exercised with an input built to trip it - and the boundary cases that
must still pass are exercised too, because a gate that refuses everything is
also decoration.
"""
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
from groundwork import prereg  # noqa: E402
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
