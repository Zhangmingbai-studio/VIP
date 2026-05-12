#!/usr/bin/env python3
"""Extract a short song clip for the RVC audio workflow.

Examples:
  python extract_song_clip.py full_song.mp3 demo.wav --start 01:12 --duration 15
  python extract_song_clip.py full_song.mp3 demo.wav --auto --duration 15 --candidate-dir candidates
"""

from __future__ import annotations

import argparse
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Candidate:
    start: float
    score: float


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required tool: {name}. Please install ffmpeg first.")
    return path


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or f"Command failed: {' '.join(cmd)}")


def capture(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return proc.stdout.strip()


def parse_time(value: str | float | int) -> float:
    if isinstance(value, (float, int)):
        return float(value)

    text = str(value).strip()
    if not text:
        raise argparse.ArgumentTypeError("empty time value")

    if ":" not in text:
        try:
            return float(text)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid time value: {text}") from exc

    parts = text.split(":")
    if len(parts) > 3:
        raise argparse.ArgumentTypeError(f"invalid time value: {text}")
    try:
        nums = [float(p) for p in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid time value: {text}") from exc

    seconds = 0.0
    for num in nums:
        seconds = seconds * 60 + num
    return seconds


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(int(minutes), 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:06.3f}"
    return f"{minutes:02d}:{sec:06.3f}"


def ffprobe_duration(input_path: Path) -> float:
    out = capture(
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
    try:
        return float(out)
    except ValueError as exc:
        raise SystemExit(f"Could not read duration from ffprobe output: {out}") from exc


def make_analysis_wav(input_path: Path, wav_path: Path, sample_rate: int) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-sample_fmt",
            "s16",
            str(wav_path),
        ]
    )


def read_pcm16_mono(path: Path) -> tuple[int, list[int]]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    if channels != 1 or sample_width != 2:
        raise SystemExit("analysis WAV must be mono PCM16")
    if not frames:
        raise SystemExit("analysis WAV is empty")
    count = len(frames) // 2
    samples = list(struct.unpack(f"<{count}h", frames))
    return sample_rate, samples


def window_rms(samples: list[int], sample_rate: int, window_seconds: float, hop_seconds: float) -> list[float]:
    window = max(1, int(window_seconds * sample_rate))
    hop = max(1, int(hop_seconds * sample_rate))
    values: list[float] = []
    for start in range(0, max(1, len(samples) - window + 1), hop):
        chunk = samples[start : start + window]
        if not chunk:
            continue
        mean_square = sum(float(s) * float(s) for s in chunk) / len(chunk)
        values.append(math.sqrt(mean_square) / 32768.0)
    return values


def pick_candidates(
    input_path: Path,
    duration: float,
    count: int,
    avoid_start: float,
    avoid_end: float,
    sample_rate: int,
) -> list[Candidate]:
    total = ffprobe_duration(input_path)
    if total < duration:
        raise SystemExit(f"Input is shorter than requested clip duration: {total:.2f}s < {duration:.2f}s")

    with tempfile.TemporaryDirectory() as tmp:
        analysis_wav = Path(tmp) / "analysis.wav"
        make_analysis_wav(input_path, analysis_wav, sample_rate)
        sr, samples = read_pcm16_mono(analysis_wav)

    hop_seconds = 0.25
    rms_values = window_rms(samples, sr, window_seconds=0.5, hop_seconds=hop_seconds)
    if not rms_values:
        raise SystemExit("Could not compute audio energy")

    min_start = avoid_start
    max_start = max(0.0, total - duration - avoid_end)
    if min_start > max_start:
        min_start = 0.0
        max_start = max(0.0, total - duration)

    span = max(1, int(duration / hop_seconds))
    scored: list[Candidate] = []
    for i in range(0, max(1, len(rms_values) - span + 1)):
        start = i * hop_seconds
        if start < min_start or start > max_start:
            continue
        window = rms_values[i : i + span]
        if not window:
            continue
        avg = sum(window) / len(window)
        peak = max(window)
        quiet_penalty = sum(1 for v in window if v < 0.01) / len(window)
        score = avg * 0.8 + peak * 0.2 - quiet_penalty * 0.05
        scored.append(Candidate(start=start, score=score))

    if not scored:
        raise SystemExit("No valid candidate windows found")

    selected: list[Candidate] = []
    for cand in sorted(scored, key=lambda item: item.score, reverse=True):
        if all(abs(cand.start - existing.start) >= duration * 0.75 for existing in selected):
            selected.append(cand)
        if len(selected) >= count:
            break
    return selected


def extract_clip(input_path: Path, output_path: Path, start: float, duration: float, fade: float, sample_rate: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "2",
        "-ar",
        str(sample_rate),
    ]
    if fade > 0:
        fade = min(fade, duration / 2)
        out_start = max(0.0, duration - fade)
        cmd += ["-af", f"afade=t=in:st=0:d={fade:.3f},afade=t=out:st={out_start:.3f}:d={fade:.3f}"]
    cmd.append(str(output_path))
    run(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract a 10-15 second song clip with ffmpeg.")
    parser.add_argument("input", type=Path, help="Input song file, e.g. full_song.mp3 or full_song.wav")
    parser.add_argument("output", type=Path, help="Output clip path, e.g. demo.wav")
    parser.add_argument("--duration", type=parse_time, default=15.0, help="Clip duration, default: 15")
    parser.add_argument("--start", type=parse_time, help="Manual start time, e.g. 72.5 or 01:12.5")
    parser.add_argument("--auto", action="store_true", help="Pick a high-energy segment automatically")
    parser.add_argument("--candidates", type=int, default=5, help="Number of auto candidates to print/export")
    parser.add_argument("--candidate-dir", type=Path, help="Optional directory to export all auto candidates")
    parser.add_argument("--avoid-start", type=parse_time, default=20.0, help="Auto mode: avoid the first N seconds")
    parser.add_argument("--avoid-end", type=parse_time, default=10.0, help="Auto mode: avoid the last N seconds")
    parser.add_argument("--fade", type=parse_time, default=0.05, help="Fade in/out length, default: 0.05")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Output sample rate, default: 44100")
    parser.add_argument("--analysis-sample-rate", type=int, default=16000, help="Auto mode analysis sample rate")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    require_tool("ffmpeg")
    require_tool("ffprobe")

    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    if args.duration <= 0:
        raise SystemExit("--duration must be greater than 0")

    if args.auto:
        candidates = pick_candidates(
            input_path=input_path,
            duration=args.duration,
            count=max(1, args.candidates),
            avoid_start=max(0.0, args.avoid_start),
            avoid_end=max(0.0, args.avoid_end),
            sample_rate=max(8000, args.analysis_sample_rate),
        )
        best = candidates[0]
        print("Auto candidates:")
        for i, cand in enumerate(candidates, start=1):
            print(f"  {i}. start={format_time(cand.start)} score={cand.score:.6f}")

        extract_clip(input_path, output_path, best.start, args.duration, args.fade, args.sample_rate)
        print(f"Best clip: {output_path}")
        print(f"Start: {format_time(best.start)}  Duration: {args.duration:.3f}s")

        if args.candidate_dir:
            candidate_dir = args.candidate_dir.expanduser().resolve()
            stem = output_path.stem
            suffix = output_path.suffix or ".wav"
            for i, cand in enumerate(candidates, start=1):
                candidate_output = candidate_dir / f"{stem}_candidate_{i:02d}_{format_time(cand.start).replace(':', '-')}{suffix}"
                extract_clip(input_path, candidate_output, cand.start, args.duration, args.fade, args.sample_rate)
            print(f"Candidate clips: {candidate_dir}")
        return 0

    if args.start is None:
        raise SystemExit("Please provide --start for manual mode, or use --auto.")

    extract_clip(input_path, output_path, max(0.0, args.start), args.duration, args.fade, args.sample_rate)
    print(f"Clip: {output_path}")
    print(f"Start: {format_time(args.start)}  Duration: {args.duration:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
