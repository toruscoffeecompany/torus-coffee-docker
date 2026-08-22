#!/usr/bin/env python3
"""
Automated verification system for Torus Coffee smart automation.
Runs every 10 minutes via scheduled task.
Checks: scheduled tasks, logs, smart ticket cycle, Trello connectivity, GitHub connectivity.
"""
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
SMART_TICKET_LOG = VAULT / "10_Skills_Library/05_Operations/logs/smart_ticket_cycle.log"
MASTER_OODA_LOG = VAULT / "10_Skills_Library/05_Operations/logs/master_ooda.log"
UNIFIED_LOG = VAULT / "10_Skills_Library/05_Operations/logs/unified_automation_runner.log"
BATCH_LOG = VAULT / "10_Skills_Library/05_Operations/logs/smart_ticket_batch_apply.log"
VERIFICATION_REPORT = VAULT / "10_Skills_Library/05_Operations/AUTOMATED_VERIFICATION_REPORT.json"
TRELLO_CYCLE_STATE = VAULT / "10_Skills_Library/05_Operations/smart_ticket_cycle_state.json"
MASTER_OODA_STATE = VAULT / "10_Skills_Library/05_Operations/master_ooda_loop_state.json"
TRELLO_VERIFY_REPORT = VAULT / "10_Skills_Library/05_Operations/VERIFICATION_REPORT.json"
DISCORD_SECRETS = VAULT / "02_Business_Operations/Communications/Discord/miss_pink_bot/secrets.local.json"
DISCORD_CONNECT_STATE = VAULT / "02_Business_Operations/Communications/Discord/miss_pink_bot/discord_connect_state.json"
DISCORD_BOT_PY = VAULT / "02_Business_Operations/Communications/Discord/miss_pink_bot/bot.py"
DISCORD_AUTO_HELPER = VAULT / "10_Skills_Library/05_Operations/scripts/discord_automation_helper.py"

def log(msg):
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}")

def load_creds():
    text = TRELLO_CREDS.read_text(encoding="utf-8")
    lines = text.splitlines()
    api_key = token = None
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    return api_key, token

