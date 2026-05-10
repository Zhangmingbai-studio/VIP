#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/song.wav [demucs_model]" >&2
  exit 1
fi

INPUT_AUDIO="$1"
MODEL="${2:-htdemucs}"
WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"
OUT_ROOT="${OUT_ROOT:-$WORKFLOW_ROOT/output/separated}"

if [[ ! -f "$INPUT_AUDIO" ]]; then
  echo "Input audio not found: $INPUT_AUDIO" >&2
  exit 1
fi

mkdir -p "$OUT_ROOT" "$WORKFLOW_ROOT/logs"

export PATH="$CONDA_ROOT/bin:$PATH"
# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc

demucs --two-stems=vocals -n "$MODEL" -o "$OUT_ROOT" "$INPUT_AUDIO"

echo "Demucs output root: $OUT_ROOT/$MODEL"
