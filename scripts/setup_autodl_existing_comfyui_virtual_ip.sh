#!/usr/bin/env bash
set -Eeuo pipefail

# Setup for the AutoDL ComfyUI pure image.
# This reuses the existing /root/ComfyUI service on AutoDL WebUI-6006.
# It does not start, stop, restart, or reconfigure ComfyUI.

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/vip_singing}"
COMFY_DIR="${COMFY_DIR:-/root/ComfyUI}"
PUBLIC_MODEL_DIR="${PUBLIC_MODEL_DIR:-/.autodl-model/data}"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

link_model() {
  local src="$1"
  local dst="$2"

  if [ ! -e "$src" ]; then
    echo "[missing source] $src"
    return 1
  fi

  if [ -L "$dst" ]; then
    local current
    current="$(readlink "$dst")"
    if [ "$current" = "$src" ]; then
      echo "[exists] $dst -> $src"
      return 0
    fi
    echo "[skip existing symlink] $dst -> $current"
    return 0
  fi

  if [ -e "$dst" ]; then
    echo "[skip existing file] $dst"
    return 0
  fi

  ln -s "$src" "$dst"
  echo "[linked] $dst -> $src"
}

if [ ! -d "$COMFY_DIR" ]; then
  echo "ComfyUI directory not found: $COMFY_DIR" >&2
  exit 1
fi

log "Creating project folders"
mkdir -p \
  "$PROJECT_DIR/assets/ip_refs" \
  "$PROJECT_DIR/assets/first_frames" \
  "$PROJECT_DIR/outputs/ip_candidates" \
  "$PROJECT_DIR/outputs/first_frames" \
  "$PROJECT_DIR/workflows/ip" \
  "$PROJECT_DIR/prompts" \
  "$PROJECT_DIR/logs" \
  "$COMFY_DIR/user/default/workflows/VIP/IP" \
  "$COMFY_DIR/models/diffusion_models" \
  "$COMFY_DIR/models/text_encoders" \
  "$COMFY_DIR/models/vae"

log "Linking Flux models from AutoDL public model storage"
link_model "$PUBLIC_MODEL_DIR/black-forest-labs/FLUX.1-dev/flux1-dev.safetensors" "$COMFY_DIR/models/diffusion_models/flux1-dev.safetensors"
link_model "$PUBLIC_MODEL_DIR/black-forest-labs/FLUX.1-dev/ae.safetensors" "$COMFY_DIR/models/vae/ae.safetensors"
link_model "$PUBLIC_MODEL_DIR/comfyanonymous/flux_text_encoders/clip_l.safetensors" "$COMFY_DIR/models/text_encoders/clip_l.safetensors"
link_model "$PUBLIC_MODEL_DIR/comfyanonymous/flux_text_encoders/t5xxl_fp16.safetensors" "$COMFY_DIR/models/text_encoders/t5xxl_fp16.safetensors"
link_model "$PUBLIC_MODEL_DIR/black-forest-labs/FLUX.2-klein-base-4B/flux-2-klein-base-4b.safetensors" "$COMFY_DIR/models/diffusion_models/flux-2-klein-base-4b.safetensors"
link_model "$PUBLIC_MODEL_DIR/black-forest-labs/FLUX.2-klein-base-4B/vae/diffusion_pytorch_model.safetensors" "$COMFY_DIR/models/vae/flux2-klein-vae.safetensors"

log "Writing project README and prompt template"
cat > "$PROJECT_DIR/README.md" <<'EOF'
# VIP Singing Project On AutoDL

This project reuses the existing AutoDL ComfyUI installation:

```text
ComfyUI: /root/ComfyUI
Access: AutoDL WebUI-6006
Project: /root/autodl-tmp/vip_singing
```

Do not change `start-comfyui.sh` or AutoDL port mappings. Use the existing 6006 service.
EOF

cat > "$PROJECT_DIR/prompts/ip_character_card_template.md" <<'EOF'
# Virtual IP Character Card Template

```text
Name:
Role:
Age impression:
Music style:
Visual style:
Hair:
Eyes:
Outfit:
Accessories:
Do-not-change features:
```

Positive prompt:

```text
single virtual singer, [fixed character features], medium close-up, facing camera, clear mouth, natural singing expression, soft stage lighting, clean background, high quality, stable face, detailed eyes, 9:16 vertical composition
```

Avoid:

```text
multiple people, distorted face, asymmetric eyes, deformed mouth, teeth artifacts, microphone covering mouth, hand covering face, heavy motion blur, crowded background, low quality, cropped face, extreme side view
```
EOF

if [ ! -f "$PROJECT_DIR/logs/generation_notes.md" ]; then
  cat > "$PROJECT_DIR/logs/generation_notes.md" <<'EOF'
# Generation Notes

Record prompt, seed, model, workflow, selected outputs, problems, and next iteration here.
EOF
fi

if [ -f "$PROJECT_DIR/workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json" ]; then
  cp "$PROJECT_DIR/workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json" \
    "$COMFY_DIR/user/default/workflows/VIP/IP/Flux1_DEV_Virtual_IP_Text2Image.json"
  echo "[workflow] registered UI workflow in $COMFY_DIR/user/default/workflows/VIP/IP"
fi

log "Done. Existing ComfyUI service is left unchanged."
