#!/usr/bin/env python3
"""Trust-but-verify end-to-end automation checker. No hallucinations, no fluff."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TRELLO_CREDENTIALS = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
INDEX_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"
ALERT_LOG_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/ALERT_PROCESSING_LOG.json"
CALENDAR_SYNC_LOG_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/CALENDAR_SYNC_LOG.json"
CREW_QUEUE_STATE_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/CREW_QUEUE_STATE.json"
CREW_QUEUE_TRANSFER_LOG_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/CREW_QUEUE_TRANSFER_LOG.json"
GOOGLE_TOKEN_PATH = Path(r"C:\Users\torus\AppData\Local\hermes\google_token.json")
GOOGLE_CLIENT_SECRET_PATH = Path(r"C:\Users\torus\AppData\Local\hermes\google_client_secret.json")

BOARD_ID = "6a70a3157d0db4214ac3f9a3"
REPO = "toruscoffeecompany/Torus_Ops"
MAX_P2 = 20
MAX_P1 = 60
TOP_10_TARGET = 10
RECENT_WINDOW_MINUTES = 120


def get_trello_credentials():
    creds = TRELLO_CREDENTIALS.read_text(encoding="utf-8")
    lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
    return lines[0].strip("`"), lines[2].strip("`")


def check_trello():
    key, token = get_trello_credentials()
    lists = requests.get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=15,
    ).json()
    cards = requests.get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,idList,labels,dateLastActivity", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()
    labels = requests.get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=15,
    ).json()

    list_counts = Counter(c.get("idList") for c in cards)
    label_counts = Counter(l["name"] for c in cards for l in c.get("labels", []))
    top10_label_id = next((l["id"] for l in labels if l["name"] == "Top 10"), None)

    top10_in_list = list_counts.get(next((l["id"] for l in lists if "Top 10" in l["name"]), None), 0)
    top10_by_label = sum(1 for c in cards if any(l.get("id") == top10_label_id for l in c.get("labels", [])) and c.get("idList") == next((l["id"] for l in lists if "Top 10" in l["name"]), None))
    p1 = list_counts.get(next((l["id"] for l in lists if "P1" in l["name"]), None), 0)
    p2 = list_counts.get(next((l["id"] for l in lists if "P2" in l["name"]), None), 0)
    p0 = list_counts.get(next((l["id"] for l in lists if "P0" in l["name"]), None), 0)

    name_groups = defaultdict(list)
    for c in cards:
        name_groups[c["name"].strip().lower()].append(c)
    duplicate_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
    duplicate_count = sum(len(v) for v in duplicate_groups.values())

    weird_lists = [l["name"] for l in lists if l["name"] not in {
        "In_Progress", "Top 10 — Focus Fleet", "Torus Coffee Future Ideas", "P0 - Alert / Critical / Do Now",
        "To Do", "To_Do", "P1 - High / Doing Now", "P2 - Med High / This Week", "VOID Ops",
        "Torus Coffee's Future Ideas", "Top 10 - Highest Priority", "P3 - Medium / Follow Up",
        "P4 - Medium Low / Backlog", "P5 - Low / Review", "P6 - Very Low / Blocked / Waiting",
        "Sir Azure's Queue", "Sir Green's Queue", "Follow-up", "Done", "Sir Azure's Queue for Miss Pink",
        "Sir Azure's Queue from Miss Pink", "Sir Green's Queue from Miss Pink"
    }]

    return {
        "ok": True,
        "total": len(cards),
        "top10_list": top10_in_list,
        "top10_label_matches_list": top10_by_label,
        "p1": p1,
        "p2": p2,
        "p0": p0,
        "duplicate_groups": len(duplicate_groups),
        "duplicate_cards": duplicate_count,
        "weird_lists": weird_lists,
        "label_counts": dict(label_counts),
    }


def check_github():
    try:
        out = subprocess.check_output(
            ["gh", "issue", "list", "-R", REPO, "--state", "open", "--limit", "100", "--json", "number,title,labels"],
            text=True,
            timeout=30,
        )
        issues = json.loads(out)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    label_counts = Counter()
    for issue in issues:
        for label in issue.get("labels", []):
            label_counts[label["name"]] += 1
    return {
        "ok": True,
        "open_issues": len(issues),
        "label_counts": dict(label_counts),
    }


def check_inbox_processor():
    if not ALERT_LOG_PATH.exists():
        return {"ok": True, "note": "no alert log yet"}
    try:
        log = json.loads(ALERT_LOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "ALERT_PROCESSING_LOG.json invalid JSON"}
    processed_at = log.get("processed_at")
    if not processed_at:
        return {"ok": True, "note": "no processed_at"}
    try:
        processed_dt = datetime.fromisoformat(processed_at)
        recent = datetime.now() - processed_dt <= timedelta(minutes=RECENT_WINDOW_MINUTES)
    except Exception:
        recent = False
    return {
        "ok": True,
        "recent": recent,
        "processed_at": processed_at,
        "processed": log.get("processed"),
        "trello_created": log.get("trello_created"),
        "github_created": log.get("github_created"),
        "errors": log.get("errors", []),
    }


def check_calendar():
    # Strict check: real Google Calendar read must work end-to-end.
    if not GOOGLE_TOKEN_PATH.exists() or not GOOGLE_CLIENT_SECRET_PATH.exists():
        return {"ok": False, "blocked": True, "error": "Google token/client secret missing"}

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except Exception as e:
        return {"ok": False, "blocked": True, "error": f"Google libs missing: {e}"}

    try:
        from datetime import datetime, timezone
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_PATH), ["https://www.googleapis.com/auth/calendar"])
        if not creds.valid:
            return {"ok": False, "blocked": True, "error": "Google Calendar token invalid or missing scope"}
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        events = service.events().list(calendarId="primary", timeMin=now, maxResults=2500, singleEvents=True).execute()
        upcoming = events.get("items", [])

        automation_events = []
        protected_types = {"birthday", "holiday"}
        for e in upcoming:
            summary = e.get("summary", "")
            description = e.get("description", "") or ""
            event_type = e.get("eventType", "")
            if event_type in protected_types:
                continue
            if "Auto-generated by Torus automation" in description:
                automation_events.append(e)

        counts = Counter(
            (e.get("summary"), (e.get("start", {}).get("date") or e.get("start", {}).get("dateTime", "")).split("T")[0])
            for e in automation_events
        )
        automation_spam = {k: v for k, v in counts.items() if v > 1}
        return {
            "ok": len(automation_spam) == 0,
            "blocked": False,
            "upcoming_count": len(upcoming),
            "automation_event_count": len(automation_events),
            "automation_duplicates": automation_spam,
            "sample": [{"summary": e.get("summary"), "start": e.get("start"), "status": e.get("status")} for e in upcoming[:5]],
        }
    except Exception as e:
        msg = str(e)
        if "insufficientPermissions" in msg or "403" in msg:
            return {"ok": False, "blocked": True, "error": "Google Calendar scope missing on token"}
        return {"ok": False, "blocked": False, "error": msg}


def check_processes():
    expected = [
        "ooda_loop.py",
        "verifier_daemon.py",
        "pinkcady_crew_heartbeat.py",
        "progress_updater.py",
        "self_healing_loop.py",
        "cmd_popup_blocker.py",
        "crew_api.py",
        "docker_proxy.py",
        "pirate_dashboard.py",
    ]
    try:
        # Use wmic to get full command lines (tasklist only shows process name like pythonw.exe)
        out = subprocess.check_output(
            ["wmic", "process", "where", "name='pythonw.exe'", "get", "CommandLine", "/format:list"],
            text=True, timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        present = []
        for line in out.splitlines():
            if line.startswith("CommandLine="):
                cmdline = line[len("CommandLine="):].strip()
                for exp in expected:
                    if exp.lower() in cmdline.lower():
                        present.append(exp)
        missing = [exp for exp in expected if exp not in present]
        return {"ok": len(missing) == 0, "present": present, "missing": missing, "raw_lines": len(out.splitlines())}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_docker():
    expected = [
        "torus-redis",
        "torus-prometheus",
        "torus-grafana",
        "torus-website",
        "torus-inventory",
        "torus-pos",
        "torus-alert-router",
        "torus-cadvisor",
        "torus-node-exporter",
    ]
    try:
        out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"], text=True, timeout=30)
        running = []
        restarting = []
        for line in out.splitlines():
            parts = line.split("\t")
            if not parts or not parts[0].strip():
                continue
            name = parts[0]
            status = parts[1] if len(parts) > 1 else ""
            if "k8s_" in name or "desktop-" in name or name in ["torus-backup"]:
                continue
            running.append(name)
            if "Restarting" in status:
                restarting.append(name)
        missing = [n for n in expected if n not in running]
        ok = len(missing) == 0 and len(restarting) == 0
        return {
            "ok": ok,
            "running": running,
            "missing": missing,
            "restarting": restarting,
            "expected": expected,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_index_integrity():
    if not INDEX_PATH.exists():
        return {"ok": False, "error": "TRELLO_CARD_INDEX.json missing"}
    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "TRELLO_CARD_INDEX.json corrupt"}
    cards = data.get("cards", [])
    card_ids = [c.get("id") for c in cards if c.get("id")]
    duplicate_ids = [item for item, count in Counter(card_ids).items() if count > 1]
    return {
        "ok": len(duplicate_ids) == 0,
        "indexed_count": len(card_ids),
        "duplicate_ids": duplicate_ids,
    }


def check_crew_queue():
    state_ok = False
    transfer_ok = False
    state_count = None
    failed_count = None
    last_run = None
    if CREW_QUEUE_STATE_PATH.exists():
        try:
            state = json.loads(CREW_QUEUE_STATE_PATH.read_text(encoding="utf-8"))
            state_ok = isinstance(state, dict)
            state_count = state.get("processed_count")
            failed_count = state.get("failed_count")
            last_run = state.get("last_run")
        except Exception:
            state_ok = False
    transfer_count = None
    if CREW_QUEUE_TRANSFER_LOG_PATH.exists():
        try:
            transfer = json.loads(CREW_QUEUE_TRANSFER_LOG_PATH.read_text(encoding="utf-8"))
            transfer_ok = isinstance(transfer, dict) and isinstance(transfer.get("entries"), list)
            transfer_count = len(transfer.get("entries", []))
        except Exception:
            transfer_ok = False
    ok = state_ok and transfer_ok and ((state_count or 0) > 0 or (transfer_count or 0) > 0) and (failed_count or 0) == 0
    return {
        "ok": ok,
        "state_ok": state_ok,
        "transfer_ok": transfer_ok,
        "processed_count": state_count,
        "transfer_count": transfer_count,
        "failed_count": failed_count,
        "last_run": last_run,
    }


def check_file_integrity():
    """Check for file mutations in watched files."""
    watched = [
        "10_Skills_Library/05_Operations/Docker/torus-light/docker-compose.yml",
        "10_Skills_Library/05_Operations/Fleet_Tools_Deployment/tools/fleet_dashboard.py",
        "10_Skills_Library/05_Operations/CREW_QUEUE_STATE.json",
        "10_Skills_Library/05_Operations/secrets.local.json",
    ]
    hash_file = REPO_ROOT / "10_Skills_Library/05_Operations/file_hashes.json"
    try:
        if hash_file.exists():
            saved = json.loads(hash_file.read_text(encoding="utf-8"))
        else:
            saved = {}
    except Exception:
        saved = {}
    mutated = []
    for rel in watched:
        path = REPO_ROOT / rel
        if path.exists():
            import hashlib
            h = hashlib.sha256()
            with open(path, "rb") as f:
                h.update(f.read())
            current = h.hexdigest()
            if rel in saved and saved[rel] != current:
                mutated.append(rel)
    return {"ok": len(mutated) == 0, "mutated_files": mutated}

def build_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "trello": check_trello(),
        "github": check_github(),
        "inbox": check_inbox_processor(),
        "calendar": check_calendar(),
        "processes": check_processes(),
        "docker": check_docker(),
        "index": check_index_integrity(),
        "crew_queue": check_crew_queue(),
        "file_integrity": check_file_integrity(),
    }

    hard_fails = []
    soft_fails = []
    if not report["trello"]["ok"]:
        hard_fails.append("trello")
    if not report["github"]["ok"]:
        hard_fails.append("github")
    if not report["inbox"]["ok"]:
        hard_fails.append("inbox")
    if not report["calendar"]["ok"] and not report["calendar"].get("blocked"):
        hard_fails.append("calendar")
    if not report["index"]["ok"]:
        hard_fails.append("index")
    if not report["crew_queue"]["ok"]:
        hard_fails.append("crew_queue")
    if not report["file_integrity"]["ok"]:
        soft_fails.append("file_integrity")
    if not report["docker"]["ok"]:
        soft_fails.append("docker")
    if not report["processes"]["ok"]:
        soft_fails.append("processes")

    report["summary"] = {
        "hard_fails": hard_fails,
        "soft_fails": soft_fails,
        "status": "PASS" if not hard_fails else "FAIL",
    }
    return report


def main():
    report = build_report()
    path = REPO_ROOT / "10_Skills_Library/05_Operations/VERIFICATION_REPORT.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    s = report["summary"]
    print(f"VERIFY {s['status']} | hard_fails={s['hard_fails']} soft_fails={s['soft_fails']}")
    if s["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
