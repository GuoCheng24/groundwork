#!/usr/bin/env python3
"""The exact tests this pipeline keeps asking for, so nobody has to re-implement them.

Every stage note that says "report an exact interval" or "report the discordant
counts" is asking for something a four-line script gets subtly wrong, so the
four-line script is here and it is checked against published figures.

    groundwork ci 69 80                  # exact binomial interval
    groundwork mcnemar 4 7               # exact paired test, discordant counts
    groundwork mde --se 0.019            # what this split can resolve
    groundwork fdr p.txt                 # BH and BY side by side

No dependencies: the binomial interval is obtained by inverting the tails
numerically rather than by importing a statistics package, and the paired test
is an exact binomial tail.
"""
from __future__ import annotations

import argparse
import sys
from math import comb, exp, fsum, lgamma, log, log1p

Z80, Z95 = 0.8416, 1.9600


def _log_pmf(i, n, p):
    """log of the binomial pmf, via lgamma.

    Not `comb(n, i) * p**i * (1-p)**(n-i)`: `comb` is an exact integer, and at
    n = 2638 multiplying it by a float raises OverflowError. That version
    shipped and was only found by running the tool on a full benchmark - every
    earlier use had n of 541 or less.
    """
    if p <= 0.0:
        return 0.0 if i == 0 else -float("inf")
    if p >= 1.0:
        return 0.0 if i == n else -float("inf")
    return (lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1)
            + i * log(p) + (n - i) * log1p(-p))


def binom_cdf(p, k, n):
    """P(X <= k) for X ~ Binomial(n, p), summed from the shorter tail."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if k <= n // 2:
        return min(1.0, fsum(exp(_log_pmf(i, n, p)) for i in range(0, k + 1)))
    return max(0.0, 1.0 - fsum(exp(_log_pmf(i, n, p)) for i in range(k + 1, n + 1)))


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval. Not the normal approximation, which is wrong at the ends."""
    if n == 0:
        return (float("nan"), float("nan"))
    lo = hi = 0.0
    if k > 0:
        a, b = 0.0, 1.0
        for _ in range(100):          # 2^-100; double precision runs out long before
            m = (a + b) / 2
            a, b = (m, b) if 1 - binom_cdf(m, k - 1, n) < alpha / 2 else (a, m)
        lo = (a + b) / 2
    if k < n:
        a, b = 0.0, 1.0
        for _ in range(100):
            m = (a + b) / 2
            a, b = (m, b) if binom_cdf(m, k, n) > alpha / 2 else (a, m)
        hi = (a + b) / 2
    else:
        hi = 1.0
    return lo, hi


