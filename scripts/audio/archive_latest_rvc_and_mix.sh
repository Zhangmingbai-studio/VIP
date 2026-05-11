#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat >&2 <<'USAGE'
Usage:
  archive_latest_rvc_and_mix.sh /path/to/no_vocals.wav [name]

Find the newest RVC WebUI audio from /tmp/gradio, copy it to output/rvc_vocals,
then mix it with the Demucs no_vocals.wav accompaniment.

Example:
  bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/archive_latest_rvc_and_mix.sh \
    /root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav \
    demo_misono_mika
USAGE
  exit 1
fi

INSTRUMENTAL="$1"
NAME="${2:-latest_rvc}"
WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"
RVC_OUT_DIR="$WORKFLOW_ROOT/output/rvc_vocals"
FINAL_OUT_DIR="$WORKFLOW_ROOT/output/final_mix"
MIX_SCRIPT="$WORKFLOW_ROOT/scripts/mix_rvc_with_instrumental.sh"

if [[ ! -f "$INSTRUMENTAL" ]]; then
  echo "Instrumental not found: $INSTRUMENTAL" >&2
  exit 1
fi
if [[ ! -f "$MIX_SCRIPT" ]]; then
  echo "Mix script not found: $MIX_SCRIPT" >&2
  exit 1
fi

mkdir -p "$RVC_OUT_DIR" "$FINAL_OUT_DIR"

LATEST_RVC=""
if [[ -d /tmp/gradio ]]; then
  LATEST_RVC="$(
    find /tmp/gradio -type f \( -iname '*.wav' -o -iname '*.mp3' \) -printf '%T@\t%p\n' 2>/dev/null \
      | sort -nr \
      | head -n 1 \
      | cut -f2-
  )"
fi
if [[ -z "${LATEST_RVC:-}" || ! -f "$LATEST_RVC" ]]; then
  echo "No recent RVC WebUI audio found under /tmp/gradio." >&2
  echo "Run Convert in RVC WebUI first, then rerun this script." >&2
  exit 1
fi

RVC_VOCAL="$RVC_OUT_DIR/${NAME}_rvc.wav"
FINAL_MIX="$FINAL_OUT_DIR/${NAME}_final_mix.wav"

cp -f "$LATEST_RVC" "$RVC_VOCAL"

export PATH="$CONDA_ROOT/envs/rvc/bin:$CONDA_ROOT/bin:$PATH"
bash "$MIX_SCRIPT" "$RVC_VOCAL" "$INSTRUMENTAL" "$FINAL_MIX"

echo
echo "Archived RVC vocal: $RVC_VOCAL"
echo "Final mix: $FINAL_MIX"
