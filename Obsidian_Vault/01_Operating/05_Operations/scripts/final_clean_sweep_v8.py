#!/usr/bin/env python3
"""
FINAL clean sweep — archive ALL non-priority cards in one pass.
Target: everything in Sir Green's Queue, Sir Azure's Queue, Miss Pink's Inbox,
Future Ideas, P4, P5, P6, Done lists. Also dedupes by name (keep 1 open).
"""
import sys, requests, time
sys.path.insert(0, "scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]

BOARD = "6a70a3157d0db4214ac3f9a3"

# Get all lists
r = requests.get(f"https://api.trello.com/1/boards/{BOARD}/lists",
    params={"key": key, "token": token, "fields": "name,id,closed"}, timeout=20)
lists = r.json()

# Lists to fully archive
ARCHIVE_KEYWORDS = ["Sir Azure", "Sir Green", "Miss Pink's Inbox", "Future", "P4", "P5", "P6", "Done"]
KEEP_KEYWORDS = ["Top 10", "P0", "P1", "P2", "P3"]

total_open = 0
total_archived = 0

for l in lists:
    lname = l["name"]
    
    # Skip closed lists
    if l.get("closed"):
        continue
    
    r2 = requests.get(f"https://api.trello.com/1/lists/{l['id']}/cards",
        params={"key": key, "token": token, "fields": "id,name,closed"}, timeout=30)
    cards = r2.json()
    open_cards = [c for c in cards if not c.get("closed", False)]
    
    if not open_cards:
        continue
    
    if any(k in lname for k in KEEP_KEYWORDS):
        # Keep priority lists, but dedupe by name
        seen_names = {}
        for i, c in enumerate(open_cards):
            name = c["name"]
            if name in seen_names:
                # Duplicate — archive it
                requests.put(f"https://api.trello.com/1/cards/{c['id']}",
                    params={"key": key, "token": token, "closed": "true"}, timeout=10)
                total_archived += 1
            else:
                seen_names[name] = c["id"]
        total_open += len(seen_names)
        print(f"  KEEP {lname}: {len(open_cards)} open, {len(open_cards) - len(seen_names)} duplicates archived, {len(seen_names)} remaining")
    else:
        # Archive everything in non-priority lists
        for i, c in enumerate(open_cards):
            try:
                rr = requests.put(f"https://api.trello.com/1/cards/{c['id']}",
                    params={"key": key, "token": token, "closed": "true"}, timeout=10)
                if rr.status_code == 200:
                    total_archived += 1
            except:
                pass
            if (i + 1) % 50 == 0:
                time.sleep(0.5)
        print(f"  ARCHIVE {lname}: {len(open_cards)} cards archived")
    
    time.sleep(0.3)

# Get final count
r = requests.get(f"https://api.trello.com/1/boards/{BOARD}/cards",
    params={"key": key, "token": token, "fields": "closed"}, timeout=60)
final_open = sum(1 for c in r.json() if not c.get("closed", False))

print(f"\nTotal archived: {total_archived}")
print(f"Total open (priority only): {final_open}")
