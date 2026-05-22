#!/usr/bin/env python3
"""Render v0.0.7 result panels as 16:9 slides for talk presentation.

Three slide types are supported:

- `delta`     — the "Does Vera beat Python / TypeScript?" horizontal-bar chart
                (the headline storytelling slide; Vera-wins read as green
                positive bars).
- `tiers`     — Flagship and Sonnet tier comparisons side-by-side, mirroring
                the top row of the documentation chart.
- `all-modes` — all 6 models × 4 modes (Vera, Vera NL, Python, TypeScript)
                in a single grouped-bar panel.

Standalone script — not part of the documentation chart-generation flow in
`plot_results.py`. Slide rendering has different typography and layout
requirements (slide-readable from the back of a room, single panel or
side-by-side per figure, landscape aspect) that don't belong in the README
artefact. Reuses palette + data extraction from `plot_results.py` so the
slide numbers match the README chart by construction.

The historical v0.0.7 model lineup is hard-coded here because the live
`plot_results.MODELS` registry now reflects the post-K2.6 lineup (PR #69)
— slide must match what was actually run in v0.0.7.

Usage:
    # Render all three by default
    python scripts/plot_slide.py
        # -> /tmp/vera-bench_slide_{delta,tiers,all-modes}.png

    # One at a time
    python scripts/plot_slide.py --type delta
    python scripts/plot_slide.py --type tiers
    python scripts/plot_slide.py --type all-modes

    # Custom output path (only with single --type)
    python scripts/plot_slide.py --type delta --output ~/Desktop/slide-3.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.plot_results import (  # noqa: E402
    BROWN_300,
    BROWN_500,
    BROWN_700,
    BROWN_900,
    COLORS,
    CREAM,
    FONT_BODY,
    FONT_HEADING,
    GREEN,
    RED,
    ModelSpec,
    extract_data,
)

# v0.0.7 historical lineup. Kept locally rather than imported from
# plot_results.MODELS because the live registry has since been updated
# (K2.6 in flagship, K2.5 in sonnet) — but the v0.0.7 chart needs the
# v0.0.7-era assignments to match the result files we're plotting.
MODELS_V_0_0_7: list[ModelSpec] = [
    ModelSpec("Claude Opus 4", "claude-opus-4-20250514", "flagship"),
    ModelSpec("GPT-4.1", "gpt-4.1-2025-04-14", "flagship"),
    ModelSpec("Kimi K2.5", "moonshot-kimi-k2.5", "flagship"),
    ModelSpec("Claude Sonnet 4", "claude-sonnet-4-20250514", "sonnet"),
    ModelSpec("GPT-4o", "gpt-4o", "sonnet"),
    ModelSpec("Kimi K2 Turbo", "moonshot-kimi-k2-turbo-preview", "sonnet"),
]

# Slide typography. Roughly 3× the README-chart sizes so the slide reads
# from the back of a room. Tier and all-modes panels use slightly smaller
# tick labels because they have more bars to label per panel.
TITLE_PT = 36
SUBTITLE_PT = 22
AXIS_LABEL_PT = 22
TICK_PT_LARGE = 22  # delta chart — 6 model rows
TICK_PT_MEDIUM = 20  # tier panels — 3 models per panel
TICK_PT_SMALL = 18  # all-modes — 6 models in one panel
BAR_LABEL_PT_LARGE = 22
BAR_LABEL_PT_MEDIUM = 18
BAR_LABEL_PT_SMALL = 14
LEGEND_PT = 20

# Slide background choices. All are light-theme variants — the text/spine
# colors inherited from plot_results.py (BROWN_*) work cleanly on any of
# these. A dark-mode background is not offered here because it would
# require cascading text-color inversion that's out of scope for the
# current talk's design language.
BACKGROUNDS = {
    "paper": "#FAF7F0",  # off-white — chosen default; soft, neutral
    "white": "#FFFFFF",  # pure white — high contrast, baseline
    "cream": "#FEEAD1",  # on-brand (veralang.dev palette)
    "light-grey": "#F4F4F2",  # neutral grey
}
DEFAULT_BACKGROUND = "paper"


def _patch_models_for_slide():
    """Temporarily swap plot_results.MODELS for the v0.0.7 lineup.

    extract_data() reads from the module-level MODELS in plot_results,
    so we patch it for the duration of the data load. Restored on exit.
    """
    import scripts.plot_results as pr

    original = pr.MODELS
    pr.MODELS = MODELS_V_0_0_7
    return pr, original


def _load_v0_0_7_data(version: str, results_dir: Path):
    """Load the v0.0.7 data once, patched against the historical lineup."""
    pr, original = _patch_models_for_slide()
    try:
        modes = ["Vera", "Vera NL", "Python", "TypeScript"]
        flagship, sonnet, warnings, _used = extract_data(results_dir, version, modes)
    finally:
        pr.MODELS = original

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(w)

    return flagship, sonnet


def _slide_rcparams():
    """rcParams shared across all slide types."""
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [FONT_BODY, "Inter", "Helvetica", "Arial"],
            "font.size": TICK_PT_LARGE,
            "text.color": BROWN_700,
            "axes.labelcolor": BROWN_500,
            "xtick.color": BROWN_500,
            "ytick.color": BROWN_500,
        }
    )


def _style_ax(ax):
    """Light visual frame so the bars carry the eye."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(BROWN_300)
    ax.spines["left"].set_color(BROWN_300)
    ax.tick_params(colors=BROWN_500)


