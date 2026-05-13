#!/usr/bin/env bash
set -euo pipefail

COMFY_ROOT="${COMFY_ROOT:-/root/ComfyUI}"

echo "--- ComfyUI process ---"
pgrep -af 'main.py --port 6006' || true

echo "--- required custom nodes via object_info ---"
/root/miniconda3/bin/python - <<'PY'
import json
import urllib.request

required = [
    "LTXAVTextEncoderLoader",
    "LTXVAudioVAELoader",
    "LTXVAudioVAEEncode",
    "LTXVAudioVAEDecode",
    "MultimodalGuider",
    "GuiderParameters",
    "LTXVEmptyLatentAudio",
    "LTXVConcatAVLatent",
    "LTXVSeparateAVLatent",
    "VHS_VideoCombine",
    "CM_FloatToInt",
    "ComfyMathExpression",
]
with urllib.request.urlopen("http://127.0.0.1:6006/object_info", timeout=10) as response:
    object_info = json.load(response)
for name in required:
    print(f"{name}: {'present' if name in object_info else 'missing'}")
PY

echo "--- required model files ---"
for file in \
  "$COMFY_ROOT/models/checkpoints/ltx-2.3-22b-dev-fp8.safetensors" \
  "$COMFY_ROOT/models/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors" \
  "$COMFY_ROOT/models/loras/ltx-2.3-22b-distilled-lora-384.safetensors" \
  "$COMFY_ROOT/models/loras/gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors" \
  "$COMFY_ROOT/models/latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.1.safetensors"; do
  if [[ -s "$file" ]]; then
    printf 'present %s (%s)\n' "$file" "$(du -h "$file" | awk '{print $1}')"
  else
    printf 'missing %s\n' "$file"
  fi
done

echo "--- ComfyUI input assets ---"
find "$COMFY_ROOT/input/VIP/video" -maxdepth 3 \( -type l -o -type f \) -printf '%p -> %l\n' 2>/dev/null | sort || true
