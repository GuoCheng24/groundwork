"""The 1200x630 card GitHub shows when the link is shared.

The composition is the positioning: a full pipeline, and the first stage is the
one that refuses. Counts come from archive/causes-of-death.json and from the
skill tree, so the card cannot drift from what the repository contains.

Built through cardkit, which refuses to write a card that fails its own
legibility, contrast and collision audit at the ~360 px a link unfurl gives it.
Per-stage labels are impossible at that floor - a ten-character word needs more
width than a seventh of the canvas - so the strip carries the shape and one
label carries the argument.
"""
import collections
import glob
import json
import pathlib
import sys

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(pathlib.Path.home() / "bin"))
from cardkit import INK, MUTE, SANS, card  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
with open(ROOT / "archive" / "causes-of-death.json", encoding="utf-8") as fh:
    CAUSES = json.load(fh)["causes"]

EARLY_STAGES = {"00-gate", "10-direction"}
N_CAUSES = len(CAUSES)
N_EARLY = sum(1 for c in CAUSES if c["gate"].split("/")[0] in EARLY_STAGES)
N_STAGES = len(sorted(glob.glob(str(ROOT / "skills" / "*/"))))
N_NOTES = len(glob.glob(str(ROOT / "skills" / "*" / "*.md")))

ACCENT = "#1f6f6b"
WARN = "#b4562a"


def chart(ax, accent):
    # the pipeline strip: one block per stage, the first one refusing
    x0, x1, y0, h, gap = 0.78, 11.22, 2.78, 0.74, 0.11
    w = (x1 - x0 - gap * (N_STAGES - 1)) / N_STAGES
    for i in range(N_STAGES):
        x = x0 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.015,rounding_size=0.09",
                                    fc=WARN if i == 0 else accent, ec="none", zorder=3))

    ax.text(x0, 2.16, "NO-GO", fontsize=42, fontweight="bold", color=WARN,
            family=SANS, va="center")
    ax.text(x0 + 2.55, 2.16, "the stage other pipelines skip",
            fontsize=34, color=INK, family=SANS, va="center")
    ax.text(x0, 1.30, f"{N_STAGES} stages, {N_NOTES} notes, 6 tools, no dependencies",
            fontsize=34, color=MUTE, family=SANS, va="center")


if __name__ == "__main__":
    out = ROOT / ".github" / "assets" / "social-preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    card(out=str(out), accent=ACCENT, badge="gw",
         kicker="GROUNDWORK",
         headline="Most directions should not be started",
         evidence=f"{N_CAUSES} ways a direction dies, {N_EARLY} before you start",
         chart=chart,
         footer="github.com/GuoCheng24/groundwork",
         headline_size=44)
    print("wrote", out)
