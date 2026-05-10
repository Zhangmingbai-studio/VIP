#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
RVC_ROOT="${RVC_ROOT:-$WORKFLOW_ROOT/tools/Retrieval-based-Voice-Conversion-WebUI}"
MODEL_ROOT="${MODEL_ROOT:-$WORKFLOW_ROOT/input/rvc_models}"
VOICE_DIR="${1:-}"

mkdir -p "$MODEL_ROOT" "$RVC_ROOT/assets/weights" "$RVC_ROOT/assets/indices"

sync_one_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "Skip missing directory: $dir" >&2
    return 0
  fi

  local pth=""
  pth="$(find "$dir" -maxdepth 2 -type f -name '*.pth' | sort | head -n 1 || true)"
  if [[ -n "$pth" ]]; then
    ln -sfn "$pth" "$RVC_ROOT/assets/weights/$(basename "$pth")"
    echo "Linked pth: $(basename "$pth")"
  else
    echo "No .pth found in $dir"
  fi

  while IFS= read -r idx; do
    [[ -z "$idx" ]] && continue
    ln -sfn "$idx" "$RVC_ROOT/assets/indices/$(basename "$idx")"
    echo "Linked index: $(basename "$idx")"
  done < <(find "$dir" -maxdepth 3 -type f -name '*.index' ! -name '*trained*' | sort)
}

if [[ -n "$VOICE_DIR" ]]; then
  sync_one_dir "$VOICE_DIR"
else
  found=0
  for dir in "$MODEL_ROOT"/*; do
    [[ -d "$dir" ]] || continue
    found=1
    sync_one_dir "$dir"
  done
  if [[ "$found" -eq 0 ]]; then
    echo "Put each RVC voice model under: $MODEL_ROOT/<voice_name>/"
  fi
fi

echo "RVC weights: $RVC_ROOT/assets/weights"
echo "RVC indices: $RVC_ROOT/assets/indices"
