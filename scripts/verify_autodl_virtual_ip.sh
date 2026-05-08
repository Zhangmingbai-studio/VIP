#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/vip_singing}"
COMFY_DIR="${COMFY_DIR:-$PROJECT_DIR/ComfyUI}"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

log "Checking NVIDIA runtime"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found"
fi

if [ ! -d "$COMFY_DIR" ]; then
  echo "ComfyUI directory not found: $COMFY_DIR" >&2
  exit 1
fi

if [ ! -f "$COMFY_DIR/.venv/bin/activate" ]; then
  echo "ComfyUI venv not found: $COMFY_DIR/.venv" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$COMFY_DIR/.venv/bin/activate"

log "Checking Python and PyTorch"
python - <<'PY'
import sys
print("python:", sys.version)
try:
    import torch
    print("torch:", torch.__version__)
    print("cuda available:", torch.cuda.is_available())
    print("cuda version:", torch.version.cuda)
    if torch.cuda.is_available():
        print("gpu:", torch.cuda.get_device_name(0))
except Exception as exc:
    print("torch check failed:", repr(exc))
    raise
PY

log "Checking ComfyUI folders"
for path in \
  "$COMFY_DIR/main.py" \
  "$COMFY_DIR/custom_nodes/ComfyUI-Manager" \
  "$COMFY_DIR/models/unet" \
  "$COMFY_DIR/models/diffusion_models" \
  "$COMFY_DIR/models/clip" \
  "$COMFY_DIR/models/vae" \
  "$PROJECT_DIR/run_comfyui.sh"; do
  if [ -e "$path" ]; then
    echo "[ok] $path"
  else
    echo "[missing] $path"
  fi
done

log "Model files found"
find "$COMFY_DIR/models" -maxdepth 2 -type f \( -name '*.safetensors' -o -name '*.gguf' -o -name '*.ckpt' -o -name '*.pt' -o -name '*.pth' \) | sort || true

log "Verification complete"

