#!/usr/bin/env python3
"""Create a contact sheet from a GIF for sticker annotation.

Example:
    python scripts/gif_contact_sheet.py stickers/a.gif sticker_sheets/a_sheet.jpg --frames 12
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageSequence, ImageOps, ImageDraw


def sample_indices(total: int, n: int) -> list[int]:
    if total <= 0:
        return []
    if n <= 1:
        return [0]
    n = min(n, total)
    return sorted({round(i * (total - 1) / (n - 1)) for i in range(n)})


def make_contact_sheet(gif_path: Path, out_path: Path, frames: int = 12, thumb_size: int = 160, columns: int = 4) -> None:
    if not gif_path.exists():
        raise FileNotFoundError(gif_path)

    with Image.open(gif_path) as im:
        all_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(im)]

    if not all_frames:
        raise ValueError(f"No frames found in {gif_path}")

    chosen = [all_frames[i] for i in sample_indices(len(all_frames), frames)]

    thumbs = []
    for idx, frame in zip(sample_indices(len(all_frames), frames), chosen):
        bg = Image.new("RGBA", frame.size, "white")
        bg.alpha_composite(frame)
        rgb = bg.convert("RGB")
        rgb.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
        canvas = Image.new("RGB", (thumb_size, thumb_size + 22), "white")
        x = (thumb_size - rgb.width) // 2
        y = (thumb_size - rgb.height) // 2
        canvas.paste(rgb, (x, y))
        d = ImageDraw.Draw(canvas)
        d.text((6, thumb_size + 4), f"frame {idx}", fill=(0, 0, 0))
        thumbs.append(canvas)

    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_size, rows * (thumb_size + 22)), "white")

    for i, thumb in enumerate(thumbs):
        x = (i % columns) * thumb_size
        y = (i // columns) * (thumb_size + 22)
        sheet.paste(thumb, (x, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gif", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--frames", type=int, default=12)
    parser.add_argument("--thumb-size", type=int, default=160)
    parser.add_argument("--columns", type=int, default=4)
    args = parser.parse_args()

    make_contact_sheet(args.gif, args.output, args.frames, args.thumb_size, args.columns)
    print(f"Created {args.output}")


if __name__ == "__main__":
    main()
