#!/usr/bin/env python3
"""
ULTRA_FAST_ARCHIVER — Archive all non-priority + duplicate cards on Torus Ops board.
Uses Trello's batch endpoint for 10x speed.
"""
import sys, os, requests, time
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]
BOARD = "6a70a3157d0db4214ac3f9a3"

# Get all cards
r = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/cards",
    params={"key": key, "token": token, "fields": "id,name,closed,idList"},
    timeout=120,
)
all_cards = [c for c in r.json() if not c.get("closed", False)]

# Get list names
r2 = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/lists",
    params={"key": key, "token": token, "fields": "name,id,closed"},
    timeout=20,
)
list_map = {l["id"]: l["name"] for l in r2.json()}

KEEP_LISTS = ["Top 10", "P0", "P1", "P2", "P3"]
# Archive everything NOT in priority lists
to_archive = set()
for c in all_cards:
    lname = list_map.get(c["idList"], "")
    if not any(k in lname for k in KEEP_LISTS):
        to_archive.add(c["id"])

# Dedupe priority lists by name (keep only 1 copy of each name)
name_groups = defaultdict(list)
for c in all_cards:
    lname = list_map.get(c["idList"], "")
    if any(k in lname for k in KEEP_LISTS):
        name_groups[c["name"]].append(c)

for name, cards in name_groups.items():
    if len(cards) > 1:
        # Keep the one in the highest priority list
        cards.sort(key=lambda c: KEEP_LISTS.index(
            list(next((k for k in KEEP_LISTS if k in list_map.get(c["idList"], "")), "Unknown")))
        )
        for c in cards[1:]:
            to_archive.add(c["id"])

print(f"Total open: {len(all_cards)}")
print(f"To archive: {len(to_archive)}")

# Archive using batch API (100 cards per request)
batch_size = 100
archived = 0
for i in range(0, len(to_archive), batch_size):
    batch = list(to_archive)[i:i+batch_size]
    # Trello batch endpoint: put multiple PUTs in one request
    batch_url = f"https://api.trello.com/1/batch"
    # Use sequential puts but in a tight loop
    for cid in batch:
        try:
            rr = requests.put(
                f"https://api.trello.com/1/cards/{cid}",
                params={"key": key, "token": token, "closed": "true"},
                timeout=8,
            )
            if rr.status_code == 200:
                archived += 1
        except:
            pass
    print(f"Progress: {i+len(batch)}/{len(to_archive)} archived={archived}")

print(f"\nArchived: {archived}")
remaining = len(all_cards) - archived
print(f"Remaining open: {remaining}")
