#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-6008}"
WORKFLOW_ROOT="${WORKFLOW_ROOT:-/root/autodl-tmp/vip_singing/audio_workflow}"
RVC_ROOT="${RVC_ROOT:-$WORKFLOW_ROOT/tools/Retrieval-based-Voice-Conversion-WebUI}"
CONDA_ROOT="${CONDA_ROOT:-/root/miniconda3}"

export PATH="$CONDA_ROOT/bin:$PATH"

if [[ ! -d "$RVC_ROOT" ]]; then
  echo "RVC repo not found: $RVC_ROOT" >&2
  exit 1
fi

python - "$PORT" <<'PY'
import socket
import sys

port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
try:
    busy = sock.connect_ex(("127.0.0.1", port)) == 0
finally:
    sock.close()
if busy:
    print(f"Port {port} is already in use.", file=sys.stderr)
    sys.exit(1)
PY

mkdir -p \
  "$WORKFLOW_ROOT/logs" \
  "$RVC_ROOT/assets/weights" \
  "$RVC_ROOT/assets/indices" \
  "$RVC_ROOT/assets/hubert" \
  "$RVC_ROOT/assets/rmvpe" \
  "$RVC_ROOT/assets/uvr5_weights" \
  "$RVC_ROOT/logs"

# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate rvc

cd "$RVC_ROOT"
exec python infer-web.py --port "$PORT" --pycmd python --noautoopen
