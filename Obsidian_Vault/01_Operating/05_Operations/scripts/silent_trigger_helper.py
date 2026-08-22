#!/usr/bin/env python3
"""Silent trigger helper: ensure exactly one master_ooda_loop.py is running without popups."""
import os
import subprocess
from subprocess import CREATE_NO_WINDOW
import time
from pathlib import Path

SCRIPT = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\master_ooda_loop.py")
PYTHONW = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\pythonw.exe")
PIDFILE = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\logs\master_ooda_loop.pid")


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            text=True,
            timeout=10,
        )
        return str(pid) in out and "python" in out.lower()
    except Exception:
        return False


def _existing_pid() -> int:
    try:
        return int(PIDFILE.read_text(encoding="utf-8", errors="ignore").strip() or "0")
    except Exception:
        return 0


def _kill(pid: int) -> None:
    try:
        subprocess.run(["taskkill", "/f", "/pid", str(pid)], check=False, capture_output=True, timeout=10)
    except Exception:
        pass


def _launch() -> None:
    if not SCRIPT.exists() or not PYTHONW.exists():
        return
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen(
        [str(PYTHONW), str(SCRIPT)],
        creationflags=flags | CREATE_NO_WINDOW,
        close_fds=True,
    )


def main() -> int:
    if not SCRIPT.exists() or not PYTHONW.exists():
        return 0

    pid = _existing_pid()
    if pid and _pid_alive(pid):
        try:
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/value"],
                text=True,
                timeout=10,
            )
            if "master_ooda_loop.py" in out:
                return 0
        except Exception:
            pass
        _kill(pid)

    _launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
