#!/usr/bin/env python3
"""
Prepare a short WAV song clip for the RVC audio workflow.

Examples:
  python3 scripts/audio/prepare_song_clip.py song.mp3 --start 01:12 --duration 12 --out song_clip_12s.wav
  python3 scripts/audio/prepare_song_clip.py song.m4a --start 72.5 --duration 10
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


MIN_RECOMMENDED_SECONDS = 10.0
MAX_RECOMMENDED_SECONDS = 15.0


def parse_time(value: str) -> float:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("time value cannot be empty")

    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)

    parts = value.split(":")
    if len(parts) not in (2, 3):
        raise argparse.ArgumentTypeError(
            f"invalid time '{value}', use seconds, MM:SS, or HH:MM:SS"
        )

    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid time '{value}', use seconds, MM:SS, or HH:MM:SS"
        ) from exc

    if any(number < 0 for number in numbers):
        raise argparse.ArgumentTypeError("time values must be non-negative")
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds
    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def format_suffix(seconds: float) -> str:
    text = f"{seconds:.3f}".rstrip("0").rstrip(".")
    return text.replace(".", "p")


def default_output_name(input_path: Path, start: float, duration: float) -> str:
    return f"{input_path.stem}_clip_{format_suffix(start)}s_{format_suffix(duration)}s.wav"


def default_output_path(input_path: Path, start: float, duration: float) -> Path:
    return input_path.with_name(default_output_name(input_path, start, duration))


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def probe_duration(input_path: Path) -> float | None:
    if shutil.which("ffprobe") is None:
        return None

    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_path),
        ]
    )
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Trim a downloaded song into a 10-15 second WAV clip for RVC."
    )
    parser.add_argument("input", help="Source audio file, such as .mp3, .m4a, .flac, or .wav")
    parser.add_argument(
        "--start",
        type=parse_time,
        default=0.0,
        help="Clip start time. Supports seconds, MM:SS, or HH:MM:SS. Default: 0",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=12.0,
        help="Clip duration in seconds. Recommended: 10-15. Default: 12",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output .wav path or output directory. Default: next to input with a clip suffix",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Output sample rate. Default: 44100",
    )
    parser.add_argument(
        "--channels",
        type=int,
        choices=(1, 2),
        default=2,
        help="Output channels: 1 mono or 2 stereo. Default: 2",
    )
    parser.add_argument(
        "--fade",
        type=float,
        default=0.05,
        help="Fade in/out seconds to avoid hard cuts. Use 0 to disable. Default: 0.05",
    )
    parser.add_argument(
        "--allow-any-duration",
        action="store_true",
        help="Allow durations outside the recommended 10-15 second MVP range",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"Input audio not found: {input_path}", file=sys.stderr)
        return 2

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found. Install ffmpeg first.", file=sys.stderr)
        return 2

    if args.duration <= 0:
        print("--duration must be greater than 0", file=sys.stderr)
        return 2

    if not args.allow_any_duration and not (
        MIN_RECOMMENDED_SECONDS <= args.duration <= MAX_RECOMMENDED_SECONDS
    ):
        print(
            f"--duration should be {MIN_RECOMMENDED_SECONDS:g}-{MAX_RECOMMENDED_SECONDS:g} "
            "seconds for this MVP. Use --allow-any-duration to override.",
            file=sys.stderr,
        )
        return 2

    if args.fade < 0:
        print("--fade must be non-negative", file=sys.stderr)
        return 2

    if args.out:
        raw_output_path = Path(args.out).expanduser()
        output_text = str(args.out)
        output_is_directory = raw_output_path.is_dir() or output_text.endswith(
            (os.sep, "/", "\\")
        )
        if output_is_directory:
            output_path = (
                raw_output_path / default_output_name(input_path, args.start, args.duration)
            ).resolve()
        else:
            output_path = raw_output_path.resolve()
            if output_path.suffix == "":
                output_path = output_path.with_suffix(".wav")
    else:
        output_path = default_output_path(input_path, args.start, args.duration)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source_duration = probe_duration(input_path)
    if source_duration is not None and args.start >= source_duration:
        print(
            f"--start {args.start:g}s is outside source duration {source_duration:.2f}s",
            file=sys.stderr,
        )
        return 2
    if source_duration is not None and args.start + args.duration > source_duration + 0.01:
        print(
            "Warning: requested clip extends beyond the source duration; "
            "ffmpeg will output the available tail.",
            file=sys.stderr,
        )

    filters: list[str] = []
    if args.fade > 0:
        fade = min(args.fade, args.duration / 2)
        fade_out_start = max(args.duration - fade, 0)
        filters.append(f"afade=t=in:st=0:d={fade}")
        filters.append(f"afade=t=out:st={fade_out_start}:d={fade}")

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{args.start:.6f}",
        "-i",
        str(input_path),
        "-t",
        f"{args.duration:.6f}",
        "-vn",
        "-map",
        "0:a:0",
    ]
    if filters:
        command.extend(["-af", ",".join(filters)])
    command.extend(
        [
            "-ar",
            str(args.sample_rate),
            "-ac",
            str(args.channels),
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]
    )

    result = run(command)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return result.returncode

    clip_duration = probe_duration(output_path)
    print(f"Created WAV clip: {output_path}")
    if clip_duration is not None:
        print(f"Duration: {clip_duration:.2f}s")
    print(f"Sample rate: {args.sample_rate} Hz")
    print(f"Channels: {args.channels}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
