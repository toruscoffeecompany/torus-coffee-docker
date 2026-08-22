#!/usr/bin/env python3
"""Fix and process 2 remaining alert cards with correct IDs."""
import requests
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LISTS = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=15).json()
P2_ID = next((l["id"] for l in LISTS if "P2" in l["name"]), None)

CARDS = [
    {"id": "6a7589103196cfb8339ed071", "name": "Build inbox-to-Trello/GitHub alert automation"},
    {"id": "6a75899de72bd0cf31beb36f", "name": "Test Critical System Alert"},
]

for card in CARDS:
    cid = card["id"]
    c = requests.get(f"{BASE}/cards/{cid}", params={**AUTH, "fields": "name,idList,desc"}, timeout=20).json()

    comment = (
        "**Miss Pink OODA — " + now + " **\n\n"
        "**Observe:** Auto-indexed stub — smart ticket returned 'Unknown'. No executable directive. Due Aug 9.\n\n"
        "**Orient:** Related inbox alert automation already built and active:\n"
        "- PINKCADY comms watcher: `10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py`\n"
        "- Alert router: `10_Skills_Library/05_Operations/scripts/alert_router.py`\n"
        "- Crew reply watcher: `crew_reply_watcher.py` (30min cron)\n\n"
        "**Decision:** Not a P0 blocker — automation is operational. Demoting to P2 for tracking.\n"
        "Moving P0 → P2 + linking vault docs."
    )
    r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=20)
    print(f"[{cid[:8]}] Comment: {r.status_code}")

    desc = (
        "## " + c.get("name", "") + "\n\n"
        "**Status:** P2 — Tracking (automation operational)\n"
        "**Priority:** P0 → P2 (reclassified " + now + ")\n\n"
        "**Automation in place:**\n"
        "- PINKCADY comms watcher: `10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py` (active)\n"
        "- Alert router: `10_Skills_Library/05_Operations/scripts/alert_router.py` (deployed)\n"
        "- Inbox monitoring: crew_reply_watcher.py (30min cron active)\n\n"
        "---\n"
        "[OODA_OBSERVED] " + now + " — Reclassified P0→P2. Alert automation already live. "
        "Tracking item, not urgent.\n"
    )
    r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=20)
    print(f"[{cid[:8]}] Desc: {r.status_code}")

    r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": P2_ID}, timeout=20)
    print(f"[{cid[:8]}] Move P0→P2: {r.status_code}")

print("\n✅ 2 remaining alert cards processed")
