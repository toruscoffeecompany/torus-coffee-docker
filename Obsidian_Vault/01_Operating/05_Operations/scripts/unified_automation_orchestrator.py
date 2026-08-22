#!/usr/bin/env python3
"""
Unified Automation Orchestrator for Torus Coffee Company.

Runs all automation scripts in dependency order with proper error handling,
logging, and state tracking. Designed to be called by master_ooda_loop.py
or run standalone.

Usage:
    venv/Scripts/python.exe scripts/unified_automation_orchestrator.py run
    venv/Scripts/python.exe scripts/unified_automation_orchestrator.py run --check-only
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
SCRIPTS_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "scripts"
LOG_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "orchestrator.log"
STATE_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "orchestration_state.json"

# Python interpreter — use venv pythonw for headless, python for visible
PYTHON = str(VAULT / "10_Skills_Library" / "05_Operations" / "venv" / "Scripts" / "python.exe")

# Scripts in execution order (dependencies first)
ORCHESTRATION_PIPELINE = [
    {
        "name": "credential_check",
        "script": "credential_check.py",
        "description": "Verify all credential files are accessible",
        "critical": True,
        "timeout": 30,
    },
    {
        "name": "daily_ops",
        "script": "daily_ops_automation.py",
        "description": "Daily ops check: inventory, backup, git status",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "trello_top10_maintenance",
        "script": "trello_top10_maintenance.py",
        "description": "Maintain Top 10 card cap on Torus_Ops board",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "trello_full_audit",
        "script": "trello_full_audit.py",
        "description": "Archive duplicates, fix unlabeled cards on Torus_Ops",
        "critical": False,
        "timeout": 120,
    },
    {
        "name": "social_media_status",
        "script": "social_media_automation.py",
        "args": "status",
        "description": "Check social media platform connection status",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "buffer_status",
        "script": "buffer_automation.py",
        "args": "status",
        "description": "Check Buffer API connection and channels",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "zapier_status",
        "script": "zapier_automation.py",
        "args": "status",
        "description": "Check Zapier webhook configuration",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "hubspot_import",
        "script": "hubspot_crm.py",
        "args": "import",
        "description": "Import vault contacts into HubSpot",
        "critical": False,
        "timeout": 60,
    },
    {
        "name": "inventory_sync",
        "script": "inventory_to_website_sync.py",
        "args": "--dry-run",
        "description": "Verify inventory matches website data",
        "critical": False,
        "timeout": 30,
    },
    {
        "name": "order_check",
        "script": "order_manager.py",
        "args": "--list",
        "description": "List current orders",
        "critical": False,
        "timeout": 30,
    },
    {
        "name": "inbox_watcher",
        "script": "miss_pink_inbox_watcher.py",
        "args": "--once",
        "description": "Process crew inbox messages",
        "critical": False,
        "timeout": 120,
    },
    {
        "name": "pinkcady_watcher",
        "script": "pinkcady_comms_watcher.py",
        "args": "--once",
        "description": "Process PINKCADY inbox",
        "critical": False,
        "timeout": 60,
    },
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(msg: str):
    line = f"[{now_iso()}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"runs": []}
    return {"runs": []}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_script(step: dict, check_only: bool = False) -> dict:
    """Run a single orchestration step."""
    if check_only:
        result = {
            "name": step["name"],
            "script": step["script"],
            "description": step["description"],
            "critical": step["critical"],
            "status": "check_only",
            "output": "",
            "returncode": 0,
            "error": None,
            "duration": 0,
        }
        return result

    script_path = SCRIPTS_DIR / step["script"]
    if not script_path.exists():
        result = {
            "name": step["name"],
            "script": step["script"],
            "status": "script_not_found",
            "output": "",
            "returncode": -1,
            "error": f"Script not found: {script_path}",
            "duration": 0,
        }
        log(f"  ✗ {step['name']}: script not found")
        return result

    cmd = [PYTHON, str(script_path)]
    if step.get("args"):
        cmd.extend(step["args"].split())

    start = time.time()
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=step["timeout"],
            cwd=str(VAULT),
        )
        duration = round(time.time() - start, 2)
        result = {
            "name": step["name"],
            "script": step["script"],
            "description": step["description"],
            "critical": step["critical"],
            "status": "success" if r.returncode == 0 else "failed",
            "output": (r.stdout + r.stderr)[:2000],
            "returncode": r.returncode,
            "error": None if r.returncode == 0 else f"Exit code {r.returncode}",
            "duration": duration,
        }
        if r.returncode == 0:
            log(f"  ✓ {step['name']}: OK ({duration}s)")
        else:
            log(f"  ✗ {step['name']}: FAILED exit={r.returncode} ({duration}s)")
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start, 2)
        result = {
            "name": step["name"],
            "script": step["script"],
            "status": "timeout",
            "output": "",
            "returncode": -1,
            "error": f"Timed out after {step['timeout']}s",
            "duration": duration,
        }
        log(f"  ⚠ {step['name']}: TIMEOUT ({duration}s)")
    except Exception as e:
        duration = round(time.time() - start, 2)
        result = {
            "name": step["name"],
            "script": step["script"],
            "status": "error",
            "output": "",
            "returncode": -1,
            "error": str(e)[:500],
            "duration": duration,
        }
        log(f"  ✗ {step['name']}: ERROR {e} ({duration}s)")

    return result


def run_orchestrator(check_only: bool = False) -> dict:
    """Run the full automation pipeline."""
    state = load_state()
    run_entry = {
        "timestamp": now_iso(),
        "check_only": check_only,
        "steps": [],
        "summary": {},
    }

    log(f"ORCHESTRATOR_START check_only={check_only} steps={len(ORCHESTRATION_PIPELINE)}")

    for step in ORCHESTRATION_PIPELINE:
        result = run_script(step, check_only=check_only)
        run_entry["steps"].append(result)

        # If a critical step fails in non-check mode, stop
        if step["critical"] and result.get("status") == "failed" and not check_only:
            log(f"CRITICAL_FAILURE {step['name']}: stopping orchestration")
            break

    # Build summary
    statuses = [s.get("status", "") for s in run_entry["steps"]]
    run_entry["summary"] = {
        "total": len(statuses),
        "success": sum(1 for s in statuses if s == "success"),
        "failed": sum(1 for s in statuses if s in ("failed", "error")),
        "timeout": sum(1 for s in statuses if s == "timeout"),
        "script_not_found": sum(1 for s in statuses if s == "script_not_found"),
        "check_only": sum(1 for s in statuses if s == "check_only"),
    }

    state["runs"].append(run_entry)
    state["runs"] = state["runs"][-10:]  # Keep last 10 runs
    save_state(state)

    log(f"ORCHESTRATOR_COMPLETE summary={run_entry['summary']}")
    return run_entry


def print_summary(run_entry: dict):
    """Print human-readable summary."""
    print(f"\n{'='*60}")
    print(f"  Orchestration Run — {run_entry['timestamp']}")
    print(f"{'='*60}")
    s = run_entry["summary"]
    print(f"  Total:     {s['total']}")
    print(f"  Success:   {s['success']}")
    print(f"  Failed:    {s['failed']}")
    print(f"  Timeout:   {s['timeout']}")
    print(f"  NotFound:  {s['script_not_found']}")
    print(f"{'='*60}\n")

    for step in run_entry["steps"]:
        status_icon = "✓" if step["status"] == "success" else "✗"
        print(f"  {status_icon} [{step['status']:^14s}] {step['name']:30s} ({step.get('duration', 0)}s)")
    print()


def main():
    check_only = "--check-only" in sys.argv
    check_only = check_only or (len(sys.argv) > 1 and sys.argv[1] == "check")

    run_entry = run_orchestrator(check_only=check_only)
    print_summary(run_entry)

    # Exit non-zero if any critical step failed
    for step in run_entry["steps"]:
        if step.get("critical") and step.get("status") in ("failed", "error", "timeout"):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
