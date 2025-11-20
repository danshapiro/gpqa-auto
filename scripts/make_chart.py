"""
Render a horizontal bar chart of the latest GPQA Diamond scores.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path("data/gpqa_scores.json")
OUT_PATH = Path("img/gpqa_frontier.png")

DEFAULT_COLORS = {
    "OpenAI": "#0b70ff",
    "Google": "#e59b0f",
    "xAI": "#1a1a1a",
    "Anthropic": "#8c4bff",
    "Unknown": "#5c6b73",
}


def _load_df() -> pd.DataFrame:
    payload = json.loads(DATA_PATH.read_text())
    df = pd.DataFrame(payload.values())
    df = df.sort_values("score", ascending=True)
    return df


def _color_for(provider: str) -> str:
    return DEFAULT_COLORS.get(provider, DEFAULT_COLORS["Unknown"])


def main() -> None:
    df = _load_df()
    colors = [_color_for(p) for p in df["provider"]]

    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=220)
    ax.barh(df["model"], df["score"], color=colors)
    ax.set_xlabel("GPQA Diamond accuracy (%)")
    ax.set_xlim(60, max(df["score"].max() + 2, 92))
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.set_title("Frontier model GPQA Diamond scores", pad=12)

    for idx, score in enumerate(df["score"]):
        ax.text(score + 0.4, idx, f"{score:.1f}%", va="center", fontsize=9)

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH)
    print(f"[ok] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
