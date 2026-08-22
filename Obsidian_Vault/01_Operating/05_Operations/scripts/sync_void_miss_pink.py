#!/usr/bin/env python3
"""Sync Miss Pink's Queue from VOID Ops board to Torus Ops board."""
import sys, requests, json, time
sys.path.insert(0, "scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]
VOID = "6a595669b8f8f99c93392f4f"
TORUS = "6a70a3157d0db4214ac3f9a3"

def get_lists(board_id):
    r = requests.get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        params={"key": key, "token": token, "fields": "name,id,closed"},
        timeout=30,
    )
    return [l for l in r.json() if not l.get("closed")]

def get_cards(list_id):
    r = requests.get(
        f"https://api.trello.com/1/lists/{list_id}/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,labels,closed,dateLastActivity"},
        timeout=30,
    )
    return [c for c in r.json() if not c.get("closed", False)]

# Get Torus Ops lists
torus_lists = get_lists(TORUS)
torus_list_names = {l["id"]: l["name"] for l in torus_lists}

# Find target lists on Torus board
inbox_id = next((l["id"] for l in torus_lists if "Miss Pink's Inbox" in l["name"]), None)
p0_id = next((l["id"] for l in torus_lists if l["name"].startswith("P0")), None)
p1_id = next((l["id"] for l in torus_lists if l["name"].startswith("P1")), None)
p2_id = next((l["id"] for l in torus_lists if l["name"].startswith("P2")), None)
p3_id = next((l["id"] for l in torus_lists if l["name"].startswith("P3")), None)

# Get all VOID cards looking for Miss Pink assignments
void_lists = get_lists(VOID)
miss_pink_cards = []
for l in void_lists:
    cards = get_cards(l["id"])
    for c in cards:
        name = c.get("name", "").lower()
        desc = c.get("desc", "").lower()
        labels = [x["name"].lower() for x in c.get("labels", [])]
        # Check if card is for Miss Pink
        if "miss pink" in name or "miss pink" in desc or "miss-pink" in desc or "miss pink" in labels:
            list_name = l["name"]
            miss_pink_cards.append((l["id"], list_name, c))

print(f"Found {len(miss_pink_cards)} Miss Pink cards on VOID Ops board")
for lid, lname, c in miss_pink_cards[:10]:
    name = c["name"][:60]
    labels = [x["name"] for x in c.get("labels", [])]
    print(f"  [{lname}] {name} | labels={labels}")

# Transfer each card to Torus Ops board
transferred = 0
for src_list_id, src_list_name, c in miss_pink_cards:
    name = c["name"]
    desc = c.get("desc", "")
    labels = [x["name"] for x in c.get("labels", [])]
    
    # Classify priority
    desc_lower = desc.lower()
    if "p0" in labels or "critical" in desc_lower or "urgent" in desc_lower:
        target_list = p0_id
    elif "p1" in labels or "high" in desc_lower:
        target_list = p1_id
    elif "p2" in labels or "medium" in desc_lower:
        target_list = p2_id
    else:
        target_list = p2_id  # Default to P2
    
    # Move card to Torus Ops board
    r = requests.put(
        f"https://api.trello.com/1/cards/{c['id']}",
        params={
            "key": key,
            "token": token,
            "idBoard": TORUS,
            "idList": target_list,
        },
        timeout=15,
    )
    if r.status_code == 200:
        transferred += 1
        # Add comment noting transfer
        requests.post(
            f"https://api.trello.com/1/cards/{c['id']}/actions/comments",
            params={"key": key, "token": token, "text": f"Transferred from VOID Ops ({src_list_name}) by Miss Pink automated sync"},
            timeout=10,
        )
    else:
        print(f"  FAILED to move: {name[:50]} — {r.status_code}")
    time.sleep(0.3)

print(f"\nTransferred {transferred} cards to Torus Ops board")

# Now check Torus Ops board for Sir Green/Azure work
torus_cards = []
for l in torus_lists:
    cards = get_cards(l["id"])
    for c in cards:
        torus_cards.append((l["name"], c))

print(f"\n=== Torus Ops board: {len(torus_cards)} total open cards ===")
for lname, c in torus_cards[:5]:
    print(f"  [{lname}] {c['name'][:60]}")
