"""The 1200x630 card GitHub shows when the link is shared.

Read from archive/causes-of-death.json, so the chart cannot drift from the file
it summarises - and the shape it makes is the argument: of the ten ways a
direction dies, eight are catchable before the first real experiment.

Built through cardkit, which refuses to write a card that fails its own
legibility, contrast and collision audit at the ~360 px a link unfurl gives it.
"""
import collections
import json
import pathlib
import sys

from matplotlib.patches import Rectangle

sys.path.insert(0, str(pathlib.Path.home() / "bin"))
from cardkit import INK, SANS, card  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
with open(ROOT / "archive" / "causes-of-death.json", encoding="utf-8") as fh:
    CAUSES = json.load(fh)["causes"]

STAGE = {
    "00-gate": "before you start",
    "10-direction": "before you start",
    "20-experiment": "at the experiment",
    "30-claim": "at the write-up",
}
missing = sorted({c["gate"].split("/")[0] for c in CAUSES} - set(STAGE))
if missing:
    raise SystemExit(f"causes name stages with no card label: {missing}")

COUNTS = collections.Counter(STAGE[c["gate"].split("/")[0]] for c in CAUSES)
ORDER = ["before you start", "at the experiment", "at the write-up"]
ROWS = [(k, COUNTS[k]) for k in ORDER if COUNTS[k]]
TOTAL = sum(n for _k, n in ROWS)

ACCENT = "#7a4b1f"
EARLY = "#1f6f6b"


def chart(ax, accent):
    top, gap, end = 3.10, 0.90, 10.95
    labels = [ax.text(0.78, top - i * gap, name, fontsize=34, color=INK,
                      family=SANS, va="center")
              for i, (name, _n) in enumerate(ROWS)]
    ax.figure.canvas.draw()
    r = ax.figure.canvas.get_renderer()
    widest = max(t.get_window_extent(r).x1 for t in labels) / ax.figure.dpi
    x0 = widest + 0.30
    unit = (end - x0) / max(n for _k, n in ROWS)
    for i, (name, n) in enumerate(ROWS):
        y = top - i * gap
        colour = EARLY if name == "before you start" else accent
        ax.add_patch(Rectangle((x0, y - 0.22), n * unit, 0.44, fc=colour, ec="none"))
        ax.text(x0 + n * unit + 0.18, y, str(n), fontsize=34, fontweight="bold",
                color=colour, family=SANS, va="center")


if __name__ == "__main__":
    out = ROOT / ".github" / "assets" / "social-preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    card(out=str(out), accent=ACCENT, badge="pg",
         kicker="PROOFGROUND",
         headline="Most directions should not be started",
         evidence=f"{TOTAL} ways a direction dies, and where each is caught",
         chart=chart,
         footer="github.com/GuoCheng24/proofground",
         headline_size=44)
    print("wrote", out)
