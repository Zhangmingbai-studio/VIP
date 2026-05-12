#!/usr/bin/env bash
set -euo pipefail

COMFY_ROOT="${COMFY_ROOT:-/root/ComfyUI}"

download() {
  local url="$1"
  local out="$2"
  local expected_bytes="${3:-0}"
  local max_attempts="${4:-8}"
  local current_size
  mkdir -p "$(dirname "$out")"

  current_size="$(stat -c%s "$out" 2>/dev/null || echo 0)"
  if (( expected_bytes > 0 && current_size >= expected_bytes )); then
    echo "Already complete: $out ($current_size bytes)"
    return 0
  fi

  if (( current_size > 0 )); then
    echo "Resuming: $out ($current_size bytes already downloaded)"
  else
    echo "Downloading: $out"
  fi

  for attempt in $(seq 1 "$max_attempts"); do
    echo "Attempt $attempt/$max_attempts: $out"
    if wget -c --tries=3 --retry-connrefused --waitretry=20 --read-timeout=60 --timeout=60 --show-progress --progress=bar:force:noscroll -O "$out" "$url"; then
      break
    fi

    current_size="$(stat -c%s "$out" 2>/dev/null || echo 0)"
    if (( expected_bytes > 0 && current_size >= expected_bytes )); then
      break
    fi

    echo "Download interrupted; retrying from the original Hugging Face URL..."
    sleep 5
  done

  current_size="$(stat -c%s "$out" 2>/dev/null || echo 0)"
  if (( expected_bytes > 0 && current_size < expected_bytes )); then
    echo "ERROR: incomplete download: $out"
    echo "       current:  $current_size bytes"
    echo "       expected: $expected_bytes bytes"
    return 1
  fi
}

download \
  "https://huggingface.co/Lightricks/LTX-2.3-fp8/resolve/main/ltx-2.3-22b-dev-fp8.safetensors" \
  "$COMFY_ROOT/models/checkpoints/ltx-2.3-22b-dev-fp8.safetensors" \
  "29145431166"

download \
  "https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors" \
  "$COMFY_ROOT/models/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors"

download \
  "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-22b-distilled-lora-384.safetensors" \
  "$COMFY_ROOT/models/loras/ltx-2.3-22b-distilled-lora-384.safetensors"

download \
  "https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/loras/gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors" \
  "$COMFY_ROOT/models/loras/gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors"

download \
  "https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x2-1.1.safetensors" \
  "$COMFY_ROOT/models/latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.1.safetensors"

echo "LTX-2.3 model files are in place. Restart ComfyUI before running the workflow."
