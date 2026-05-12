#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 /path/to/ltx_video.mp4 /path/to/output_final_mix_video.mp4 [final_mix.wav]" >&2
  exit 1
fi

VIDEO="$1"
OUT="$2"
FINAL_MIX="${3:-/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/045b_clip_27s_16s_misono_mika_final_mix.wav}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"

if [[ ! -f "$VIDEO" ]]; then
  echo "Video not found: $VIDEO" >&2
  exit 1
fi
if [[ ! -f "$FINAL_MIX" ]]; then
  echo "Final mix audio not found: $FINAL_MIX" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
export PATH="$CONDA_ROOT/bin:$PATH"

ffmpeg -y \
  -i "$VIDEO" \
  -i "$FINAL_MIX" \
  -map 0:v:0 \
  -map 1:a:0 \
  -c:v copy \
  -c:a aac \
  -b:a 192k \
  -shortest \
  "$OUT"

echo "Muxed final video: $OUT"
