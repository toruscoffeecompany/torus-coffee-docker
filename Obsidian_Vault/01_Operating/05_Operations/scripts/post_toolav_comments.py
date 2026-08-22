#!/usr/bin/env python3
"""Post verification comments on TOOL_AV Trello cards."""
import requests
import sys
import time

sys.path.insert(0, "10_Skills_Library/05_Operations/scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]

r = requests.get(
    "https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards",
    params={"key": key, "token": token, "fields": "id,name,closed"},
    timeout=60,
)

FLOOD_COMMENT = (
    "SMART BRIDGE FLOOD - ROOT CAUSE FOUND + FIXED:\n\n"
    "ROOT CAUSE: crew_queue_automation.py create_void_card() had NO deduplication. "
    "Every time smart_ticket_cycle.py promoted the Smart Bridge card, "
    "crew_queue_automation.py created a NEW mirrored VOID card. "
    "414 duplicates on VOID board, 2 on Torus Ops.\n\n"
    "FIXES APPLIED (all scripts now have name-based dedup):\n"
    "1. crew_queue_automation.py - create_void_card() checks find_existing_card_by_name() before creating\n"
    "2. ooda_loop_agent.py - create_trello_card() deduped\n"
    "3. inbox_processor.py - create_trello_card() deduped\n"
    "4. miss_pink_inbox_watcher.py - create_trello_card() deduped\n"
    "5. Crew coordination lock (crew_queue_sync) added to crew_queue_automation.run()\n\n"
    "CLEANUP: Archived 413 duplicates on VOID board (kept 1 newest). Archived 1 on Torus Ops.\n"
    "All card-creating processes killed. All scheduled tasks disabled until verified."
)

EMERGENCY_COMMENT = (
    "Phase 1 complete - emergency action plan fully executed:\n"
    "- K8s disabled, Docker restarted, 10 containers running\n"
    "- 414 Smart Bridge cards reduced to 1 (413 archived on VOID, 1 on Torus)\n"
    "- Root cause: duplicate card creation - all scripts now have name-based dedup\n"
    "- Crew coordination lock deployed across all 3 rigs"
)

for c in r.json():
    if c.get("closed", False):
        continue
    n = c["name"]
    if any(x in n for x in ["SMART BRIDGE FLOOD", "anti-duplication", "flood"]):
        requests.post(
            f"https://api.trello.com/1/cards/{c['id']}/actions/comments",
            params={"key": key, "token": token},
            json={"text": FLOOD_COMMENT},
            timeout=10,
        )
        print(f"Updated: {n[:60]}")
        time.sleep(0.5)
    if "Emergency Action Plan" in n and not c.get("closed", False):
        requests.post(
            f"https://api.trello.com/1/cards/{c['id']}/actions/comments",
            params={"key": key, "token": token},
            json={"text": EMERGENCY_COMMENT},
            timeout=10,
        )
        print(f"Updated: {n[:60]}")
        time.sleep(0.5)
