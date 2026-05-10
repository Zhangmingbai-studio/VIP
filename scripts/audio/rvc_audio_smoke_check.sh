#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
RVC_ROOT="${RVC_ROOT:-$WORKFLOW_ROOT/tools/Retrieval-based-Voice-Conversion-WebUI}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"

export PATH="$CONDA_ROOT/bin:$PATH"
# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc

cd "$RVC_ROOT"
mkdir -p assets/weights assets/indices assets/hubert assets/rmvpe assets/uvr5_weights logs

python - <<'PY'
import shutil
from pathlib import Path

import demucs
import faiss
import gradio
import gradio_client
import librosa
import soundfile
import torch

print("python packages: ok")
print("torch:", torch.__version__, "cuda:", torch.cuda.is_available(), torch.version.cuda)
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none")
print("gradio:", gradio.__version__, "gradio_client:", gradio_client.__version__)
print("librosa:", librosa.__version__, "soundfile:", soundfile.__version__)
print("faiss:", faiss.__version__, "demucs:", getattr(demucs, "__version__", "import-ok"))

checks = {
    "hubert": Path("assets/hubert/hubert_base.pt"),
    "rmvpe": Path("assets/rmvpe/rmvpe.pt"),
}
for name, path in checks.items():
    print(f"{name} model:", "present" if path.exists() else f"missing ({path})")

weights = sorted(Path("assets/weights").glob("*.pth"))
indices = sorted(Path("assets/indices").glob("*.index"))
print("voice pth count:", len(weights))
print("voice index count:", len(indices))
print("ffmpeg:", shutil.which("ffmpeg") or "missing")
PY
