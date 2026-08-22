#!/usr/bin/env pythonw.exe
"""launch_watcher.py — Start the Pinkcady comms watcher daemon.

FIX: Uses PID files for reliable dedup (was using wmic which only checked
python.exe, not pythonw.exe, causing duplicate instances to spawn every
scheduled task cycle). Now checks both python.exe and pythonw.exe.
"""
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
PYTHON = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/pythonw.exe"
LAUNCHER = VAULT / "10_Skills_Library/05_Operations/scripts/start_watcher_safe.py"
DETACHED = subprocess.DETACHED_PROCESS if hasattr(subprocess, 'DETACHED_PROCESS') else 0
CREATE_NEW_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
PID_DIR = VAULT / "10_Skills_Library/05_Operations/logs/pids"


def is_running(script_name: str) -> bool:
    """Check if a script is already running using PID files + process verification.
    FIX: Previously checked name='python.exe' but launcher uses pythonw.exe,
    so duplicate instances were spawned every cycle."""
    PID_DIR.mkdir(parents=True, exist_ok=True)
    pid_file = PID_DIR / f"{script_name}.pid"
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, IOError):
        pid_file.unlink(missing_ok=True)
        return False

    # Check if process is alive
    try:
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW,
        )
        if str(pid) not in proc.stdout:
            pid_file.unlink(missing_ok=True)
            return False
        # Verify it's running the right script (via wmic, checks BOTH python.exe and pythonw.exe)
        wmic = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],
            capture_output=True, text=True, timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
        return script_name in wmic.stdout
    except Exception:
        return False


def write_pid(script_name: str, pid: int) -> None:
    """Write PID to file for dedup tracking."""
    PID_DIR.mkdir(parents=True, exist_ok=True)
    (PID_DIR / f"{script_name}.pid").write_text(str(pid))


def run_launcher() -> int:
    if is_running("pinkcady_comms_watcher.py"):
        print("WATCHER_ALREADY_RUNNING")
        return 0
    print("STARTING_WATCHER")
    proc = subprocess.Popen(
        [str(PYTHON), str(LAUNCHER)],
        cwd=VAULT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=DETACHED | CREATE_NEW_GROUP | CREATE_NO_WINDOW,
    )
    print(f"LAUNCHER_STARTED pid={proc.pid}")
    # FIX: Write PID file so is_running() can detect this instance next cycle
    try:
        write_pid("pinkcady_comms_watcher.py", proc.pid)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(run_launcher())
