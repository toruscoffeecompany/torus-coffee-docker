#!/usr/bin/env python3
"""
PINKCADY Crew Heartbeat — posts Miss Pink's status to Captain's dashboard.
Endpoint: POST http://localhost:8089/api/crew_heartbeat
"""
import json
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CREATE_NO_WINDOW

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

VAULT = Path(r"D:\\Work\\Torus Coffee Company LLC")
DASHBOARD_URL = "http://192.168.0.39:8080/api/crew_heartbeat"
RIG_NAME = "PINKCADY"
WATCHER_LOG = VAULT / "10_Skills_Library" / "05_Operations" / "Crew" / "pinkcady_comms.log"
GIT_DIR = VAULT
INTERVAL = 300  # 5 minutes


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{now_iso()}] {msg}"
    print(line)
    try:
        log_file = VAULT / "10_Skills_Library" / "05_Operations" / "logs" / "pinkcady_crew_heartbeat.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\\n")
    except Exception:
        pass


def tailscale_status() -> bool:
    try:
        result = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW)
        return "online" in result.stdout.lower() or result.returncode == 0
    except Exception:
        return False


def watcher_running() -> bool:
    try:
        if not WATCHER_LOG.exists():
            return False
        lines = WATCHER_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        return any("started" in line.lower() or "running" in line.lower() for line in lines[-20:])
    except Exception:
        return False


def git_status() -> dict:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            cwd=str(GIT_DIR),
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=CREATE_NO_WINDOW,
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
                creationflags=CREATE_NO_WINDOW,
            ).strip()
        except Exception:
            pass
        return {"dirty": dirty, "changes": len(lines), "sha": sha}
    except Exception:
        return {"dirty": False, "changes": 0, "sha": ""}


def build_heartbeat() -> dict:
    payload = {
        "ship": RIG_NAME,
        "timestamp": now_iso(),
        "status": "online",
        "tailscale": tailscale_status(),
        "services": {
            "pinkcady_comms_watcher": "running" if watcher_running() else "stopped",
        },
        "git": git_status(),
        "notes": "PINKCADY crew heartbeat from Miss Pink automation",
    }
    return payload


def send_heartbeat(payload: dict) -> bool:
    try:
        resp = requests.post(DASHBOARD_URL, json=payload, timeout=10)
        print(f"POST {DASHBOARD_URL} -> {resp.status_code}")
        return resp.status_code in (200, 202)
    except Exception as exc:
        print(f"Dashboard post failed: {exc}")
        return False


def main() -> int:
    log("PINKCADY_CREW_HEARTBEAT_STARTED — loop mode")
    while True:
        try:
            payload = build_heartbeat()
            print(json.dumps(payload, indent=2))
            ok = send_heartbeat(payload)
            if ok:
                log(f"HEARTBEAT_SENT status=online git_dirty={payload.get('git',{}).get('dirty',False)}")
            else:
                log("HEARTBEAT_SEND_FAILED")
        except Exception as exc:
            log(f"HEARTBEAT_ERROR: {exc}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    raise SystemExit(main())
