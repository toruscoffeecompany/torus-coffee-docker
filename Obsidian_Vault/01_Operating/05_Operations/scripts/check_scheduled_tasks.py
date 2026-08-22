#!/usr/bin/env python3
"""
Check and fix Windows scheduled tasks for Torus Coffee automations.
Ensures all Torus_* tasks are properly configured and enabled.
"""
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
LOG_DIR = AUTOMATION_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "scheduled_tasks_audit.log"

# Tasks that should be enabled for Miss Pink
TORUS_TASKS = [
    "Torus_Nightly_Calendar_Sync",
    "Torus_Automated_Verification",
    "Torus_Continuous_OODA",
    "Torus_Daily_Ops_Check",
    "Torus_Inventory_Alert",
    "Torus_Inventory_Sync",
    "Torus_Miss_Pink_Self_Heal",
    "Torus_Order_Manager",
    "Torus_Silent_Smart_System_Trigger",
    "Torus_Smart_Ticket_Cycle",
    "Torus_Social_Media_Calendar",
    "Torus_Social_Media_Check",
    "Torus_Trello_Sync",
    "Torus_Vault_Audit",
    "Torus_Vault_Cleanup",
    "Torus_Vault_Sync_To_GitHub",
    "Torus_Weekly_Obsidian_Note",
    "Torus_Weekly_Ops_Review",
    "Torus_Monthly_Inventory_Count",
    "Torus_Monthly_Obsidian_Note",
    "Torus_Monthly_Ops_Review",
    "Torus_Asset_Validator",
    "PINKCADY_SQUIDSTATION_Backup",
]

# Tasks that should remain DISABLED or belong to other crew members
SKIP_TASKS = [
    "Torus_Sir_Azure_OODA",  # Sir Azure's — do not touch
    "Torus_Continuous_OODA_Deep_Learning",  # May not exist
]

# Tasks that should be ENABLED
ENABLE_TASKS = [
    "Torus_Nightly_Calendar_Sync",
    "Torus_Continuous_OODA",
]


def log(msg: str):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def get_task_status(task_name: str):
    """Get task status and details from schtasks."""
    try:
        r = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST", "/V"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return None, None, None
        status = "unknown"
        next_run = "unknown"
        action = "unknown"
        for line in r.stdout.splitlines():
            if "Status:" in line:
                status = line.split(":", 1)[1].strip()
            elif "Next Run Time:" in line:
                next_run = line.split(":", 1)[1].strip()
            elif "Task To Run:" in line:
                action = line.split(":", 1)[1].strip()
        return status, next_run, action
    except Exception as e:
        return None, str(e), None


def fix_task(task_name: str):
    """Enable a disabled task."""
    try:
        r = subprocess.run(
            ["schtasks", "/Change", "/TN", task_name, "/ENABLE"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0, r.stdout + r.stderr
    except Exception as e:
        return False, str(e)


def main():
    log("SCHEDULED_TASKS_AUDIT_START")

    results = []
    for task in TORUS_TASKS:
        status, next_run, action = get_task_status(task)
        if status is None:
            log(f"  ⚠ {task}: not found")
            results.append({"task": task, "status": "NOT_FOUND", "action": action or ""})
            continue

        result = {
            "task": task,
            "status": status,
            "next_run": next_run,
            "action": action[:120] if action else "",
        }
        results.append(result)

        if status == "Disabled":
            if task in ENABLE_TASKS:
                ok, msg = fix_task(task)
                if ok:
                    log(f"  ✅ {task}: was Disabled → ENABLED")
                else:
                    log(f"  ✗ {task}: failed to enable — {msg[:100]}")
            else:
                log(f"  ⚠ {task}: disabled (not in enable list)")
        elif status == "Ready":
            log(f"  ✓ {task}: ready")
        elif status == "Running":
            log(f"  ⚙ {task}: running")
        else:
            log(f"  ? {task}: {status}")

    # Write results
    results_path = AUTOMATION_DIR / "reports" / f"scheduled_tasks_audit_{datetime.now().strftime('%Y%m%d')}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    summary = {
        "total": len(results),
        "ready": sum(1 for r in results if r["status"] == "Ready"),
        "disabled": sum(1 for r in results if r["status"] == "Disabled"),
        "running": sum(1 for r in results if r["status"] == "Running"),
        "not_found": sum(1 for r in results if r["status"] == "NOT_FOUND"),
    }
    log(f"AUDIT_COMPLETE summary={summary}")
    print(f"\nSummary: {summary}")
    print(f"Full report: {results_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
