#!/usr/bin/env pythonw.exe
"""start_watcher_safe.py — Launch daemon watcher processes with PID-based dedup.

FIX: Previously checked name='python.exe' only via wmic, but launcher
uses pythonw.exe — so is_running() never matched and duplicate daemons
spawned every cycle. Now checks BOTH python.exe AND pythonw.exe via PID files.
"""
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
PYTHON = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/pythonw.exe"
WATCHER = VAULT / "10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py"
OODA = VAULT / "10_Skills_Library/05_Operations/Crew/ooda_self_prompt_loop.py"
PID_DIR = VAULT / "10_Skills_Library/05_Operations/logs/pids"

DETACHED = subprocess.DETACHED_PROCESS if hasattr(subprocess, 'DETACHED_PROCESS') else 0
CREATE_NEW_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0


def is_running(script_name: str) -> bool:
    """Check if a script is already running using PID file + wmic verification.
    FIX: Uses pythonw.exe instead of python.exe for hidden execution."""
    PID_DIR.mkdir(parents=True, exist_ok=True)
    pid_file = PID_DIR / f"{script_name}.pid"
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, IOError):
        pid_file.unlink(missing_ok=True)
        return False

    try:
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW,
        )
        if str(pid) not in proc.stdout:
            pid_file.unlink(missing_ok=True)
            return False
        # Verify via wmic that the process is running our script
        wmic = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],
            capture_output=True, text=True, timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
        return script_name in wmic.stdout
    except Exception:
        return False


def write_pid(script_name: str, pid: int) -> None:
    PID_DIR.mkdir(parents=True, exist_ok=True)
    (PID_DIR / f"{script_name}.pid").write_text(str(pid))


def main() -> int:
    started = []
    if not is_running("pinkcady_comms_watcher.py"):
        proc = subprocess.Popen(
            [str(PYTHON), str(WATCHER)],
            cwd=VAULT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=DETACHED | CREATE_NEW_GROUP | CREATE_NO_WINDOW,
        )
        write_pid("pinkcady_comms_watcher.py", proc.pid)
        started.append(f"watcher pid={proc.pid}")
    else:
        print("watcher already running")

    if not is_running("ooda_self_prompt_loop.py"):
        proc = subprocess.Popen(
            [str(PYTHON), str(OODA)],
            cwd=VAULT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=DETACHED | CREATE_NEW_GROUP | CREATE_NO_WINDOW,
        )
        write_pid("ooda_self_prompt_loop.py", proc.pid)
        started.append(f"ooda pid={proc.pid}")
    else:
        print("ooda already running")

    print("; ".join(started) if started else "nothing started")
    return 0


if __name__ == "__main__":
    sys.exit(main())
