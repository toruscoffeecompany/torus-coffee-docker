#!/usr/bin/env python3
"""
PINKCADY Rig Reporter — pushes local status to Captain's dashboard.
Endpoint: POST http://localhost:8089/api/rig-report
Auth: X-Rig-Key header
"""
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
DASHBOARD_URL = "http://192.168.0.39:8080/api/rig-report"
RIG_KEY = ""
VAULT = BASE
RIG_NAME = "PINKCADY"
WATCHER_LOG = VAULT / "10_Skills_Library" / "05_Operations" / "Crew" / "pinkcady_comms.log"
GIT_DIR = VAULT


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def tailscale_status() -> bool:
    try:
        result = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=10)
        return "online" in result.stdout.lower() or result.returncode == 0
    except Exception:
        return False


def service_status(name: str) -> str:
    try:
        result = subprocess.run(["sc", "query", name], capture_output=True, text=True, timeout=10)
        if "RUNNING" in result.stdout:
            return "running"
        if "STOPPED" in result.stdout:
            return "stopped"
        return "unknown"
    except Exception:
        return "unknown"


def watcher_running() -> bool:
    try:
        if not WATCHER_LOG.exists():
            return False
        lines = WATCHER_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        return any("started" in line.lower() or "running" in line.lower() for line in lines[-20:])
    except Exception:
        return False


def inbox_count() -> int:
    try:
        inbox = Path("/z/MISS_PINK_INBOX")
        if not inbox.exists():
            return -1
        return len(list(inbox.glob("*.msg.md")))
    except Exception:
        return -1


def git_status() -> dict:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            cwd=str(GIT_DIR),
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        dirty = len(lines) > 0
        sha = ""
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(GIT_DIR),
                text=True,
                timeout=5,
            ).strip()
        except Exception:
            pass
        return {"dirty": dirty, "changes": len(lines), "sha": sha}
    except Exception:
        return {"dirty": False, "changes": 0, "sha": ""}


def disk_usage() -> float:
    try:
        result = subprocess.run(["df", "-h", str(VAULT)], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[-1].split()
            if len(parts) >= 5:
                return parts[4]
        return "unknown"
    except Exception:
        return "unknown"


def build_report() -> dict:
    git = git_status()
    payload = {
        "rig": RIG_NAME,
        "timestamp": now_iso(),
        "status": "online",
        "tailscale": tailscale_status(),
        "inbox_count": inbox_count(),
        "services": {
            "pinkcady_comms_watcher": "running" if watcher_running() else "stopped",
        },
        "git": git,
        "disk_usage": disk_usage(),
        "notes": "Auto-reported by PINKCADY rig reporter",
    }
    return payload


def send_report(payload: dict) -> bool:
    headers = {"Content-Type": "application/json"}
    if RIG_KEY:
        headers["X-Rig-Key"] = RIG_KEY
    try:
        resp = requests.post(DASHBOARD_URL, json=payload, headers=headers, timeout=10)
        print(f"POST {DASHBOARD_URL} -> {resp.status_code}")
        return resp.status_code in (200, 202)
    except Exception as exc:
        print(f"Dashboard post failed: {exc}")
        return False


def main() -> int:
    payload = build_report()
    print(json.dumps(payload, indent=2))
    ok = send_report(payload)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
