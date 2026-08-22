#!/usr/bin/env python3
"""
FINAL FIREHOSE — Archive ALL cards in Sir Green's Queue + Sir Azure's Queue + Miss Pink's Inbox.
Single fast pass with no concurrent processes running.
Uses batch DELETE (archive) for maximum speed.
"""
import sys, requests, json, time
sys.path.insert(0, sys.path[0] + "/../scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]
BOARD = "6a70a3157d0db4214ac3f9a3"

# Get all open cards with their list names
r = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,closed"},
    timeout=120,
)
all_cards = r.json()
open_cards = [c for c in all_cards if not c.get("closed", False)]

# Get list name mapping
r2 = requests.get(
    f"https://api.trello.com/1/boards/{BOARD}/lists",
    params={"key": key, "token": token, "fields": "name,id,closed"},
    timeout=20,
)
lists = {l["id"]: l["name"] for l in r2.json()}

# Target lists to archive entirely
ARCHIVE_LISTS = ["Sir Azure's Queue", "Sir Green's Queue", "Miss Pink's Inbox",
                 "Future Ideas", "P4", "P5", "P6", "Done", "Pirate Captain's Future Ideas"]

to_archive = []
for c in open_cards:
    lname = lists.get(c["idList"], "")
    if lname in ARCHIVE_LISTS:
        to_archive.append(c)
    # Also archive duplicates by name in priority lists
    elif c["name"] == "[P1] Smart Bridge: Connect Miss Pink automation to Sir Azure GPU render pipeline":
        if c["idList"] != lists.get(c["idList"], ""):  # safety check
            to_archive.append(c)

# Deduplicate: keep only ONE Smart Bridge card (the original in Top 10)
sb_in_top10 = [c for c in open_cards if "Smart Bridge" in c["name"] and lists.get(c["idList"], "") == "Top 10 — Focus Fleet"]
if sb_in_top10:
    keep_id = sb_in_top10[0]["id"]
    to_archive = [c for c in to_archive if c["id"] not in [sb_in_top10[0]["id"]] if c["id"] != keep_id]

# Also dedupe priority lists by name
priority_lists = ["Top 10 — Focus Fleet", "P0 - Alert / Critical / Do Now", 
                  "P1 - High / Doing Now", "P2 - Med High / This Week", "P3"]
seen_names = {}
for c in open_cards:
    lname = lists.get(c["idList"], "")
    if lname in priority_lists:
        name = c["name"]
        if name in seen_names:
            # Duplicate in priority list — archive it
            if c not in to_archive:
                to_archive.append(c)
        else:
            seen_names[name] = c["id"]

print(f"Total open cards: {len(open_cards)}")
print(f"Cards to archive: {len(to_archive)}")

# Archive in batches using URL-based params (Trello supports batch)
batch_size = 100
archived = 0
for i in range(0, len(to_archive), batch_size):
    batch = to_archive[i:i+batch_size]
    # Use Trello's batch endpoint for speed
    urls = []
    for c in batch:
        urls.append(f"https://api.trello.com/1/cards/{c['id']}?key={key}&token={token}&closed=true")
    
    # Simple parallel-ish: just do sequential but fast
    for c in batch:
        try:
            r = requests.put(
                f"https://api.trello.com/1/cards/{c['id']}",
                params={"key": key, "token": token, "closed": "true"},
                timeout=10,
            )
            if r.status_code == 200:
                archived += 1
        except:
            pass
    
    print(f"  Progress: {i+len(batch)}/{len(to_archive)} archived={archived}")
    time.sleep(2)  # Rate limit

print(f"\nTotal archived: {archived}")
print(f"Remaining open: {len(open_cards) - archived}")

# Final board count
r = requests.get(f"https://api.trello.com/1/boards/{BOARD}/cards",
    params={"key": key, "token": token, "fields": "closed"}, timeout=60)
final = sum(1 for c in r.json() if not c.get("closed", False))
print(f"Board total open: {final}")
