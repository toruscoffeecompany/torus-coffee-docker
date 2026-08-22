#!/usr/bin/env python3
"""
Miss Pink OODA — Aggressive card archiver v3.

Archives ALL done/verified/stale/duplicate/inbox/crew-scoped cards 
that I've already processed. Also archives cards older than 7 days 
with no recent activity that have been commented on by OODA.

This is the "slim down the board" pass — we want the board as small
as possible so new cards are easier to read.
"""
import sys, os, requests, time, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'

# Get all lists
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['id']: l['name'] for l in r.json()}

# Get ALL cards with last activity
r2 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=60)
cards = r2.json()

print(f'Total cards (including archived): {len(cards)}')
open_cards = [c for c in cards if not c.get('closed', False)]
print(f'Open cards: {len(open_cards)}')

# Find duplicates (same name)
name_counts = defaultdict(list)
for c in open_cards:
    name_counts[c['name']].append(c)

dup_ids = set()
for name, dups in name_counts.items():
    if len(dups) > 1:
        for dup in dups[1:]:
            dup_ids.add(dup['id'])

# Categorize for archival
archive_now = []  # Archive immediately
archive_age = []  # Archive if old enough
keep = []

now = datetime.now(timezone.utc)

for c in open_cards:
    name = c['name']
    desc = c.get('desc', '')
    last_activity = c.get('dateLastActivity', '')
    
    # Already commented by OODA → archive
    if 'OODA' in desc or 'OODA' in name:
        # Check if old enough (7 days) OR if card was commented and is now stale
        try:
            act = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            age = (now - act).total_seconds() / 86400  # days
        except:
            age = 0
        
        # If OODA commented AND (card is old OR card is clearly stale)
        if age > 7 or any(k in name for k in ['✅ COMPLETE', '✅ FIXED', 'DEPLOYED', 'RESOLVED']):
            archive_now.append(c)
            continue
    
    # Duplicates → archive
    if c['id'] in dup_ids:
        archive_now.append(c)
        continue
    
    # Inbox messages → archive (they're communications, not work)
    if '[INBOX]' in name or '📨' in name:
        archive_now.append(c)
        continue
    
    # Auto-generated cards → archive
    if any(p in name for p in ['[AUTO]', 'SYSTEM ONLINE', 'Webhook Event', 'SMART_TICKET',
                                'Auto-alert when new', 'Auto-generated']):
        archive_now.append(c)
        continue
    
    # No executable directive → archive
    if any(p in desc for p in ['No executable directive', 'Non-crew card']):
        archive_now.append(c)
        continue
    
    # Completed/stale status → archive
    if any(p in name for p in ['COMPLETE', '✅ FIXED', 'DEPLOYED', 'RESOLVED', 'COMPLETE']):
        archive_now.append(c)
        continue
    
    # Cards with OODA_ prefix that are old → archive
    if 'OODA' in name and age > 3:
        archive_age.append(c)
        continue
    
    keep.append(c)

print(f'Archive now: {len(archive_now)}')
print(f'Archive by age: {len(archive_age)}')
print(f'Keep: {len(keep)}')

# Archive all
total_archive = len(archive_now) + len(archive_age)
archived = 0

for batch_name, batch in [('NOW', archive_now), ('AGE', archive_age)]:
    for c in batch:
        try:
            r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
                params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
            if r.status_code == 200:
                archived += 1
            time.sleep(0.02)  # 20ms delay, ~50 cards/sec
        except:
            pass

print(f'\nArchived: {archived}/{total_archive}')
print(f'Remaining open: {len(open_cards) - archived}')
