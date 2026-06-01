#!/usr/bin/env python3
"""Probe the Windows offload host and report availability without failing hard."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime


def probe(host: str, timeout: int = 20) -> dict:
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}", host, "powershell", "-NoProfile", "-Command", "$PSVersionTable.PSVersion; python --version; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        return {
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "host": host,
            "available": p.returncode == 0,
            "returncode": p.returncode,
            "output": (p.stdout + p.stderr).strip()[-3000:],
        }
    except Exception as exc:
        return {"checked_at": datetime.now().isoformat(timespec="seconds"), "host": host, "available": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="yin")
    args = parser.parse_args()
    result = probe(args.host)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