# ----------------------------------------------------------------------
# Delta slide — the storytelling chart
# ----------------------------------------------------------------------


def render_delta(
    flagship: dict, sonnet: dict, output: Path, background: str = DEFAULT_BACKGROUND
) -> None:
    """The 'Does Vera beat …?' horizontal-bar chart at 16:9."""
    all_data = {**flagship, **sonnet}
    models = list(all_data.keys())
    comparison_modes = ["Python", "TypeScript"]

    deltas = {
        mode: [all_data[m]["Vera"] - all_data[m][mode] for m in models]
        for mode in comparison_modes
    }

    fig, ax = plt.subplots(figsize=(16, 9), dpi=180)

    y = np.arange(len(models))
    n = len(comparison_modes)
    height = 0.7 / n
    offsets = [(i - (n - 1) / 2) * height for i in range(n)]

    hatches = [None, "//"]
    alphas = [0.9, 0.6]

    for i, mode in enumerate(comparison_modes):
        d = deltas[mode]
        colors = [GREEN if v >= 0 else RED for v in d]
        bars = ax.barh(
            y + offsets[i],
            d,
            height,
            color=colors,
            edgecolor=CREAM,
            linewidth=0.8,
            alpha=alphas[i],
            hatch=hatches[i],
        )
        for bar, val in zip(bars, d):
            xpos = val + (1.2 if val >= 0 else -1.2)
            ha = "left" if val >= 0 else "right"
            sign = "+" if val > 0 else ""
            ax.text(
                xpos,
                bar.get_y() + bar.get_height() / 2,
                f"{sign}{val}",
                ha=ha,
                va="center",
                fontsize=BAR_LABEL_PT_LARGE,
                fontweight="bold",
                color=BROWN_700,
            )

    ax.axvline(x=0, color=BROWN_900, linewidth=2)
    ax.set_yticks(y)
    ax.set_yticklabels(models, fontsize=TICK_PT_LARGE)
    ax.set_xlabel(
        "Vera run_correct minus comparison language (percentage points)",
        fontsize=AXIS_LABEL_PT,
        color=BROWN_500,
        labelpad=12,
    )
    ax.set_title(
        "Does Vera beat Python / TypeScript?",
        fontsize=TITLE_PT,
        fontweight="bold",
        pad=24,
        fontfamily=FONT_HEADING,
        color=BROWN_900,
    )

    max_abs = max(
        (abs(v) for mode in comparison_modes for v in deltas[mode]),
        default=0,
    )
    limit = max(22, max_abs + 6)
    ax.set_xlim(-limit, limit)
    ax.invert_yaxis()
    ax.tick_params(axis="x", labelsize=TICK_PT_LARGE)

    _style_ax(ax)

    legend_handles = [
        Patch(facecolor="#888888", edgecolor=CREAM, alpha=alphas[0], label="vs Python"),
        Patch(
            facecolor="#aaaaaa",
            edgecolor=CREAM,
            alpha=alphas[1],
            hatch=hatches[1],
            label="vs TypeScript",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower right",
        fontsize=LEGEND_PT,
        framealpha=0.85,
        edgecolor=BROWN_300,
    )

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.95))
    _save(fig, output, background)


# ----------------------------------------------------------------------
# Tier comparison slide — Flagship and Sonnet panels side-by-side
# ----------------------------------------------------------------------


def _draw_tier_panel(ax, data: dict, title: str, comparison_modes: list[str]):
    """Grouped vertical bars: Vera vs each comparison language, per model."""
    models = list(data.keys())
    languages = ["Vera", *comparison_modes]
    x = np.arange(len(models))
    width = 0.8 / len(languages)

    for i, lang in enumerate(languages):
        values = [data[m][lang] for m in models]
        bars = ax.bar(
            x + i * width,
            values,
            width,
            label=lang,
            color=COLORS[lang],
            edgecolor=CREAM,
            linewidth=0.8,
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val}%",
                ha="center",
                va="bottom",
                fontsize=BAR_LABEL_PT_MEDIUM,
                fontweight="bold",
                color=BROWN_700,
            )

    ax.set_ylabel("run_correct (%)", fontsize=AXIS_LABEL_PT, color=BROWN_500)
    ax.set_title(
        title,
        fontsize=TITLE_PT - 4,
        fontweight="bold",
        pad=16,
        fontfamily=FONT_HEADING,
        color=BROWN_900,
    )
    ax.set_xticks(x + width * (len(languages) - 1) / 2)
    ax.set_xticklabels(models, fontsize=TICK_PT_MEDIUM)
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.tick_params(axis="y", labelsize=TICK_PT_MEDIUM)
    ax.axhline(y=100, color=BROWN_300, linestyle="--", linewidth=0.8, alpha=0.4)
    _style_ax(ax)
    ax.legend(
        loc="lower right", fontsize=LEGEND_PT, framealpha=0.85, edgecolor=BROWN_300
    )


