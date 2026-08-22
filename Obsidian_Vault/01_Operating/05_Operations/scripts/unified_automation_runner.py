#!/usr/bin/env python3
"""
Unified Torus automation runner.
Runs every 5 minutes via scheduled task.
Sequence: smart ticket cycle -> continuous OODA worker.
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_DIR = VAULT / "10_Skills_Library/05_Operations/logs"
SMART_TICKET_LOG = LOG_DIR / "smart_ticket_cycle.log"
OODA_LOG = LOG_DIR / "continuous_ooda_worker.log"
PYTHON = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"
SMART_TICKET_SCRIPT = VAULT / "10_Skills_Library/05_Operations/scripts/smart_ticket_cycle.py"
OODA_SCRIPT = VAULT / "10_Skills_Library/05_Operations/scripts/continuous_ooda_worker.py"

def log(msg):
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)

def run_script(script_path, log_path, name):
    log(f"{name}_START")
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            result = subprocess.run(
                [str(PYTHON), str(script_path)],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300,
            )
        log(f"{name}_COMPLETE exit={result.returncode}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log(f"{name}_TIMEOUT after 300s")
        return False
    except Exception as e:
        log(f"{name}_ERROR: {e}")
        return False

def main():
    log("UNIFIED_AUTOMATION_RUNNER_START")
    
    # Step 1: Smart ticket cycle
    smart_ok = run_script(SMART_TICKET_SCRIPT, SMART_TICKET_LOG, "SMART_TICKET_CYCLE")
    
    # Step 2: Continuous OODA worker
    ooda_ok = run_script(OODA_SCRIPT, OODA_LOG, "CONTINUOUS_OODA_WORKER")
    
    log(f"UNIFIED_AUTOMATION_RUNNER_COMPLETE smart={smart_ok} ooda={ooda_ok}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
