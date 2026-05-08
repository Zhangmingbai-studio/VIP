#!/usr/bin/env python3
"""
SCP uploader fallback for large ComfyUI model files.

Use this when SFTP upload through the AutoDL SSH proxy keeps dropping.

Usage:
  python scripts/upload_large_model_scp_to_autodl.py "D:\\models\\novaOrangeXL_exV20.safetensors"
"""

from __future__ import annotations

import argparse
import getpass
import os
import posixpath
import socket
import sys
import time
from pathlib import Path

import paramiko
from scp import SCPClient


DEFAULT_HOST = "connect.bjb2.seetacloud.com"
DEFAULT_PORT = 41578
DEFAULT_USER = "root"
DEFAULT_REMOTE_DIR = "/root/ComfyUI/models/checkpoints"


def human_size(value: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


class Progress:
    def __init__(self) -> None:
        self.start = time.monotonic()
        self.last = self.start
        self.last_sent = 0

    def __call__(self, filename: bytes, size: int, sent: int) -> None:
        now = time.monotonic()
        if now - self.last < 2 and sent < size:
            return
        window_speed = (sent - self.last_sent) / max(now - self.last, 1e-6)
        total_speed = sent / max(now - self.start, 1e-6)
        eta = (size - sent) / total_speed if total_speed > 0 else 0
        pct = sent / size * 100 if size else 0
        print(
            f"{pct:6.2f}%  {human_size(sent)}/{human_size(size)}  "
            f"{human_size(window_speed)}/s  ETA {eta/60:.1f} min",
            flush=True,
        )
        self.last = now
        self.last_sent = sent


def run_remote(client: paramiko.SSHClient, command: str, timeout: int = 60) -> str:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    rc = stdout.channel.recv_exit_status()
    if rc != 0:
        raise RuntimeError(f"remote command failed ({rc}): {command}\n{err}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a large model to AutoDL using SCP.")
    parser.add_argument("local_path")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--remote-name", default=None)
    args = parser.parse_args()

    local_path = Path(args.local_path).expanduser().resolve()
    if not local_path.is_file():
        print(f"Local file not found: {local_path}", file=sys.stderr)
        return 2

    remote_name = args.remote_name or local_path.name
    remote_final = posixpath.join(args.remote_dir, remote_name)
    remote_part = remote_final + ".scp.part"

    password = os.environ.get("AUTODL_SSH_PASSWORD")
    if not password:
        password = getpass.getpass(f"Password for {args.user}@{args.host}:{args.port}: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=args.host,
            port=args.port,
            username=args.user,
            password=password,
            timeout=30,
            banner_timeout=30,
            auth_timeout=30,
        )
        transport = client.get_transport()
        if transport is not None:
            transport.set_keepalive(15)

        run_remote(client, f"mkdir -p {args.remote_dir!r}; rm -f {remote_part!r}")

        print(f"[local]  {local_path}")
        print(f"[remote] {remote_final}")
        print(f"[size]   {human_size(local_path.stat().st_size)}")
        print("[mode]   scp fallback, no resume")

        with SCPClient(client.get_transport(), progress=Progress(), socket_timeout=60) as scp:
            scp.put(str(local_path), remote_path=remote_part)

        expected = local_path.stat().st_size
        remote_size = int(run_remote(client, f"stat -c %s {remote_part!r}").strip())
        if remote_size != expected:
            raise RuntimeError(
                f"remote size mismatch: {human_size(remote_size)} vs local {human_size(expected)}"
            )

        run_remote(client, f"mv -f {remote_part!r} {remote_final!r}")
        print(f"[done] uploaded to {remote_final}")
    except (paramiko.SSHException, socket.error, OSError, RuntimeError) as exc:
        print(f"\n[error] {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

