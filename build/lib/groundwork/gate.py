#!/usr/bin/env python3
"""The gate a direction has to pass before it is allowed to cost a week.

Most of what an autonomous research pipeline can do cheaply is downstream:
survey, ideate, implement, write. The expensive failures are upstream, and they
are not subtle. A direction dies because the ceiling was never high enough,
because a trivial baseline nobody tried to tune absorbs the whole signal,
because a random arm beats every learned one, or because the null you measured
was your pipeline rather than the world. `archive/causes-of-death.json` records
ten of these with what each one cost.

Every one of them is detectable before the first real experiment, from four
numbers on the same split:

    baseline   the strongest trivial method, tuned as hard as the proposal
    oracle     a method given perfect access to whatever the proposal estimates
    se         the standard error of a difference on this split
    random     a shuffled or randomly-assigned arm

This computes what those four say and refuses the direction when they say no.
It is deliberately unaware of what the proposed method is: a gate that knows
what you are hoping for is not a gate.

    groundwork gate --baseline 0.812 --oracle 0.838 --se 0.019
    groundwork gate --config gate.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys

HEADROOM_MULTIPLE = 2.0          # headroom must be at least this many SEs wide
Z80, Z95 = 0.8416, 1.9600        # 80% power, 95% two-sided


def detectable_effect(se, power_z=Z80, alpha_z=Z95):
    """Smallest difference this split can resolve, at 80% power and alpha 0.05."""
    return (power_z + alpha_z) * se


def required_se(effect, power_z=Z80, alpha_z=Z95):
    """The SE a split would need for `effect` to be detectable."""
    return effect / (power_z + alpha_z)


def verdict(baseline, oracle, se, random_arm=None, positive_control=None,
            positive_control_floor=None, multiple=HEADROOM_MULTIPLE):
    """Decide, and say why. Returns (go: bool, lines: list[str], facts: dict)."""
    headroom = oracle - baseline
    mde = detectable_effect(se)
    lines, blocking = [], []
    facts = {
        "baseline": baseline, "oracle": oracle, "se": se,
        "headroom": headroom,
        "headroom_in_se": headroom / se if se else float("inf"),
        "minimum_detectable_effect": mde,
        "headroom_multiple_required": multiple,
    }

    lines.append(f"headroom            {headroom:+.4f}  (oracle {oracle:.4f} - baseline {baseline:.4f})")
    lines.append(f"one standard error  {se:.4f}")
    lines.append(f"headroom in SEs     {headroom / se:.2f}" if se else "headroom in SEs     undefined (se = 0)")
    lines.append(f"smallest detectable {mde:.4f}  (80% power, two-sided 0.05)")

    if headroom <= 0:
        blocking.append(
            "The oracle does not beat the baseline. There is nothing for a method to "
            "recover: whatever the proposal estimates, knowing it perfectly does not help here.")
    elif headroom < multiple * se:
        blocking.append(
            f"Headroom is {headroom / se:.2f} SE, under the {multiple:g} SE this gate requires. "
            f"Even a method that captured the entire gap would not separate from the baseline "
            f"on this split.")
    elif headroom < mde:
        blocking.append(
            f"Headroom {headroom:.4f} is smaller than the smallest effect this split can "
            f"resolve ({mde:.4f}). A perfect method would still be reported as null. "
            f"Fix the split before the method: n must grow by about "
            f"{(se / required_se(headroom)) ** 2:.1f}x.")
    else:
        share = mde / headroom
        lines.append(
            f"a method must capture   {share:.0%} of the headroom to be detectable at all")
        if share > 0.5:
            lines.append(
                "  that is more than half the gap - a demanding target, and worth "
                "deciding on before the work rather than after")

    if random_arm is not None:
        facts["random_arm"] = random_arm
        lines.append(f"random arm          {random_arm:.4f}")
        if random_arm >= baseline - se:
            blocking.append(
                f"A random arm scores {random_arm:.4f} against a baseline of {baseline:.4f}. "
                "Whatever this task measures, it is not something a learned policy has "
                "yet been shown to need.")

    if positive_control is not None:
        facts["positive_control"] = positive_control
        floor = positive_control_floor
        lines.append(f"positive control    {positive_control:.4f}"
                     + (f"  (must clear {floor:.4f})" if floor is not None else ""))
        if floor is not None and positive_control < floor:
            blocking.append(
                f"The positive control returns {positive_control:.4f}, under the {floor:.4f} it "
                "must clear. A null from this pipeline would measure the pipeline. Fix it "
                "before running anything you intend to believe.")

    facts["blocking"] = blocking
    facts["go"] = not blocking
    return (not blocking), lines, facts


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="groundwork gate",
        description="Refuse a direction whose ceiling, baseline or controls already answer it.")
    ap.add_argument("--config", help="JSON file with the same keys as the flags")
    ap.add_argument("--baseline", type=float, help="strongest trivial method, tuned")
    ap.add_argument("--oracle", type=float, help="method with perfect access to the quantity")
    ap.add_argument("--se", type=float, help="standard error of a difference on this split")
    ap.add_argument("--random", type=float, dest="random_arm",
                    help="a shuffled or randomly-assigned arm")
    ap.add_argument("--positive-control", type=float)
    ap.add_argument("--positive-control-floor", type=float)
    ap.add_argument("--multiple", type=float, default=HEADROOM_MULTIPLE)
    ap.add_argument("--json", help="write the decision here")
    a = ap.parse_args(argv)

    if a.config:
        with open(a.config, encoding="utf-8") as fh:
            cfg = json.load(fh)
        for k, v in cfg.items():
            key = {"random": "random_arm"}.get(k, k).replace("-", "_")
            if getattr(a, key, None) is None:
                setattr(a, key, v)

    missing = [n for n in ("baseline", "oracle", "se") if getattr(a, n) is None]
    if missing:
        ap.error("need " + ", ".join("--" + m for m in missing) + " (or --config)")
    if a.se < 0:
        ap.error("--se cannot be negative")

    go, lines, facts = verdict(a.baseline, a.oracle, a.se, a.random_arm,
                               a.positive_control, a.positive_control_floor, a.multiple)
    for ln in lines:
        print("  " + ln)
    print()
    if go:
        print("GO. Nothing here rules the direction out.")
        print("That is all this says. It does not say the idea is novel, that the")
        print("method will work, or that the result will be worth a paper - only that")
        print("the ceiling, the baseline and the controls have not already answered it.")
    else:
        print("NO-GO.")
        for b in facts["blocking"]:
            print("  * " + b)
        print()
        print("Record it in archive/ with the cause, so the next person who has this")
        print("idea - including you, in four months - finds the verdict before the work.")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, indent=1)
        print(f"\nwrote {a.json}")
    return 0 if go else 1


if __name__ == "__main__":
    sys.exit(main())
