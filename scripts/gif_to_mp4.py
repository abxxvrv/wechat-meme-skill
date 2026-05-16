#!/usr/bin/env python3
"""Convert GIF stickers to short MP4 loops.

For short GIFs, repeat the complete GIF enough times to produce a 1-2 second
MP4. For GIFs already longer than 2 seconds, keep one complete play and speed it
up just enough to fit within the maximum duration.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import subprocess
import sys

from PIL import Image


MIN_DURATION = 1.0
MAX_DURATION = 2.0


def gif_duration_seconds(path: Path) -> float:
    total_ms = 0
    with Image.open(path) as image:
        for frame_index in range(getattr(image, "n_frames", 1)):
            image.seek(frame_index)
            total_ms += int(image.info.get("duration", 100))
    return max(total_ms / 1000.0, 0.01)


def plan_conversion(duration: float, min_duration: float, max_duration: float) -> tuple[int, float, float]:
    """Return repeat count, speed factor, and expected output duration."""
    if duration > max_duration:
        speed = duration / max_duration
        return 1, speed, max_duration

    repeats = max(1, math.ceil(min_duration / duration))
    while duration * repeats > max_duration and repeats > 1:
        repeats -= 1

    expected = duration * repeats
    if expected < min_duration:
        speed = expected / min_duration
        return repeats, speed, min_duration

    return repeats, 1.0, expected


def convert_gif(
    source: Path,
    output: Path,
    *,
    min_duration: float,
    max_duration: float,
    overwrite: bool,
) -> tuple[int, float, float]:
    duration = gif_duration_seconds(source)
    repeats, speed, expected = plan_conversion(duration, min_duration, max_duration)
    stream_loop = repeats - 1
    output.parent.mkdir(parents=True, exist_ok=True)

    filters = []
    if abs(speed - 1.0) > 0.001:
        filters.append(f"setpts=PTS/{speed:.8f}")
    filters.extend([
        "fps=30",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos",
        "format=yuv420p",
    ])

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-stream_loop",
        str(stream_loop),
        "-i",
        str(source),
        "-t",
        f"{expected:.3f}",
        "-vf",
        ",".join(filters),
        "-an",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True)
    return repeats, speed, expected


def iter_gifs(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".gif":
            raise SystemExit(f"Not a GIF file: {path}")
        return [path]
    if path.is_dir():
        return sorted(path.glob("*.gif"))
    raise SystemExit(f"Path not found: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert GIF stickers to 1-2 second MP4 loops.")
    parser.add_argument("path", type=Path, help="GIF file or directory containing GIF files")
    parser.add_argument("--output-dir", type=Path, default=None, help="Defaults to each GIF's directory")
    parser.add_argument("--min-duration", type=float, default=MIN_DURATION)
    parser.add_argument("--max-duration", type=float, default=MAX_DURATION)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.min_duration <= 0 or args.max_duration <= 0 or args.min_duration > args.max_duration:
        raise SystemExit("--min-duration must be <= --max-duration, and both must be positive")

    gifs = iter_gifs(args.path)
    if not gifs:
        print(f"No GIF files found in {args.path}")
        return

    failed = False
    for gif in gifs:
        output_dir = args.output_dir or gif.parent
        output = output_dir / f"{gif.stem}.mp4"
        try:
            repeats, speed, expected = convert_gif(
                gif,
                output,
                min_duration=args.min_duration,
                max_duration=args.max_duration,
                overwrite=args.overwrite,
            )
        except subprocess.CalledProcessError as exc:
            failed = True
            print(f"FAILED {gif} -> {output}: ffmpeg exited {exc.returncode}", file=sys.stderr)
            continue

        speed_note = f", speed={speed:.3f}x" if abs(speed - 1.0) > 0.001 else ""
        print(f"OK {gif} -> {output} ({repeats} play(s){speed_note}, ~{expected:.3f}s)")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
