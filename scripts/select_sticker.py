#!/usr/bin/env python3
"""Select a sticker from index.yaml by simple keyword scoring.

This is a deterministic helper. The agent should still apply SKILL.md's social
rules before sending the selected file.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import yaml


def as_text(value) -> str:
    if isinstance(value, list):
        return " ".join(map(str, value))
    if isinstance(value, dict):
        return " ".join(f"{k} {as_text(v)}" for k, v in value.items())
    return "" if value is None else str(value)


def score_item(item: dict, query_terms: list[str], max_intensity: int | None) -> tuple[int, int]:
    if max_intensity is not None and int(item.get("intensity", 5)) > max_intensity:
        return (-10_000, 999)

    searchable = " ".join([
        as_text(item.get("id")),
        as_text(item.get("short_meaning")),
        as_text(item.get("emotion")),
        as_text(item.get("intent")),
        as_text(item.get("tone")),
        as_text(item.get("tags")),
        as_text(item.get("text_on_image")),
        as_text(item.get("visual_description")),
    ]).lower()

    score = 0
    for term in query_terms:
        term = term.lower().strip()
        if not term:
            continue
        if term in as_text(item.get("tags")).lower():
            score += 5
        if term in as_text(item.get("short_meaning")).lower():
            score += 4
        if term in searchable:
            score += 1

    # Tie-breaker: prefer lower intensity when semantic scores are equal.
    intensity = int(item.get("intensity", 3))
    return score, -intensity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-intensity", type=int, default=None)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    data = yaml.safe_load((args.root / "index.yaml").read_text(encoding="utf-8")) or {}
    stickers = data.get("stickers", [])
    terms = args.query.replace("，", " ").replace(",", " ").split()

    scored = []
    for item in stickers:
        if not isinstance(item, dict):
            continue
        score, tie = score_item(item, terms, args.max_intensity)
        if score > 0:
            scored.append((score, tie, item))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    for score, _, item in scored[: args.top_k]:
        print(f"{score}\t{item.get('id')}\t{item.get('file')}\t{item.get('short_meaning')}")


if __name__ == "__main__":
    main()
