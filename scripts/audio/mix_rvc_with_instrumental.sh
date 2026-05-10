#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 /path/to/rvc_vocal.wav /path/to/no_vocals.wav /path/to/final_mix.wav" >&2
  exit 1
fi

RVC_VOCAL="$1"
INSTRUMENTAL="$2"
OUT_AUDIO="$3"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"
VOCAL_GAIN="${VOCAL_GAIN:-1.0}"
INSTRUMENTAL_GAIN="${INSTRUMENTAL_GAIN:-1.0}"

if [[ ! -f "$RVC_VOCAL" ]]; then
  echo "RVC vocal not found: $RVC_VOCAL" >&2
  exit 1
fi
if [[ ! -f "$INSTRUMENTAL" ]]; then
  echo "Instrumental not found: $INSTRUMENTAL" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT_AUDIO")"

export PATH="$CONDA_ROOT/bin:$PATH"
# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc

ffmpeg -y \
  -i "$INSTRUMENTAL" \
  -i "$RVC_VOCAL" \
  -filter_complex "[0:a]volume=${INSTRUMENTAL_GAIN}[inst];[1:a]volume=${VOCAL_GAIN}[voc];[inst][voc]amix=inputs=2:duration=longest:dropout_transition=2,alimiter=limit=0.98[a]" \
  -map "[a]" \
  -ar 44100 \
  -ac 2 \
  "$OUT_AUDIO"

echo "Final mix: $OUT_AUDIO"