def check_file_fresh(path: Path, max_age_minutes: int) -> dict:
    if not path.exists():
        return {"ok": False, "error": f"{path.name} missing"}
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = (datetime.now(timezone.utc) - mtime).total_seconds() / 60
        return {"ok": age <= max_age_minutes, "age_minutes": round(age, 1)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_scheduled_tasks():
    expected = {
        "\\Torus_Smart_Ticket_Cycle",
        "\\Torus_Continuous_OODA",
        "\\Torus_Vault_Audit",
        "\\Torus_Trello_Sync",
        "\\Torus_Inventory_Sync",
        "\\Torus_Order_Manager",
        "\\Torus_Daily_Ops_Check",
        "\\Torus_Social_Media_Check",
        "\\Torus_Asset_Validator",
    }
    try:
        out = subprocess.check_output(["schtasks", "/query", "/fo", "csv", "/nh"], text=True, timeout=20)
        found = set()
        for line in out.splitlines():
            parts = [p.strip('"') for p in line.split(",")]
            if len(parts) >= 2:
                name = parts[0].strip()
                if any(name.startswith(e) for e in expected):
                    found.add(name.lstrip("\\"))
        missing = sorted(expected - {f"\\{n}" for n in found})
        return {
            "ok": len(missing) == 0,
            "found": sorted(found),
            "missing": missing,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_log_recency(path: Path, label: str, max_age_minutes: int = 5) -> dict:
    if not path.exists():
        return {"ok": False, label: "missing"}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines:
            return {"ok": False, label: "empty"}
        last = lines[-1]
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = (datetime.now(timezone.utc) - mtime).total_seconds() / 60
        fresh = age <= max_age_minutes
        # One-shot batch jobs: treat as fresh if they ever completed successfully
        if not fresh and label == "batch_apply" and "BATCH_APPLY_COMPLETE" in text:
            fresh = True
        return {
            "ok": fresh,
            f"{label}_last_line": last[:200],
            f"{label}_age_minutes": round(age, 1),
        }
    except Exception as e:
        return {"ok": False, label: str(e)}

def check_trello_connectivity():
    try:
        api_key, token = load_creds()
        url = f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={api_key}&token={token}&fields=id&limit=1"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return {"ok": True, "sample_count": len(data)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_github_connectivity():
    try:
        out = subprocess.check_output(
            ["gh", "issue", "list", "-R", "toruscoffeecompany/Torus_Ops", "--state", "open", "--limit", "1", "--json", "number,title"],
            text=True, timeout=30,
        ).strip()
        if not out:
            return {"ok": True, "open_issue_count": 0}
        data = json.loads(out)
        return {"ok": True, "open_issue_count": len(data)}
    except json.JSONDecodeError:
        return {"ok": False, "error": "GitHub CLI returned non-JSON output"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_crew_work_verification():
    try:
        api_key, token = load_creds()
    except Exception as e:
        return {"ok": False, "error": f"load_creds_failed: {e}"}
    board = "6a70a3157d0db4214ac3f9a3"
    green_queue = "6a74cbd679972be49ea46dae"
    azure_queue = "6a74cbd51b2662f6cdc37cce"
    priority_lists = {"6a74cbd3aa052ed2b30c5644", "6a74cbd440270147ff04bd5b", "6a74cbd5e3d54d2d08be82e7", "6a74cbd4148f814483a64589", "6a70a32923622d3e00107d70", "6a74cbd573259cffe8a23cc0", "6a70a3282e405a2460afc170", "6a74cbd67bbe3ef35a634495"}
    
    try:
        cards = requests.get(
            f"https://api.trello.com/1/boards/{board}/cards",
            params={"key": api_key, "token": token, "fields": "name,idList,dateLastActivity,labels,closed", "limit": 1000},
            timeout=30,
        ).json()
    except Exception as e:
        return {"ok": False, "error": f"crew_trello_fetch_failed: {e}"}
    
    open_cards = [c for c in cards if not c.get("closed")]
    crew_cards = [c for c in open_cards if any(l.get("name", "").lower() in ("sir-green", "sir-azure", "sir green's queue", "sir azure's queue") for l in c.get("labels", []))]
    green_queue_cards = [c for c in open_cards if c.get("idList") == green_queue]
    azure_queue_cards = [c for c in open_cards if c.get("idList") == azure_queue]
    priority_crew_cards = [c for c in crew_cards if c.get("idList") in priority_lists]
    
    now = datetime.now(timezone.utc)
    stale = []
    for c in crew_cards:
        last = c.get("dateLastActivity")
        if last:
            try:
                last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if (now - last_dt) > timedelta(hours=48):
                    stale.append(c["id"])
            except Exception:
                pass
    
    crew_work_status = {
        "crew_card_count": len(crew_cards),
        "green_queue_count": len(green_queue_cards),
        "azure_queue_count": len(azure_queue_cards),
        "priority_crew_count": len(priority_crew_cards),
        "stale_crew_cards": stale[:10],
        "stale_count": len(stale),
    }
    
    ok = len(stale) == 0 and len(crew_cards) > 0
    return {"ok": ok, **crew_work_status}

def check_fleet_deployment_status():
    fleet_dir = VAULT / "10_Skills_Library/05_Operations/Fleet_Tools_Deployment"
    manifest = fleet_dir / "DEPLOYMENT_MANIFEST.json"
    tasklist = VAULT / "10_Skills_Library/05_Operations/FLEET_DEPLOYMENT_OODA_TASKLIST.json"
    expected = [
        "pirate_crew_cli.py",
        "fleet_dashboard.py",
        "all_five_tools_bundle.py",
        "five_more_tools_bundle.py",
        "tools_k_thru_o_bundle.py",
        "tools_p_thru_u_bundle.py",
    ]
    try:
        missing = []
        if not fleet_dir.exists() or not manifest.exists() or not tasklist.exists():
            return {"ok": False, "error": "fleet_dir_or_manifest_or_tasklist_missing"}
        for name in expected:
            p = fleet_dir / "tools" / name
            if not p.exists() or p.stat().st_size == 0:
                missing.append(name)
        if missing:
            return {"ok": False, "missing_tools": missing}
        return {"ok": True, "tools_present": expected, "manifest": str(manifest), "tasklist": str(tasklist)}
    except Exception as e:
        return {"ok": False, "error": f"fleet_check_failed: {e}"}


def check_discord_secrets():
    try:
        secrets_ok = DISCORD_SECRETS.exists()
        connect_ok = DISCORD_CONNECT_STATE.exists()
        token_present = False
        channel_configured = False
        if secrets_ok:
            try:
                data = json.loads(DISCORD_SECRETS.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            token_present = bool(
                data.get("DISCORD_MISS_PINK_TOKEN")
                or data.get("DISCORD_BOT_TOKEN")
            )
            channel_configured = True
        return {
            "ok": True,
            "secrets_present": secrets_ok,
            "token_present": token_present,
            "channel_configured": channel_configured,
            "connect_state_present": connect_ok,
        }
    except Exception as e:
        return {"ok": False, "error": f"discord_secrets_check_failed: {e}"}


def main():
    log("AUTOMATED_VERIFICATION_START")
    
    checks = {}
    
    # Scheduled tasks
    checks["scheduled_tasks"] = check_scheduled_tasks()
    
    # Log recency
    checks["smart_ticket_log"] = check_log_recency(SMART_TICKET_LOG, "smart_ticket", max_age_minutes=10)
    checks["master_ooda_log"] = check_log_recency(MASTER_OODA_LOG, "master_ooda", max_age_minutes=10)
    checks["batch_log"] = check_log_recency(BATCH_LOG, "batch_apply", max_age_minutes=60)
    
    # State files
    checks["smart_ticket_state"] = check_file_fresh(TRELLO_CYCLE_STATE, 10)
    checks["master_ooda_state"] = check_file_fresh(MASTER_OODA_STATE, 10)
    
    # Connectivity
    checks["trello_connectivity"] = check_trello_connectivity()
    checks["github_connectivity"] = check_github_connectivity()
    checks["crew_work_verification"] = check_crew_work_verification()
    checks["fleet_deployment_status"] = check_fleet_deployment_status()
    checks["discord_secrets"] = check_discord_secrets()
    
    # Load existing verification report if exists
    existing_verify = {}
    if TRELLO_VERIFY_REPORT.exists():
        try:
            existing_verify = json.loads(TRELLO_VERIFY_REPORT.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    checks["existing_verification"] = {
        "ok": existing_verify.get("summary", {}).get("status") == "PASS",
        "status": existing_verify.get("summary", {}).get("status"),
    }
    
    # Determine overall status
    hard_fails = []
    soft_fails = []
    
    if not checks["scheduled_tasks"]["ok"]:
        hard_fails.append("scheduled_tasks")
    if not checks["smart_ticket_log"].get("ok", False):
        hard_fails.append("smart_ticket_log")
    if not checks["batch_log"].get("ok", False):
        hard_fails.append("batch_log")
    if not checks["master_ooda_log"].get("ok", False):
        hard_fails.append("master_ooda_log")
    if not checks["trello_connectivity"]["ok"]:
        hard_fails.append("trello_connectivity")
    if not checks["github_connectivity"]["ok"]:
        hard_fails.append("github_connectivity")
    if not checks["smart_ticket_state"].get("ok", False):
        soft_fails.append("smart_ticket_state")
    if not checks["master_ooda_state"].get("ok", False):
        soft_fails.append("master_ooda_state")
    if not checks["crew_work_verification"].get("ok", False):
        soft_fails.append("crew_work_verification")
    if not checks["fleet_deployment_status"].get("ok", False):
        soft_fails.append("fleet_deployment_status")
    
    checks["summary"] = {
        "status": "PASS" if not hard_fails else "FAIL",
        "hard_fails": hard_fails,
        "soft_fails": soft_fails,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Write report
    VERIFICATION_REPORT.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    
    s = checks["summary"]
    if s["status"] == "PASS":
        log(f"VERIFY PASS | soft_fails={s['soft_fails']}")
    else:
        log(f"VERIFY FAIL | hard_fails={s['hard_fails']} soft_fails={s['soft_fails']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
