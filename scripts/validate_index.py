#!/usr/bin/env python3
"""Validate index.yaml and sticker file references."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml

SUPPORTED = {"jpg", "jpeg", "png", "webp", "mp4"}
REQUIRED = [
    "id", "file", "type", "short_meaning", "emotion", "intent", "tone",
    "intensity", "tags", "suitable_when", "avoid_when",
    "visual_description", "text_on_image"
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    root = args.root.resolve()
    index_path = root / "index.yaml"
    if not index_path.exists():
        print(f"Missing index.yaml: {index_path}", file=sys.stderr)
        raise SystemExit(1)

    data = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    stickers = data.get("stickers")
    if not isinstance(stickers, list):
        print("index.yaml must contain stickers: []", file=sys.stderr)
        raise SystemExit(1)

    ok = True
    seen_ids = set()

    for i, item in enumerate(stickers):
        prefix = f"stickers[{i}]"
        if not isinstance(item, dict):
            print(f"{prefix}: must be a mapping", file=sys.stderr)
            ok = False
            continue

        for key in REQUIRED:
            if key not in item:
                print(f"{prefix}: missing {key}", file=sys.stderr)
                ok = False

        sticker_id = item.get("id")
        if sticker_id in seen_ids:
            print(f"{prefix}: duplicate id {sticker_id}", file=sys.stderr)
            ok = False
        seen_ids.add(sticker_id)

        file_value = item.get("file")
        if file_value:
            f = root / file_value
            if not f.exists():
                print(f"{prefix}: missing file {file_value}", file=sys.stderr)
                ok = False

        typ = str(item.get("type", "")).lower()
        if typ not in SUPPORTED:
            print(f"{prefix}: unsupported type {typ}", file=sys.stderr)
            ok = False

        try:
            intensity = int(item.get("intensity"))
            if intensity < 1 or intensity > 5:
                raise ValueError
        except Exception:
            print(f"{prefix}: intensity must be 1..5", file=sys.stderr)
            ok = False

    if not ok:
        raise SystemExit(1)

    print(f"OK: {len(stickers)} stickers validated")


if __name__ == "__main__":
    main()
