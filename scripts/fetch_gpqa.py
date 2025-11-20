"""
Pull GPQA scores for frontier models from a few public benchmark posts.

Heuristics:
- Accept updates within 5 percentage points of the previously stored value,
  otherwise keep the old number to avoid bad scrapes.
- Store results in data/gpqa_scores.json with per-model metadata.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

DATA_PATH = Path("data/gpqa_scores.json")


@dataclass
class Source:
    name: str
    url: str
    candidates: List[str]


SOURCES: List[Source] = [
    Source(
        name="vals_ai_2025-09-20",
        url="https://www.vals.ai/benchmarks/gpqa-09-20-2025",
        candidates=["Grok 4", "GPT-5", "Gemini 2.5 Pro"],
    ),
    Source(
        name="moneycontrol_gemini3_announce",
        url=(
            "https://www.moneycontrol.com/technology/"
            "google-gemini-3-0-announced-here-s-how-it-compares-to-gemini-2-5-pro-and-gpt-5-1-article-13683635.html"
        ),
        candidates=["Gemini 3.0", "Gemini 2.5 Pro", "GPT-5.1"],
    ),
    Source(
        name="the_decoder_gpt5.1_launch",
        url="https://the-decoder.com/openai-launches-gpt-5-1-api-with-improved-coding-capabilities-and-new-developer-features/",
        candidates=["GPT-5.1", "GPT-5"],
    ),
]

# Map for nicer labels/colors downstream.
PROVIDER_BY_MODEL = {
    "Gemini 3.0": "Google",
    "Gemini 2.5 Pro": "Google",
    "GPT-5.1": "OpenAI",
    "GPT-5": "OpenAI",
    "Grok 4": "xAI",
}

DEFAULT_SEED = {
    "Gemini 3.0": 91.9,
    "GPT-5.1": 88.1,
    "Grok 4": 88.1,
    "Gemini 2.5 Pro": 86.4,
    "GPT-5": 85.6,
}

MAX_DELTA = 5.0  # percentage points tolerance


def _extract_scores(html: str, names: List[str]) -> Dict[str, float]:
    """Pull score numbers near each model name."""
    scores: Dict[str, float] = {}
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    for name in names:
        pattern = rf"(?i){re.escape(name)}[^0-9]{{0,40}}(\d{{2}}(?:\.\d)?)%"
        match = re.search(pattern, text)
        if match:
            try:
                scores[name] = float(match.group(1))
            except ValueError:
                continue
    return scores


def _load_existing() -> Dict[str, dict]:
    if not DATA_PATH.exists():
        return {}
    try:
        return json.loads(DATA_PATH.read_text())
    except Exception:
        return {}


def _merge(existing: Dict[str, dict], updates: Dict[str, float], source: str, as_of: str) -> Dict[str, dict]:
    merged = existing.copy()
    for model, score in updates.items():
        prev = existing.get(model, {}).get("score")
        if prev is not None and abs(score - float(prev)) > MAX_DELTA:
            # Skip suspicious jumps
            continue
        merged[model] = {
            "model": model,
            "provider": PROVIDER_BY_MODEL.get(model, "Unknown"),
            "score": score,
            "as_of": as_of,
            "source": source,
        }
    return merged


def main() -> None:
    today = _dt.date.today().isoformat()
    existing = _load_existing()
    combined: Dict[str, dict] = existing.copy()

    for src in SOURCES:
        try:
            resp = requests.get(src.url, timeout=20)
            resp.raise_for_status()
            found = _extract_scores(resp.text, src.candidates)
            combined = _merge(combined, found, src.name, today)
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"[warn] {src.name}: {exc}")

    if not combined:
        combined = {
            name: {
                "model": name,
                "provider": PROVIDER_BY_MODEL.get(name, "Unknown"),
                "score": score,
                "as_of": today,
                "source": "seed",
            }
            for name, score in DEFAULT_SEED.items()
        }
        print("[info] populated with seed scores (first run fallback)")

    if combined != existing:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATA_PATH.write_text(json.dumps(combined, indent=2, sort_keys=True))
        print(f"[ok] wrote {DATA_PATH}")
    else:
        print("[info] no changes detected")


if __name__ == "__main__":
    main()