def render_tiers(
    flagship: dict, sonnet: dict, output: Path, background: str = DEFAULT_BACKGROUND
) -> None:
    """Flagship + Sonnet tier comparisons side-by-side at 16:9."""
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 9), dpi=180)
    comparison_modes = ["Python", "TypeScript"]
    _draw_tier_panel(ax_left, flagship, "Flagship Tier", comparison_modes)
    _draw_tier_panel(ax_right, sonnet, "Sonnet Tier", comparison_modes)

    fig.suptitle(
        "run_correct by model (Vera vs Python vs TypeScript)",
        fontsize=TITLE_PT - 2,
        fontweight="bold",
        y=0.97,
        fontfamily=FONT_HEADING,
        color=BROWN_900,
    )

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.92))
    _save(fig, output, background)


# ----------------------------------------------------------------------
# All-modes slide — 6 models × 4 modes
# ----------------------------------------------------------------------


def render_all_modes(
    flagship: dict, sonnet: dict, output: Path, background: str = DEFAULT_BACKGROUND
) -> None:
    """Single panel showing Vera, Vera NL, Python, TypeScript for every model."""
    all_data = {**flagship, **sonnet}
    models = list(all_data.keys())
    modes = ["Vera", "Vera NL", "Python", "TypeScript"]

    fig, ax = plt.subplots(figsize=(16, 9), dpi=180)
    x = np.arange(len(models))
    width = 0.8 / len(modes)

    for i, mode in enumerate(modes):
        values = [all_data[m][mode] for m in models]
        bars = ax.bar(
            x + i * width,
            values,
            width,
            label=mode,
            color=COLORS[mode],
            edgecolor=CREAM,
            linewidth=0.8,
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val}",
                ha="center",
                va="bottom",
                fontsize=BAR_LABEL_PT_SMALL,
                fontweight="bold",
                color=BROWN_700,
            )

    ax.set_ylabel("run_correct (%)", fontsize=AXIS_LABEL_PT, color=BROWN_500)
    ax.set_title(
        "All Models × All Modes",
        fontsize=TITLE_PT,
        fontweight="bold",
        pad=20,
        fontfamily=FONT_HEADING,
        color=BROWN_900,
    )
    ax.set_xticks(x + width * (len(modes) - 1) / 2)
    ax.set_xticklabels(models, fontsize=TICK_PT_SMALL, rotation=12, ha="right")
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.tick_params(axis="y", labelsize=TICK_PT_SMALL)
    ax.axhline(y=100, color=BROWN_300, linestyle="--", linewidth=0.8, alpha=0.4)
    _style_ax(ax)
    ax.legend(
        loc="lower left",
        fontsize=LEGEND_PT,
        ncol=2,
        framealpha=0.85,
        edgecolor=BROWN_300,
    )

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.95))
    _save(fig, output, background)


# ----------------------------------------------------------------------
# Plumbing
# ----------------------------------------------------------------------


def _save(fig, output: Path, background: str = DEFAULT_BACKGROUND) -> None:
    """Tint the figure to the chosen background and write the PNG.

    The figure-level patch and every axes facecolor both need setting —
    matplotlib doesn't propagate one to the other, and the savefig
    facecolor kwarg only governs the area *outside* the axes box.
    """
    hex_ = BACKGROUNDS[background]
    fig.patch.set_facecolor(hex_)
    for ax in fig.axes:
        ax.set_facecolor(hex_)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, facecolor=hex_)
    print(f"Saved: {output}  (16×9, bg={background} {hex_})")
    plt.close(fig)


RENDERERS = {
    "delta": render_delta,
    "tiers": render_tiers,
    "all-modes": render_all_modes,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type",
        choices=[*RENDERERS.keys(), "all"],
        default="all",
        help="Which slide to render (default: all three).",
    )
    parser.add_argument(
        "--version",
        default="0.0.7",
        help="Bench version to plot (default: 0.0.7).",
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory containing JSONL result files.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output PNG path. Only valid with a single --type. "
            "Default: /tmp/vera-bench_slide_{type}.png"
        ),
    )
    parser.add_argument(
        "--background",
        choices=list(BACKGROUNDS),
        default=DEFAULT_BACKGROUND,
        help=(
            f"Slide background colour (default: {DEFAULT_BACKGROUND}). "
            "All choices are light themes — text/spine colours don't invert."
        ),
    )
    args = parser.parse_args()

    if args.output and args.type == "all":
        parser.error("--output is only valid when --type is a single slide type")

    _slide_rcparams()
    flagship, sonnet = _load_v0_0_7_data(args.version, Path(args.results_dir))

    types = list(RENDERERS) if args.type == "all" else [args.type]
    for t in types:
        output = (
            Path(args.output) if args.output else Path(f"/tmp/vera-bench_slide_{t}.png")
        )
        RENDERERS[t](flagship, sonnet, output, background=args.background)


if __name__ == "__main__":
    main()
