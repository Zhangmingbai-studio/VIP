#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"
SCRIPT_PATH="${SCRIPT_PATH:-$WORKFLOW_ROOT/scripts/extract_song_clip.py}"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "extract_song_clip.py not found: $SCRIPT_PATH" >&2
  exit 1
fi

export PATH="$CONDA_ROOT/bin:$PATH"
# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc

exec python "$SCRIPT_PATH" "$@"