def mcnemar_exact(b, c):
    """Two-sided exact McNemar from the discordant counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # in log space for the same reason as the interval: sum(comb(...)) / 2**n
    # is an exact-integer division that overflows to a float at a few thousand
    # discordant pairs
    return min(1.0, 2 * binom_cdf(0.5, k, n))


def detectable_effect(se, power_z=Z80, alpha_z=Z95):
    return (power_z + alpha_z) * se


def benjamini_hochberg(ps, alpha=0.05):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    thresh, k = [alpha * (r + 1) / m for r in range(m)], 0
    for r, i in enumerate(order):
        if ps[i] <= thresh[r]:
            k = r + 1
    return {order[r] for r in range(k)}


def benjamini_yekutieli(ps, alpha=0.05):
    m = len(ps)
    c = sum(1.0 / i for i in range(1, m + 1))
    order = sorted(range(m), key=lambda i: ps[i])
    thresh, k = [alpha * (r + 1) / (m * c) for r in range(m)], 0
    for r, i in enumerate(order):
        if ps[i] <= thresh[r]:
            k = r + 1
    return {order[r] for r in range(k)}


def cmd_ci(a):
    lo, hi = clopper_pearson(a.k, a.n, a.alpha)
    print(f"  {a.k}/{a.n} = {100 * a.k / a.n:.2f}%   "
          f"{100 * (1 - a.alpha):.0f}% CI [{100 * lo:.2f}, {100 * hi:.2f}]")
    if a.against is not None:
        # The interval is printed in percent, and the number a user has to hand
        # is as often a fraction. Guessing the unit produces a confident wrong
        # verdict - this printed "the interval EXCLUDES 0.8682" about an
        # interval of [85.93, 88.51], which contains 86.82. So it refuses
        # instead, and shows both readings.
        if 0.0 < a.against <= 1.0:
            as_pct = a.against * 100
            print(f"\n  --against {a.against} is ambiguous: the interval above is in PERCENT,")
            print(f"  so {a.against} reads as {a.against}% and is almost certainly meant as "
                  f"{as_pct:g}%.")
            print(f"    as {a.against:g}%   the interval {'contains' if lo * 100 <= a.against <= hi * 100 else 'excludes'} it")
            print(f"    as {as_pct:g}%   the interval {'contains' if lo * 100 <= as_pct <= hi * 100 else 'excludes'} it")
            print(f"  Say which: `--against {as_pct:g}` for the second.")
            return 2
        inside = lo * 100 <= a.against <= hi * 100
        print(f"  the interval [{100 * lo:.2f}, {100 * hi:.2f}]% "
              f"{'contains' if inside else 'EXCLUDES'} {a.against}%")
        print("\n  A verdict that rests on an interval boundary is a verdict that a second"
              "\n  arm can flip without being distinguishable from the first. If you are"
              "\n  about to publish one, run the second arm.")
    return 0


def cmd_mcnemar(a):
    p = mcnemar_exact(a.b, a.c)
    n = a.b + a.c
    print(f"  discordant b = {a.b}, c = {a.c}  (n = {n})")
    print(f"  exact two-sided p = {p:.4f}")
    if n < a.min_pairs:
        print(f"\n  {n} discordant pairs is few. Report the counts, not only the p-value,")
        print(f"  and say UNDERPOWERED rather than 'no difference' if your pre-registration")
        print(f"  set a floor you have not met (this one is --min-pairs {a.min_pairs}).")
    return 0


def cmd_mde(a):
    mde = detectable_effect(a.se)
    print(f"  one standard error       {a.se:.4f}")
    print(f"  smallest detectable      {mde:.4f}   (80% power, two-sided 0.05)")
    if a.effect is not None:
        ratio = (a.se / (a.effect / (Z80 + Z95))) ** 2
        print(f"  to resolve {a.effect:.4f} this split must grow about {ratio:.1f}x")
    return 0


def cmd_fdr(a):
    ps = []
    with open(a.path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                ps.append(float(line.split()[-1]))
    bh, by = benjamini_hochberg(ps, a.alpha), benjamini_yekutieli(ps, a.alpha)
    print(f"  {len(ps)} p-values at alpha = {a.alpha}")
    print(f"  Benjamini-Hochberg   rejects {len(bh)}")
    print(f"  Benjamini-Yekutieli  rejects {len(by)}")
    if bh - by:
        print(f"  {len(bh - by)} rejection(s) survive BH and not BY")
    print("""
  BH controls the false discovery rate under independence and under positive
  regression dependence. Under CORRELATED TWO-SIDED tests - which is what a few
  hundred correlated features and two-sided comparisons give you - that
  guarantee does not hold. If you need the guarantee, report BY, e-BH or
  knockoffs, and say which one you used.""")
    return 0


def _selftest():
    """Against figures published from an independent implementation."""
    checks = [
        ("CI 28/32 = [71.0, 96.5]",
         tuple(round(v * 100, 1) for v in clopper_pearson(28, 32)) == (71.0, 96.5)),
        ("CI 69/80 = [76.73, 92.93]",
         tuple(round(v * 100, 2) for v in clopper_pearson(69, 80)) == (76.73, 92.93)),
        ("CI 72/80 = [81.24, 95.58]",
         tuple(round(v * 100, 2) for v in clopper_pearson(72, 80)) == (81.24, 95.58)),
        ("McNemar b=2 c=2 -> 1.000", round(mcnemar_exact(2, 2), 3) == 1.000),
        ("McNemar b=4 c=7 -> 0.549", round(mcnemar_exact(4, 7), 3) == 0.549),
        ("McNemar b=8 c=4 -> 0.388", round(mcnemar_exact(8, 4), 3) == 0.388),
        ("a wrong target is rejected", round(mcnemar_exact(0, 2), 3) != 1.000),
        ("BY is never more liberal than BH",
         benjamini_yekutieli([0.001, 0.02, 0.04, 0.3]) <= benjamini_hochberg([0.001, 0.02, 0.04, 0.3])),
    ]
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("ok   " if ok else "FAIL ") + n)
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundwork stats",
                                 description="The exact tests, so nobody re-implements them.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("ci", help="exact binomial interval")
    c.add_argument("k", type=int)
    c.add_argument("n", type=int)
    c.add_argument("--alpha", type=float, default=0.05)
    c.add_argument("--against", type=float, metavar="PERCENT",
                   help="a number to compare the interval with, IN PERCENT "
                        "(86.82, not 0.8682); a value in (0, 1] is refused as "
                        "ambiguous rather than guessed at")
    c.set_defaults(func=cmd_ci)
    m = sub.add_parser("mcnemar", help="exact paired test from the discordant counts")
    m.add_argument("b", type=int)
    m.add_argument("c", type=int)
    m.add_argument("--min-pairs", type=int, default=50)
    m.set_defaults(func=cmd_mcnemar)
    d = sub.add_parser("mde", help="what this split can resolve")
    d.add_argument("--se", type=float, required=True)
    d.add_argument("--effect", type=float, help="an effect you hope to detect")
    d.set_defaults(func=cmd_mde)
    f = sub.add_parser("fdr", help="BH and BY side by side, with the caveat")
    f.add_argument("path", help="one p-value per line")
    f.add_argument("--alpha", type=float, default=0.05)
    f.set_defaults(func=cmd_fdr)
    s = sub.add_parser("selftest", help="check against published figures")
    s.set_defaults(func=lambda a: _selftest())
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
