import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
import time
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
PYTHONW = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/pythonw.exe"
WATCHER = VAULT / "10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py"
OODA = VAULT / "10_Skills_Library/05_Operations/Crew/ooda_self_prompt_loop.py"
WATCHER_PID = VAULT / "10_Skills_Library/05_Operations/logs/pinkcady_watcher.pid"
OODA_PID = VAULT / "10_Skills_Library/05_Operations/logs/ooda_loop.pid"
LOG = VAULT / "10_Skills_Library/05_Operations/logs/watchdog_launcher.log"


def log(msg: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text(
            LOG.read_text(encoding="utf-8", errors="ignore") + f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def pid_alive(pid: str) -> bool:
    if not pid or not pid.strip().isdigit():
        return False
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid.strip()}", "/FO", "CSV", "/NH"],
            text=True,
            timeout=10,
        )
        return str(pid.strip()) in out and "python" in out.lower()
    except Exception:
        return False


def is_running(script_name: str, pid_file: Path) -> bool:
    try:
        pid = pid_file.read_text(encoding="utf-8", errors="ignore").strip()
    except Exception:
        pid = ""
    if pid and pid_alive(pid):
        try:
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/value"],
                text=True,
                timeout=10,
            )
            if script_name in out:
                return True
        except Exception:
            pass
    return False


def write_pid(pid_file: Path, pid: int) -> None:
    try:
        pid_file.write_text(str(pid), encoding="utf-8")
    except Exception:
        pass


def start_detached(script: Path, pid_file: Path) -> int:
    if not PYTHONW.exists():
        return -1
    try:
        proc = subprocess.Popen(
            [str(PYTHONW), str(script)],
            cwd=VAULT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | CREATE_NO_WINDOW,
            close_fds=True,
    )
        write_pid(pid_file, proc.pid)
        return proc.pid
    except Exception as exc:
        log(f"WATCHDOG_START_ERROR {exc}")
        return -1


def main() -> int:
    log("WATCHDOG_START")
    while True:
        try:
            if not is_running("pinkcady_comms_watcher.py", WATCHER_PID):
                log(f"START_WATCHER pid={start_detached(WATCHER, WATCHER_PID)}")
            else:
                log("WATCHER_ALREADY_RUNNING")

            if not is_running("ooda_self_prompt_loop.py", OODA_PID):
                log(f"START_OODA pid={start_detached(OODA, OODA_PID)}")
            else:
                log("OODA_ALREADY_RUNNING")
        except Exception as exc:
            log(f"WATCHDOG_ERROR {exc}")
        time.sleep(60)


if __name__ == "__main__":
    sys.exit(main())
