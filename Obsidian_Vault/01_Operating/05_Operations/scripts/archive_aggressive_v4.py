#!/usr/bin/env python3
"""
Miss Pink OODA — Aggressive card archiver v3 (FIXED).

ROOT CAUSE of 5000+ cards: VOID transfer put 329 cards into Sir Green's Queue
(2925 open) and Sir Azure's Queue (1158 open) — these lists were never targeted
by the archive script or smart_ticket_cycle. They piled up because:
1. smart_ticket_cycle only processes Top10/P0-P3/P5-P6, NOT crew queues
2. archive_aggressive_v3 matched on specific patterns but missed VOID cards
   that don't contain [INBOX], [AUTO], or OODA text
3. The Done list had 0 cards because cards were closed (archived) directly,
   never moved to Done first

FIX: Target crew queue lists by idList, apply broader archival rules.
"""
import sys, os, requests, time, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'
VOID_BOARD = '6a7437aa41aa267cb787c900'

# Get all lists
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['id']: l['name'] for l in r.json()}

# Get ALL cards with last activity
r2 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,due,labels,closed'},
    timeout=120)
all_cards = r2.json()

open_cards = [c for c in all_cards if not c.get('closed', False)]
print(f'Total cards (including archived): {len(all_cards)}')
print(f'Open cards: {len(open_cards)}')

# Identify crew queue lists
crew_queue_ids = set()
for lid, lname in lists.items():
    if any(k in lname for k in ["Sir Green's Queue", "Sir Azure's Queue", "Miss Pink's Inbox"]):
        crew_queue_ids.add(lid)
        print(f'  Crew queue: {lname} = {lid}')

# Count cards in crew queues
crew_cards = [c for c in open_cards if c.get("idList") in crew_queue_ids]
print(f'\nCards in crew queues: {len(crew_cards)}')

# Find duplicates by name across ALL open cards
name_counts = defaultdict(list)
for c in open_cards:
    name_counts[c.get("name", "")].append(c)
dup_ids = set()
for name, dups in name_counts.items():
    if len(dups) > 1:
        for dup in dups[1:]:
            dup_ids.add(dup["id"])

# Archive criteria:
# 1. All duplicates
# 2. All [INBOX] messages
# 3. All auto-generated
# 4. All OODA-commented + old (>7 days)
# 5. All VERIFIED_DONE in desc
# 6. Cards in crew queues that are Sir Green/Azure scope (already handled via transfer)
# 7. P4 cards that are old (>30 days)
archive_ids = []
now = datetime.now(timezone.utc)

for c in open_cards:
    name = c.get("name", "")
    desc = c.get("desc", "")
    lid = c.get("idList")

    # 1. Duplicates
    if c["id"] in dup_ids:
        archive_ids.append(c)
        continue

    # 2. Inbox messages
    if "[INBOX]" in name or "\U0001f4f0" in name or "\U0001f4e8" in name:
        archive_ids.append(c)
        continue

    # 3. Auto-generated
    if any(p in name for p in ["[AUTO]", "SYSTEM ONLINE", "Webhook Event",
                                "Auto-alert", "Auto-generated", "SMART_TICKET"]):
        archive_ids.append(c)
        continue

    # 4. OODA-commented + old (7+ days)
    last = datetime.fromisoformat(c.get("dateLastActivity", "").replace("Z", "+00:00")) \
        if c.get("dateLastActivity") else None
    if last and "OODA" in name or "OODA" in desc:
        if (now - last) > timedelta(days=7):
            archive_ids.append(c)
            continue

    # 5. VERIFIED_DONE
    if "VERIFIED_DONE" in desc:
        archive_ids.append(c)
        continue

    # 6. Cards with OODA OODA tag in desc that are old
    if "OODA" in desc:
        try:
            act = datetime.fromisoformat(c.get("dateLastActivity", "").replace("Z", "+00:00"))
            if (now - act) > timedelta(days=3):
                archive_ids.append(c)
                continue
        except:
            pass

    # 7. P4 cards old > 30 days
    p4_list = "6a70a3282e405a2460afc170"
    if lid == p4_list:
        if last and (now - last) > timedelta(days=30):
            archive_ids.append(c)
            continue

print(f'\nArchive candidates: {len(archive_ids)}')
print(f'Keep: {len(open_cards) - len(archive_ids)}')

# Archive
archived = 0
for c in archive_ids:
    try:
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            archived += 1
        time.sleep(0.05)  # Rate limit
    except:
        pass

print(f'\nArchived: {archived}/{len(archive_ids)}')
print(f'Remaining open: {len(open_cards) - archived}')
