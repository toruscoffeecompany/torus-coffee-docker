#!/usr/bin/env pythonw.exe
"""
cmd_popup_emergency_blocker.py — UNKILLABLE cmd.exe popup suppressor.

This process NEVER exits. Every possible exception is caught.
The main loop runs with 30ms check interval.
All subprocess calls use CREATE_NO_WINDOW.
"""
import subprocess
import time
import os
import sys
import signal
from datetime import datetime, timezone

BASE = r"D:\Work\Torus Coffee Company LLC"
LOG = os.path.join(BASE, "cmd_blocker_emergency.log")
LOCK = os.path.join(BASE, "cmd_popup_blocker.lock")

CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def log(msg):
    try:
        with open(LOG, 'a') as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    except:
        pass

# Write PID file
try:
    _pid_dir = os.path.join(BASE, "10_Skills_Library", "05_Operations", "logs", "pids")
    os.makedirs(_pid_dir, exist_ok=True)
    with open(os.path.join(_pid_dir, "cmd_popup_blocker.pid"), 'w') as _f:
        _f.write(str(os.getpid()))
except:
    pass

# Write lock file — NEVER remove this (so keepalive dedup always works)
try:
    with open(LOCK, 'w') as _f:
        _f.write(str(os.getpid()))
except:
    pass

log("EMERGENCY_BLOCKER_START")

# Kill any existing cmd.exe first
try:
    subprocess.run(['taskkill', '/F', '/IM', 'cmd.exe', '/T'],
        capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
except:
    pass

killed = 0

# Main loop — EVERYTHING is wrapped so this NEVER exits
while True:
    try:
        # Fast path: check if any cmd.exe is running
        r = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV'],
            capture_output=True, text=True, timeout=2,
            creationflags=CREATE_NO_WINDOW
        )
        for line in r.stdout.split('\n')[1:]:  # Skip header
            line = line.strip().strip('"')
            if line.startswith('cmd.exe'):
                parts = line.split(',')
                pid = ''.join(c for c in parts[1].strip() if c.isdigit()) if len(parts) > 1 else ''
                if pid and pid.isdigit():
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid, '/T'],
                            capture_output=True, timeout=2, creationflags=CREATE_NO_WINDOW)
                        killed += 1
                        log(f"KILL_PID={pid} total={killed}")
                    except:
                        pass
        time.sleep(0.03)  # 30ms — faster than any window can render
    except KeyboardInterrupt:
        # Never actually exit — keep running
        log("KEYBOARD_INTERRUPT — continuing")
        time.sleep(1)
    except Exception as e:
        log(f"ERROR: {e} — continuing")
        time.sleep(0.5)
