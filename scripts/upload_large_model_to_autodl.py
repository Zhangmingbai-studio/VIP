#!/usr/bin/env python3
"""
Resumable SFTP uploader for large ComfyUI model files.

Usage:
  python scripts/upload_large_model_to_autodl.py "D:\\models\\novaOrangeXL_exV20.safetensors"

Password:
  Set AUTODL_SSH_PASSWORD, or enter it when prompted.
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


def mkdir_p(sftp: paramiko.SFTPClient, path: str) -> None:
    parts: list[str] = []
    current = path
    while current not in ("", "/"):
        parts.append(current)
        current = posixpath.dirname(current)
    for item in reversed(parts):
        try:
            sftp.stat(item)
        except OSError:
            sftp.mkdir(item)


def remote_size(sftp: paramiko.SFTPClient, path: str) -> int | None:
    try:
        return int(sftp.stat(path).st_size)
    except OSError:
        return None


def upload_resumable(
    sftp: paramiko.SFTPClient,
    local_path: Path,
    remote_path: str,
    *,
    chunk_size: int = 8 * 1024 * 1024,
    overwrite: bool = False,
) -> None:
    local_size = local_path.stat().st_size
    remote_dir = posixpath.dirname(remote_path)
    remote_part = remote_path + ".part"

    mkdir_p(sftp, remote_dir)

    final_size = remote_size(sftp, remote_path)
    if final_size == local_size and not overwrite:
        print(f"[skip] remote file already complete: {remote_path} ({human_size(local_size)})")
        return
    if final_size is not None and not overwrite:
        raise RuntimeError(
            f"Remote final file already exists with different size: {remote_path} "
            f"({human_size(final_size)} vs local {human_size(local_size)}). "
            "Use --overwrite if you really want to replace it."
        )
    if overwrite:
        for path in (remote_path, remote_part):
            try:
                sftp.remove(path)
            except OSError:
                pass

    offset = remote_size(sftp, remote_part) or 0
    if offset > local_size:
        raise RuntimeError(
            f"Remote partial file is larger than local file: {remote_part} "
            f"({human_size(offset)} > {human_size(local_size)}). Remove it or use --overwrite."
        )

    mode = "ab" if offset else "wb"
    start_time = time.monotonic()
    last_time = start_time
    last_bytes = offset

    print(f"[local]  {local_path}")
    print(f"[remote] {remote_path}")
    print(f"[size]   {human_size(local_size)}")
    if offset:
        print(f"[resume] continuing from {human_size(offset)}")

    with local_path.open("rb") as src:
        src.seek(offset)
        with sftp.file(remote_part, mode) as dst:
            uploaded = offset
            while uploaded < local_size:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                dst.write(chunk)
                uploaded += len(chunk)

                now = time.monotonic()
                if now - last_time >= 2 or uploaded == local_size:
                    window_speed = (uploaded - last_bytes) / max(now - last_time, 1e-6)
                    total_speed = (uploaded - offset) / max(now - start_time, 1e-6)
                    remaining = local_size - uploaded
                    eta = remaining / total_speed if total_speed > 0 else 0
                    pct = uploaded / local_size * 100
                    print(
                        f"\r{pct:6.2f}%  {human_size(uploaded)}/{human_size(local_size)}  "
                        f"{human_size(window_speed)}/s  ETA {eta/60:.1f} min",
                        end="",
                        flush=True,
                    )
                    last_time = now
                    last_bytes = uploaded
            print()

    part_size = remote_size(sftp, remote_part)
    if part_size != local_size:
        raise RuntimeError(
            f"Upload incomplete: remote partial size {human_size(part_size or 0)}, "
            f"local size {human_size(local_size)}"
        )

    try:
        sftp.remove(remote_path)
    except OSError:
        pass
    sftp.rename(remote_part, remote_path)
    print(f"[done] uploaded to {remote_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a large ComfyUI model to AutoDL with resume support.")
    parser.add_argument("local_path", help="Local model file path, e.g. D:\\models\\novaOrangeXL_exV20.safetensors")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--remote-name", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    local_path = Path(args.local_path).expanduser().resolve()
    if not local_path.is_file():
        print(f"Local file not found: {local_path}", file=sys.stderr)
        return 2

    remote_name = args.remote_name or local_path.name
    remote_path = posixpath.join(args.remote_dir, remote_name)

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
        sftp = client.open_sftp()
        try:
            upload_resumable(sftp, local_path, remote_path, overwrite=args.overwrite)
        finally:
            sftp.close()
    except (paramiko.SSHException, socket.error, OSError, RuntimeError) as exc:
        print(f"\n[error] {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    print("\nNext:")
    print("  1. Refresh ComfyUI model list or refresh the WebUI page.")
    print("  2. Open VIP / IP / Nova_Orange_XL_Illustrious_Text2Image.json.")
    print(f"  3. Select checkpoint: {remote_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

