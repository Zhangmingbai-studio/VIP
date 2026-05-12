#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/root/autodl-tmp/vip_singing}"
COMFY_ROOT="${COMFY_ROOT:-/root/ComfyUI}"
INPUT_DIR="$COMFY_ROOT/input/VIP/video"

FIRST_FRAME="${FIRST_FRAME:-$PROJECT_ROOT/assets/first_frames/luna_v1_first_frame.png}"
RVC_VOCAL="${RVC_VOCAL:-$PROJECT_ROOT/audio_workflow/output/rvc_vocals/045b_clip_27s_16s_misono_mika_rvc.wav}"
FINAL_MIX="${FINAL_MIX:-$PROJECT_ROOT/audio_workflow/output/final_mix/045b_clip_27s_16s_misono_mika_final_mix.wav}"

for file in "$FIRST_FRAME" "$RVC_VOCAL" "$FINAL_MIX"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing input asset: $file" >&2
    exit 1
  fi
done

mkdir -p "$INPUT_DIR"
ln -sfn "$FIRST_FRAME" "$INPUT_DIR/luna_v1_first_frame.png"
ln -sfn "$RVC_VOCAL" "$INPUT_DIR/045b_clip_27s_16s_misono_mika_rvc.wav"
ln -sfn "$FINAL_MIX" "$INPUT_DIR/045b_clip_27s_16s_misono_mika_final_mix.wav"

echo "Prepared ComfyUI video inputs:"
find "$INPUT_DIR" -maxdepth 1 \( -type l -o -type f \) -printf '%p -> %l\n' | sort
