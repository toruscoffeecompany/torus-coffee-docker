#!/usr/bin/env python3
"""
Local network dashboard launcher for Torus Coffee Company.
Starts/stops/restarts the Next.js dashboard on port 3001.
Runs via Task Scheduler at boot and on demand.
"""
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DASHBOARD_DIR = VAULT / "06_Website" / "dashboard"
LOG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "logs" / "dashboard_launcher.log"
PORT = 3001

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat()}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

def is_port_in_use(port: int) -> bool:
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return f":{port}" in result.stdout
    except Exception:
        return False

def start_dashboard():
    if is_port_in_use(PORT):
        log(f"Dashboard already running on port {PORT}")
        return True

    if not DASHBOARD_DIR.exists():
        log(f"ERROR: Dashboard directory not found: {DASHBOARD_DIR}")
        return False

    try:
        log(f"Starting dashboard on port {PORT}...")
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(DASHBOARD_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | CREATE_NO_WINDOW,
    )
        time.sleep(5)
        if is_port_in_use(PORT):
            log(f"✓ Dashboard started successfully on port {PORT}")
            return True
        else:
            log(f"✗ Dashboard failed to start on port {PORT}")
            return False
    except Exception as e:
        log(f"✗ Dashboard startup error: {e}")
        return False

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    if action == "start":
        start_dashboard()
    else:
        log(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
