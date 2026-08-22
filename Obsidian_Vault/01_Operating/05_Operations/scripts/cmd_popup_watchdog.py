#!/usr/bin/env pythonw.exe
"""cmd_popup_watchdog.py — Real-time cmd.exe popup killer.
Runs as a hidden background daemon via pythonw.exe.
Monitors for and kills any visible cmd.exe processes every 3 seconds.

Deployed from miss_pink_self_heal.py — fix for persistent cmd.exe popup windows.
Kills any cmd.exe process that appears in a console session (indicates a popup window).
"""
import csv
import io
import subprocess
import time
import sys
import os
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG = VAULT / "10_Skills_Library/05_Operations/logs/cmd_watchdog.log"

def log(msg: str) -> None:
    from datetime import datetime, timezone
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        if LOG.stat().st_size > 100 * 1024:
            LOG.with_suffix(".log.1").unlink(missing_ok=True)
            LOG.replace(LOG.with_suffix(".log.1"))
    except Exception:
        pass

def find_visible_cmd_processes() -> list:
    """Find cmd.exe processes running in console sessions (popup windows).
    Uses Python's csv module to properly parse tasklist CSV output
    (handles commas in memory usage like "3,940 K")."""
    pids = []
    try:
        out = subprocess.check_output([
            "tasklist", "/FI", "IMAGENAME eq cmd.exe",
            "/FO", "CSV"
        ], text=True, timeout=10,
           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        # Use csv.reader to properly parse CSV fields (handles "3,940 K" mem usage)
        reader = csv.reader(io.StringIO(out))
        header = next(reader, None)  # Skip header row
        for row in reader:
            if len(row) >= 2:
                img_name = row[0].strip()
                pid_str = row[1].strip()
                session = row[3].strip() if len(row) > 3 else "?"
                # Only kill if it's exactly 'cmd.exe' (not cncmd.exe Windows component)
                if img_name == 'cmd.exe' and pid_str.isdigit():
                    pids.append(int(pid_str))
    except Exception:
        pass
    return pids

def kill_pid(pid: int) -> bool:
    """Kill a process by PID silently."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True, text=True, timeout=5,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        return True
    except Exception:
        return False

def main() -> int:
    log("CMD_POPUP_WATCHDOG_START")
    killed_total = 0
    while True:
        try:
            pids = find_visible_cmd_processes()
            for pid in pids:
                if kill_pid(pid):
                    killed_total += 1
                    log(f"KILLED_SPAWNED_CMD PID={pid} total_killed={killed_total}")
            time.sleep(3)  # Check every 3 seconds
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"WATCHDOG_ERROR: {e}")
            time.sleep(10)
    log(f"CMD_POPUP_WATCHDOG_STOP killed={killed_total}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
