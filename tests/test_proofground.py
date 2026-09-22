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
sys.path.insert(0, os.path.join(ROOT, "tools"))

import cluster  # noqa: E402
import prereg  # noqa: E402
from gate import detectable_effect, required_se, verdict  # noqa: E402

IDENT = ["-c", "user.name=Guo Cheng",
         "-c", "user.email=224264187+GuoCheng24@users.noreply.github.com"]


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
            return subprocess.run([sys.executable, os.path.join(ROOT, "proofground.py"),
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
        subprocess.run(["git", *IDENT, "commit", "-qm", "x"], cwd=d, check=True)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
