#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/song.wav [demucs_model]" >&2
  exit 1
fi

INPUT_AUDIO="$1"
MODEL="${2:-htdemucs}"
WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"
OUT_ROOT="${OUT_ROOT:-$WORKFLOW_ROOT/output/separated}"

if [[ ! -f "$INPUT_AUDIO" ]]; then
  echo "Input audio not found: $INPUT_AUDIO" >&2
  exit 1
fi

mkdir -p "$OUT_ROOT" "$WORKFLOW_ROOT/logs"

export PATH="$CONDA_ROOT/bin:$PATH"
# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"

python - <<'PY'
try:
    import torchcodec  # noqa: F401
except ModuleNotFoundError:
    raise SystemExit(
        "Missing Python package: torchcodec\n"
        "Install it once in the rvc environment, then rerun this script:\n"
        "  source /root/miniconda3/etc/profile.d/conda.sh\n"
        "  conda activate rvc\n"
        "  python -m pip install --no-cache-dir 'torchcodec==0.11.*' --index-url https://download.pytorch.org/whl/cpu\n"
    )
except Exception as exc:
    raise SystemExit(
        "torchcodec is installed, but its native libraries failed to load.\n"
        "This is usually an FFmpeg/libstdc++ runtime issue in the rvc conda environment.\n"
        "Try this once, then rerun this script:\n"
        "  source /root/miniconda3/etc/profile.d/conda.sh\n"
        "  conda activate rvc\n"
        "  export LD_LIBRARY_PATH=\"$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}\"\n"
        "  python - <<'PY2'\n"
        "  from torchcodec.encoders import AudioEncoder\n"
        "  print('torchcodec ok')\n"
        "  PY2\n"
        "If that still fails, install the newer conda C++ runtime:\n"
        "  conda install -y -c conda-forge libstdcxx-ng\n"
        f"\nOriginal error:\n{exc}\n"
    )
PY

demucs --two-stems=vocals -n "$MODEL" -o "$OUT_ROOT" "$INPUT_AUDIO"

echo "Demucs output root: $OUT_ROOT/$MODEL"
