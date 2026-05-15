#!/usr/bin/env python3
"""
Extract an RVC-ready WAV clip from a local video file.

Examples:
  python3 scripts/audio/prepare_video_audio_clip.py demo.mp4 --start 00:08 --duration 12
  python3 scripts/audio/prepare_video_audio_clip.py demo.mp4 --full --name short_video
  python3 scripts/audio/prepare_video_audio_clip.py demo.mp4 --start 00:27 --duration 16 --allow-any-duration --upload
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


MIN_RECOMMENDED_SECONDS = 10.0
MAX_RECOMMENDED_SECONDS = 15.0
DEFAULT_REMOTE_USER = "root"
DEFAULT_REMOTE_HOST = "connect.bjb2.seetacloud.com"
DEFAULT_REMOTE_PORT = 41578
DEFAULT_REMOTE_DIR = "/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/"
DEFAULT_SERVER_SCRIPT_DIR = "/root/autodl-tmp/vip_singing/audio_workflow/scripts"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_time(value: str) -> float:
    text = value.strip()
    if not text:
        raise argparse.ArgumentTypeError("time value cannot be empty")

    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)

    parts = text.split(":")
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


def safe_stem(text: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._-")
    stem = re.sub(r"_+", "_", stem)
    return stem or "video_audio"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"{name} not found. Install ffmpeg first.")


def probe_duration(input_path: Path) -> float | None:
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


def has_audio_stream(input_path: Path) -> bool:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(input_path),
        ]
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def default_output_name(input_path: Path, name: str | None, start: float, duration: float) -> str:
    stem = safe_stem(name or input_path.stem)
    return f"{stem}_clip_{format_suffix(start)}s_{format_suffix(duration)}s.wav"


def resolve_output_path(args: argparse.Namespace, input_path: Path) -> Path:
    output_name = default_output_name(input_path, args.name, args.start, args.duration)
    if args.out is None:
        return (repo_root() / "local_assets" / "audio" / "video_clips" / output_name).resolve()

    raw_output_path = Path(args.out).expanduser()
    output_is_directory = raw_output_path.is_dir() or str(args.out).endswith((os.sep, "/", "\\"))
    if output_is_directory:
        return (raw_output_path / output_name).resolve()

    output_path = raw_output_path.resolve()
    if output_path.suffix == "":
        output_path = output_path.with_suffix(".wav")
    return output_path


def build_ffmpeg_command(args: argparse.Namespace, input_path: Path, output_path: Path) -> list[str]:
    filters: list[str] = []
    if args.fade > 0:
        fade = min(args.fade, args.duration / 2)
        fade_out_start = max(args.duration - fade, 0)
        filters.append(f"afade=t=in:st=0:d={fade}")
        filters.append(f"afade=t=out:st={fade_out_start}:d={fade}")

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
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
    return command


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def remote_clip_path(args: argparse.Namespace, output_path: Path) -> str:
    remote_dir = args.remote_dir.rstrip("/")
    return f"{remote_dir}/{output_path.name}"


def print_next_steps(args: argparse.Namespace, output_path: Path) -> None:
    remote_path = remote_clip_path(args, output_path)
    scp_command = [
        "scp",
        "-P",
        str(args.remote_port),
        str(output_path),
        f"{args.remote_user}@{args.remote_host}:{args.remote_dir.rstrip('/')}/",
    ]
    demucs_command = [
        "bash",
        f"{args.server_script_dir.rstrip('/')}/separate_vocals_demucs.sh",
        remote_path,
    ]

    print()
    print("Upload command:")
    print(shell_join(scp_command))
    print()
    print("Then run on AutoDL:")
    print(shell_join(demucs_command))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract audio from a local video into a WAV clip for the RVC workflow."
    )
    parser.add_argument("input", help="Source video file, such as .mp4, .mov, .mkv, or .webm")
    parser.add_argument(
        "--start",
        type=parse_time,
        default=0.0,
        help="Clip start time. Supports seconds, MM:SS, or HH:MM:SS. Default: 0",
    )
    parser.add_argument(
        "--duration",
        type=parse_time,
        default=12.0,
        help="Clip duration. Supports seconds, MM:SS, or HH:MM:SS. Recommended: 10-15. Default: 12",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Extract from --start to the end of the video. Overrides --duration.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output .wav path or output directory. Default: local_assets/audio/video_clips/",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optional ASCII-friendly output base name. Default: sanitized video filename",
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
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Run scp after creating the WAV. You will be prompted for the SSH password if needed.",
    )
    parser.add_argument(
        "--remote-user",
        default=DEFAULT_REMOTE_USER,
        help=f"AutoDL SSH user. Default: {DEFAULT_REMOTE_USER}",
    )
    parser.add_argument(
        "--remote-host",
        default=DEFAULT_REMOTE_HOST,
        help=f"AutoDL SSH host. Default: {DEFAULT_REMOTE_HOST}",
    )
    parser.add_argument(
        "--remote-port",
        type=int,
        default=DEFAULT_REMOTE_PORT,
        help=f"AutoDL SSH port. Default: {DEFAULT_REMOTE_PORT}",
    )
    parser.add_argument(
        "--remote-dir",
        default=DEFAULT_REMOTE_DIR,
        help=f"Remote RVC input directory. Default: {DEFAULT_REMOTE_DIR}",
    )
    parser.add_argument(
        "--server-script-dir",
        default=DEFAULT_SERVER_SCRIPT_DIR,
        help=f"Remote workflow script directory. Default: {DEFAULT_SERVER_SCRIPT_DIR}",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"Input video not found: {input_path}", file=sys.stderr)
        return 2

    require_tool("ffmpeg")
    require_tool("ffprobe")

    if args.fade < 0:
        print("--fade must be non-negative", file=sys.stderr)
        return 2

    if not has_audio_stream(input_path):
        print(f"No audio stream found in video: {input_path}", file=sys.stderr)
        return 2

    source_duration = probe_duration(input_path)
    if source_duration is not None and args.start >= source_duration:
        print(
            f"--start {args.start:g}s is outside source duration {source_duration:.2f}s",
            file=sys.stderr,
        )
        return 2

    if args.full:
        if source_duration is None:
            print("Could not determine source duration for --full", file=sys.stderr)
            return 2
        args.duration = source_duration - args.start

    if args.duration <= 0:
        print("--duration must be greater than 0", file=sys.stderr)
        return 2

    if not args.full and not args.allow_any_duration and not (
        MIN_RECOMMENDED_SECONDS <= args.duration <= MAX_RECOMMENDED_SECONDS
    ):
        print(
            f"--duration should be {MIN_RECOMMENDED_SECONDS:g}-{MAX_RECOMMENDED_SECONDS:g} "
            "seconds for this MVP. Use --allow-any-duration to override.",
            file=sys.stderr,
        )
        return 2

    if source_duration is not None and args.start + args.duration > source_duration + 0.01:
        print(
            "Warning: requested clip extends beyond the source duration; "
            "ffmpeg will output the available tail.",
            file=sys.stderr,
        )

    output_path = resolve_output_path(args, input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = run(build_ffmpeg_command(args, input_path, output_path))
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return result.returncode

    clip_duration = probe_duration(output_path)
    print(f"Created WAV clip: {output_path}")
    if clip_duration is not None:
        print(f"Duration: {clip_duration:.2f}s")
    print(f"Sample rate: {args.sample_rate} Hz")
    print(f"Channels: {args.channels}")

    if args.upload:
        scp_command = [
            "scp",
            "-P",
            str(args.remote_port),
            str(output_path),
            f"{args.remote_user}@{args.remote_host}:{args.remote_dir.rstrip('/')}/",
        ]
        upload = subprocess.run(scp_command)
        if upload.returncode != 0:
            print("Upload failed. The WAV clip was still created locally.", file=sys.stderr)
            print_next_steps(args, output_path)
            return upload.returncode
        print("Upload complete.")

    print_next_steps(args, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
