#!/usr/bin/env python3
"""Generate a YAML metadata draft for a new sticker.

This script does not understand images by itself. The agent should inspect the
image/GIF/MP4 using vision, then pass the semantic fields to this script. The script
standardizes the entry format so it can be added to index.yaml.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
import yaml

SUPPORTED = {".gif", ".jpg", ".jpeg", ".png", ".webp", ".mp4"}
SENDABLE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4"}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "sticker"


def split_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in re.split(r"[,，;；]", value) if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="Source sticker file")
    parser.add_argument("--id", dest="sticker_id", help="Sticker id, lowercase snake_case")
    parser.add_argument("--meaning", required=True, help="short_meaning")
    parser.add_argument("--emotion", default="", help="Comma-separated emotions")
    parser.add_argument("--intent", default="", help="Comma-separated intents")
    parser.add_argument("--tone", default="", help="Comma-separated tones")
    parser.add_argument("--intensity", type=int, default=2, choices=[1, 2, 3, 4, 5])
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--suitable-when", default="", help="Comma-separated suitable scenes")
    parser.add_argument("--avoid-when", default="", help="Comma-separated avoid scenes")
    parser.add_argument("--visual-description", default="")
    parser.add_argument("--text-on-image", default="")
    parser.add_argument("--source", default="user_upload")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    ext = args.file.suffix.lower()
    if ext not in SUPPORTED:
        raise SystemExit(f"Unsupported file type: {ext}")

    sticker_id = args.sticker_id or slugify(args.file.stem)
    stored_ext = ".mp4" if ext == ".gif" else ext
    entry = {
        "id": sticker_id,
        "file": f"stickers/{sticker_id}{stored_ext}",
        "type": stored_ext.lstrip("."),
        "short_meaning": args.meaning,
        "emotion": split_list(args.emotion),
        "intent": split_list(args.intent),
        "tone": split_list(args.tone),
        "intensity": args.intensity,
        "tags": split_list(args.tags),
        "suitable_when": split_list(args.suitable_when),
        "avoid_when": split_list(args.avoid_when),
        "visual_description": args.visual_description,
        "text_on_image": args.text_on_image,
        "created_at": dt.date.today().isoformat(),
        "source": args.source,
    }

    if stored_ext not in SENDABLE_EXTENSIONS:
        raise SystemExit(f"Unsupported sendable file type: {stored_ext}")

    if not entry["emotion"]:
        entry["emotion"] = ["待补充"]
    if not entry["intent"]:
        entry["intent"] = ["待补充"]
    if not entry["tone"]:
        entry["tone"] = ["待补充"]
    if not entry["tags"]:
        entry["tags"] = [args.meaning]
    if not entry["suitable_when"]:
        entry["suitable_when"] = ["待补充"]
    if not entry["avoid_when"]:
        entry["avoid_when"] = ["严肃求助场景", "正式工作沟通", "对方情绪低落时"]

    text = yaml.safe_dump(entry, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
