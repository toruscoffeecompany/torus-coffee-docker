#!/usr/bin/env python3
"""
Create TOOL_AV verification OODA task cards on the Torus Ops board.
These are Miss Pink's own tasks - NOT Sir Green's or Sir Azure's.
"""
import sys, requests, time
sys.path.insert(0, "scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]
BOARD = "6a70a3157d0db4214ac3f9a3"

# Get list IDs
r = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/lists",
    params={"key": key, "token": token, "fields": "name,id,closed"},
    timeout=20,
)
lists = r.json()
p0_id = next((l["id"] for l in lists if l["name"].startswith("P0")), None)
p1_id = next((l["id"] for l in lists if l["name"].startswith("P1")), None)
p2_id = next((l["id"] for l in lists if l["name"].startswith("P2")), None)

# Get label IDs
r3 = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/labels",
    params={"key": key, "token": token, "fields": "name,id,color"},
    timeout=20,
)
label_map = {l["name"].lower(): l["id"] for l in r3.json()}

# Tasks - keep descriptions short and avoid problematic characters
tasks = [
    {
        "name": "[TOOL_AV] Run self-verification: docker TLS, mem limits, swappiness, log rotation",
        "desc": "Run the 5-minute self-verification from 00_Inbox/MISS_PINK_VERIFICATION_REPORT.md. 1. docker info grep tlsverify. 2. docker inspect Memory. 3. sysctl vm.swappiness. 4. docker system df. 5. Check Docker root dir. Report findings.",
        "idList": p1_id,
        "labels": ["miss-pink", "P1", "verification"],
    },
    {
        "name": "[TOOL_AV] Execute EMERGENCY ACTION PLAN if Phase 1 gaps found",
        "desc": "If verification shows gaps: Hour 1: Enable Docker TLS, set memory limits, remove privileged containers. Hour 2: Fix swappiness, log rotation, prune dangling images. Hour 3: Verify all fixes.",
        "idList": p0_id,
        "labels": ["miss-pink", "P0", "critical"],
    },
    {
        "name": "[TOOL_AV] Run TOOL_AR comprehensive Docker audit on all 3 Rigs",
        "desc": "Run TOOL_AR_COMPREHENSIVE_NETWORK_AUDIT.py against PINKCADY, SQUIDSTATION, STEALTHATTACK. Check TLS, memory limits, privileged mode, swappiness, log rotation, docker root. Document per-rig findings.",
        "idList": p1_id,
        "labels": ["miss-pink", "P1", "docker"],
    },
    {
        "name": "[TOOL_AV] Run TOOL_AG OPSEC security audit - scan vault for exposed secrets",
        "desc": "Run TOOL_AG_OPSEC_SECURITY_AUDIT.py. Scan vault for secret_scan.py issues. Check auto-archive scripts for security flaws. Set up daily cron for security scanning. Verify no bot tokens in git history.",
        "idList": p1_id,
        "labels": ["miss-pink", "P1", "security"],
    },
    {
        "name": "[TOOL_AV] Run TOOL_AH fleet health diagnostics on all 3 Rigs",
        "desc": "Run TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py on PINKCADY, SQUIDSTATION, STEALTHATTACK. Check CPU/memory/disk per rig, container health, network connectivity, service status, Tailscale mesh.",
        "idList": p2_id,
        "labels": ["miss-pink", "P2", "health"],
    },
    {
        "name": "[TOOL_AV] Verify PINKCADY Docker daemon - TLS, memory limits, no privileged containers",
        "desc": "Direct PINKCADY-only check: 1. Docker daemon config. 2. tlsverify enabled. 3. All containers have memory limits. 4. No privileged containers. 5. Docker root on separate mount.",
        "idList": p0_id,
        "labels": ["miss-pink", "P0", "pinkcady"],
    },
    {
        "name": "[TOOL_AV] System-wide scan for cmd.exe popup source",
        "desc": "Search all .py files in 10_Skills_Library/05_Operations/scripts/ and Crew/ for shell=True or subprocess without CREATE_NO_WINDOW. Check all .vbs files. Check all scheduled tasks. Ensure no process can spawn visible cmd.exe.",
        "idList": p1_id,
        "labels": ["miss-pink", "P1", "windows", "opsec"],
    },
    {
        "name": "[TOOL_AV] Create OODA tasklist - full system audit checklist for all 3 Rigs",
        "desc": "Build comprehensive OODA tasklist that the continuous_ooda_worker can follow: 1. Security audit every cycle. 2. Card dedup check. 3. Inbox processing with crew coordination. 4. Git hygiene. 5. Board health. 6. Disk monitoring. 7. Process health. Document in Crew/OODA_TASKLIST.md.",
        "idList": p2_id,
        "labels": ["miss-pink", "P2", "automation"],
    },
]

created = 0
for task in tasks:
    label_ids = []
    for ln in task["labels"]:
        if ln.lower() in label_map:
            label_ids.append(label_map[ln.lower()])

    r = requests.post(
        "https://api.trello.com/1/cards",
        params={
            "key": key,
            "token": token,
            "idList": task["idList"],
            "name": task["name"],
            "desc": task["desc"],
            "labels": ",".join(label_ids) if label_ids else "",
        },
        timeout=15,
    )
    if r.status_code == 200:
        created += 1
        print(f"Created: {task['name'][:60]}")
    else:
        print(f"FAILED: {task['name'][:60]} - {r.status_code}")
    time.sleep(0.3)

print(f"\nCreated {created}/{len(tasks)} TOOL_AV verification cards")
