#!/usr/bin/env bash
set -Eeuo pipefail

# AutoDL setup script for the virtual IP production workflow.
# Safe default: install ComfyUI and helper nodes, create directories, do not download large models.

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/vip_singing}"
COMFY_DIR="${COMFY_DIR:-$PROJECT_DIR/ComfyUI}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTORCH_INDEX_URL="${PYTORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"
INSTALL_TORCH="${INSTALL_TORCH:-1}"
INSTALL_MANAGER="${INSTALL_MANAGER:-1}"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

clone_or_update() {
  local repo_url="$1"
  local target_dir="$2"

  if [ -d "$target_dir/.git" ]; then
    log "Updating $(basename "$target_dir")"
    git -C "$target_dir" pull --ff-only
  else
    log "Cloning $repo_url"
    git clone --depth 1 "$repo_url" "$target_dir"
  fi
}

need_cmd git
need_cmd "$PYTHON_BIN"

log "Project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

clone_or_update "https://github.com/Comfy-Org/ComfyUI.git" "$COMFY_DIR"

cd "$COMFY_DIR"

if [ ! -d ".venv" ]; then
  log "Creating Python venv"
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source "$COMFY_DIR/.venv/bin/activate"

log "Upgrading pip tooling"
python -m pip install --upgrade pip setuptools wheel

if [ "$INSTALL_TORCH" = "1" ]; then
  log "Installing PyTorch from $PYTORCH_INDEX_URL"
  python -m pip install --upgrade torch torchvision torchaudio --index-url "$PYTORCH_INDEX_URL"
else
  log "Skipping PyTorch install because INSTALL_TORCH=$INSTALL_TORCH"
fi

log "Installing ComfyUI requirements"
python -m pip install -r requirements.txt

if [ "$INSTALL_MANAGER" = "1" ]; then
  mkdir -p "$COMFY_DIR/custom_nodes"
  clone_or_update "https://github.com/Comfy-Org/ComfyUI-Manager.git" "$COMFY_DIR/custom_nodes/ComfyUI-Manager"

  if [ -f "$COMFY_DIR/custom_nodes/ComfyUI-Manager/requirements.txt" ]; then
    log "Installing ComfyUI-Manager requirements"
    python -m pip install -r "$COMFY_DIR/custom_nodes/ComfyUI-Manager/requirements.txt"
  fi
else
  log "Skipping ComfyUI-Manager install because INSTALL_MANAGER=$INSTALL_MANAGER"
fi

log "Creating model and project directories"
mkdir -p \
  "$COMFY_DIR/models/checkpoints" \
  "$COMFY_DIR/models/unet" \
  "$COMFY_DIR/models/diffusion_models" \
  "$COMFY_DIR/models/clip" \
  "$COMFY_DIR/models/vae" \
  "$COMFY_DIR/models/loras" \
  "$COMFY_DIR/models/controlnet" \
  "$COMFY_DIR/models/upscale_models" \
  "$COMFY_DIR/input" \
  "$COMFY_DIR/output" \
  "$PROJECT_DIR/assets/ip_refs" \
  "$PROJECT_DIR/assets/first_frames" \
  "$PROJECT_DIR/outputs/ip_candidates" \
  "$PROJECT_DIR/outputs/first_frames" \
  "$PROJECT_DIR/logs"

cat > "$PROJECT_DIR/run_comfyui.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
cd "$COMFY_DIR"
source "$COMFY_DIR/.venv/bin/activate"
python main.py --listen 0.0.0.0 --port \${COMFYUI_PORT:-8188}
EOF
chmod +x "$PROJECT_DIR/run_comfyui.sh"

cat > "$PROJECT_DIR/logs/README.md" <<'EOF'
# Logs

Keep generation notes here:

- prompt
- model version
- seed
- resolution
- selected output
- problems found
- next iteration
EOF

log "Setup complete"
log "Run ComfyUI with: bash $PROJECT_DIR/run_comfyui.sh"
log "Open port 8188 with AutoDL custom service or SSH local port forwarding."

