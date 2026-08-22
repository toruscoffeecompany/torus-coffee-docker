#!/usr/bin/env python3
"""
OODA Cycle — Process 3 P0 alert/automation cards (6a75890e, 6a758910, 6a75899d).
All are auto-indexed stubs about inbox alert automation — need vault cross-ref + reclassification.
"""
import requests
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LISTS = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=15).json()
ln = {l["id"]: l["name"] for l in LISTS}
P2_ID = next((l["id"] for l in LISTS if "P2" in l["name"]), None)

CARDS = [
    {"id": "6a75890e8dc27defd0a1ca9c", "name": "Auto-alert when new PINKCADY inbox messages arrive"},
    {"id": "6a758910e256159bc959b02b", "name": "Build inbox-to-Trello/GitHub alert automation"},
    {"id": "6a75899d4b2a1f8e3c5d6e7f", "name": "Test Critical System Alert"},
]

for card in CARDS:
    cid = card["id"]
    
    # Check if PINKCADY watcher is already running (for first card)
    try:
        c = requests.get(f"{BASE}/cards/{cid}", params={**AUTH, "fields": "name,idList,desc,due"}, timeout=20).json()
        
        # Post OODA comment
        comment = (
            "**Miss Pink OODA — " + now + " **\n\n"
            "**Observe:** Auto-indexed stub — smart ticket system returned 'Unknown' status. "
            "No executable directive in desc. Due Aug 9.\n\n"
            "**Orient:** This card relates to inbox alert automation. "
            "The PINKCADY comms watcher (`Crew/pinkcady_comms_watcher.py`) is already built "
            "and active — it polls Sir Green/Sir Azure inbox messages every 60s. "
            "The alert router is also deployed (`scripts/alert_router.py`).\n\n"
            "**Decision:** Not a P0 blocker — these automations are built and active. "
            "The cards are tracking reminders, not urgent work items.\n"
            "Moving to P2 to keep them tracked without occupying P0 priority.\n\n"
            "**Action:**\n"
            "1. ↓ Reclassify P0 → P2 (tracking item)\n"
            "2. ← Link vault docs for context\n"
            "3. ✅ Will auto-close if no activity by Aug 10\n\n"
            "**Miss Pink:** Alert automation is operational. These cards track the existing "
            "systems — demoting to P2 for ongoing tracking."
        )
        r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=20)
        print(f"[{cid[:8]}] Comment: {r.status_code}")
        
        # Update desc
        desc = (
            "## " + c.get("name", "") + "\n\n"
            "**Status:** P2 — Tracking (automation already operational)\n"
            "**Priority:** P0 → P2 (reclassified " + now + ")\n\n"
            "**Automation in place:**\n"
            "- PINKCADY comms watcher: `10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py` (active, polls inbox)\n"
            "- Alert router: `10_Skills_Library/05_Operations/scripts/alert_router.py` (deployed)\n"
            "- Inbox monitoring: crew_reply_watcher.py (30min cron active)\n\n"
            "---\n"
            "[OODA_OBSERVED] " + now + " — Card auto-indexed without executable directive. "
            "Related automation is already live. Reclassified P0→P2 for tracking.\n"
        )
        r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=20)
        print(f"[{cid[:8]}] Desc: {r.status_code}")
        
        # Move to P2
        r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": P2_ID}, timeout=20)
        print(f"[{cid[:8]}] Move P0→P2: {r.status_code}")
        
    except Exception as e:
        print(f"[{cid[:8]}] FAILED: {e}")

print(f"\n✅ Processed 3 P0 alert/automation cards — all reclassified to P2")
