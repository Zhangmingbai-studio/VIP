#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/root/autodl-tmp/vip_singing}"
COMFY_ROOT="${COMFY_ROOT:-/root/ComfyUI}"
INPUT_DIR="$COMFY_ROOT/input/VIP/video"

FIRST_FRAMES_DIR="${FIRST_FRAMES_DIR:-$PROJECT_ROOT/assets/first_frames}"
RVC_VOCALS_DIR="${RVC_VOCALS_DIR:-$PROJECT_ROOT/audio_workflow/output/rvc_vocals}"
FINAL_MIX_DIR="${FINAL_MIX_DIR:-$PROJECT_ROOT/audio_workflow/output/final_mix}"

COMFY_FIRST_FRAMES_DIR="$INPUT_DIR/first_frames"
COMFY_RVC_VOCALS_DIR="$INPUT_DIR/audio/rvc_vocals"
COMFY_FINAL_MIX_DIR="$INPUT_DIR/audio/final_mix"

SYNC_COUNT=0

sync_files() {
  local src_dir="$1"
  local dst_dir="$2"
  local label="$3"
  shift 3

  mkdir -p "$dst_dir"
  find "$dst_dir" -xtype l -delete 2>/dev/null || true

  if [[ ! -d "$src_dir" ]]; then
    echo "Missing $label directory: $src_dir" >&2
    SYNC_COUNT=0
    return 0
  fi

  local count=0
  local file
  local pattern
  shopt -s nullglob nocaseglob
  for pattern in "$@"; do
    for file in "$src_dir"/$pattern; do
      [[ -f "$file" ]] || continue
      ln -sfn "$file" "$dst_dir/$(basename "$file")"
      count=$((count + 1))
    done
  done
  shopt -u nullglob nocaseglob

  echo "Synced $count $label file(s): $src_dir -> $dst_dir"
  SYNC_COUNT="$count"
}

legacy_link_if_exists() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    ln -sfn "$src" "$dst"
  fi
}

mkdir -p "$INPUT_DIR"

sync_files "$FIRST_FRAMES_DIR" "$COMFY_FIRST_FRAMES_DIR" "first frame" "*.png" "*.jpg" "*.jpeg" "*.webp"
first_frame_count="$SYNC_COUNT"

sync_files "$RVC_VOCALS_DIR" "$COMFY_RVC_VOCALS_DIR" "RVC vocal" "*.wav" "*.flac" "*.mp3" "*.m4a"
sync_files "$FINAL_MIX_DIR" "$COMFY_FINAL_MIX_DIR" "final mix" "*.wav" "*.flac" "*.mp3" "*.m4a"

if (( first_frame_count == 0 )); then
  echo "No first-frame images found in: $FIRST_FRAMES_DIR" >&2
  exit 1
fi

# Backward-compatible links for older workflow versions.
legacy_link_if_exists "$FIRST_FRAMES_DIR/luna_v1_first_frame.png" "$INPUT_DIR/luna_v1_first_frame.png"
legacy_link_if_exists "$RVC_VOCALS_DIR/045b_clip_27s_16s_misono_mika_rvc.wav" "$INPUT_DIR/045b_clip_27s_16s_misono_mika_rvc.wav"
legacy_link_if_exists "$FINAL_MIX_DIR/045b_clip_27s_16s_misono_mika_final_mix.wav" "$INPUT_DIR/045b_clip_27s_16s_misono_mika_final_mix.wav"

echo "Prepared ComfyUI video inputs:"
find "$INPUT_DIR" -maxdepth 3 \( -type l -o -type f \) -printf '%p -> %l\n' | sort
