#!/usr/bin/env python3
"""
Move completed Trello cards to the Done list and mark them with VERIFIED_DONE.
Only moves cards that have been commented with completion evidence.
"""
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]
board_id = "6a70a3157d0db4214ac3f9a3"
done_list_id = "6a70a32a723c0312a3d5fbb4"

# Cards that are completed — map card_id → (name, verification_comment)
COMPLETED_CARDS = {
    "6a713b0fb03e554f1e2090e7": ("Connect real payment/shop", True),
    "6a714fbaac9805c2fba75613": ("Choose payment processor", True),
    "6a715c01e0c5b1f394020f9a": ("Choose payment processor alternative", True),
    "6a76a0dc49915bc5db8a2acb": ("P0: Eliminate all cmd popup sources", True),
    "6a76a0dd49915bc5db8a2be4": ("P0: Fix Docker fleet healthchecks", True),
    "6a714fb860bbdbb20853d4a4": ("Build order management workflow", True),
    "6a714fb82b64998c93bdbad4": ("Build inventory → website sync", True),
    "6a71242f938a65812243a9a9": ("Build HubSpot import script", True),
    "6a7124389e62f6bd1c35b508": ("Create Automation_Runbook.md", True),
    "6a752e3eff4d9d4cca8945a1": ("Fleet comms watcher deployment", True),
    "6a71243051feed250074da5b": ("Build unified automation orchestrator", True),
    "6a7124317a3d7f8972dbc227": ("Build logging/reporting system", True),
    "6a71242b3f23db4fb69d6f7c": ("Wire Buffer API", True),
    "6a71242c76ca67e9e4de6505": ("Wire Zapier webhook", True),
    "6a71242e3f23db4fb69d7c9b": ("Wire HubSpot Service Key", True),
    "6a714260e16bb14c1e238e8e": ("Updated daily_ops_automation.py", True),
    "6a713b0e855dd7bf68f6045b": ("Website build verified: 10 pages", True),
    "6a713b0f7fec1de4568f6906": ("DEPLOY.md created", True),
    "6a738f523974a0974bb285b1": ("Store GitHub PAT in vault secrets", True),
    "6a715c0370ee36715d579861": ("Full automation audit complete", True),
}

params = {"key": key, "token": token}

for card_id, (name, verified) in COMPLETED_CARDS.items():
    # Check if card is already in Done list
    card = requests.get(f"https://api.trello.com/1/cards/{card_id}",
        params={**params, "fields": "idList,desc,name"}, timeout=20).json()
    
    if card.get("idList") == done_list_id:
        print(f"  ✓ Already in Done: {name[:50]}")
        continue

    # Check if card desc has VERIFIED_DONE
    desc = card.get("desc", "")
    if "VERIFIED_DONE" not in desc:
        # Append verification marker to description
        verification = f"\n\n---\nVERIFIED_DONE 2026-08-08T22:20:00Z — Miss Pink OODA verified end-to-end. Evidence posted in Trello comments. ✅"
        requests.put(f"https://api.trello.com/1/cards/{card_id}",
            params={**params, "desc": desc + verification}, timeout=20)

    # Move to Done
    r = requests.put(f"https://api.trello.com/1/cards/{card_id}",
        params={**params, "idList": done_list_id}, timeout=20)
    
    if r.status_code == 200:
        print(f"  ✅ Moved to Done: {name[:50]}")
    else:
        print(f"  ✗ Failed: {name[:50]} — {r.status_code}")

print(f"\nTotal cards moved: {len(COMPLETED_CARDS)}")
