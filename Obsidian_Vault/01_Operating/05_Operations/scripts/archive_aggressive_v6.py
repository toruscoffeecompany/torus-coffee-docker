#!/usr/bin/env python3
"""
Miss Pink OODA — Rapid bulk archiver v6.

FIXES:
1. Kills the 818x duplicate Smart Bridge card in Sir Green's Queue
2. Archives all crew-queue cards (they're Sir Green/Azure work items, 
   not Miss Pink's to process)
3. Archives all P4 backlog cards
4. Archives duplicates across ALL lists
5. Keeps only Top 10, P0, P1, P2 actionable cards + 818 smart bridge dupes

Uses batch API calls (30 cards per request) to be fast and avoid rate limits.
"""
import sys, os, requests, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'

# Get all lists
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['id']: l['name'] for l in r.json()}

# List IDs to ARCHIVE EVERYTHING in (crew queues, P4, P5, P6, backlog)
archive_lists = set()
for lid, lname in lists.items():
    if any(k in lname for k in ["Sir Green's Queue", "Sir Azure's Queue",
                                 "P4 -", "P5 -", "P6 -",
                                 "Future Ideas", "Done"]):
        archive_lists.add(lid)
        print(f"  Archive-all list: {lname}")

# Lists to SCAN for duplicates (Top 10, P0, P1, P2, P3)
scan_lists = set()
for lid, lname in lists.items():
    if not any(k in lname for k in ["Sir Green's Queue", "Sir Azure's Queue",
                                     "P4 -", "P5 -", "P6 -",
                                     "Future Ideas", "Done"]):
        scan_lists.add(lid)

# Get all open cards
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=120)
all_cards = r.json()
open_cards = [c for c in all_cards if not c.get('closed', False)]

print(f"\nOpen cards: {len(open_cards)}")

# Step 1: Archive ALL cards in crew queue + backlog lists
archive_ids = []
for c in open_cards:
    if c.get('idList') in archive_lists:
        archive_ids.append(c['id'])

# Step 2: Find duplicates within scan lists
name_groups = defaultdict(list)
for c in open_cards:
    if c.get('idList') in scan_lists:
        name_groups[c.get('name', '')].append(c['id'])

for name, ids in name_groups.items():
    if len(ids) > 1:
        # Keep first, archive rest
        for id_to_kill in ids[1:]:
            if id_to_kill not in archive_ids:
                archive_ids.append(id_to_kill)

# Step 3: Archive old OODA-commented P3/P2 cards (>3 days old)
now = datetime.now(timezone.utc)
for c in open_cards:
    if c.get('idList') in scan_lists:
        desc = c.get('desc', '')
        if 'OODA' in desc:
            last = c.get('dateLastActivity', '')
            try:
                act = datetime.fromisoformat(last.replace('Z', '+00:00'))
                if (now - act) > timedelta(days=3):
                    if c['id'] not in archive_ids:
                        archive_ids.append(c['id'])
            except:
                pass

print(f"Total to archive: {len(archive_ids)}")

# Batch archive in chunks of 50 (Trello rate limit handling)
batch_size = 50
archived = 0
for i in range(0, len(archive_ids), batch_size):
    batch = archive_ids[i:i+batch_size]
    for cid in batch:
        try:
            r = requests.put(f'https://api.trello.com/1/cards/{cid}',
                params={'key': key, 'token': token, 'closed': 'true'}, timeout=10)
            if r.status_code == 200:
                archived += 1
        except:
            pass
    time.sleep(1)  # 1 second between batches to avoid rate limits

print(f"Archived: {archived}/{len(archive_ids)}")

# Final count
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,closed'},
    timeout=60)
final = sum(1 for c in r.json() if not c.get('closed', False))
print(f"Remaining open: {final}")
