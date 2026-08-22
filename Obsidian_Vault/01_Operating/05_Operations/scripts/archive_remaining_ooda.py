#!/usr/bin/env python3
"""Miss Pink OODA — Archive remaining stale + duplicate + inbox cards."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'

r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['id']: l['name'] for l in r.json()}

# Get all open cards
r2 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,desc'}, timeout=60)
cards = r2.json()

# Collect archive candidates: duplicates, inbox messages, stale, auto-generated
from collections import defaultdict
name_counts = defaultdict(list)
for c in cards:
    name_counts[c['name']].append(c)

duplicates = {name: cards for name, cards in name_counts.items() if len(cards) > 1}
dup_ids = set()
for name, dups in duplicates.items():
    for dup in dups[1:]:
        dup_ids.add(dup['id'])

archive_ids = []
for c in cards:
    name = c['name']
    desc = c.get('desc', '')
    
    if c['id'] in dup_ids:
        archive_ids.append(c)
        continue
    
    if '[INBOX]' in name or '📨 [INBOX]' in name:
        archive_ids.append(c)
        continue
    
    if any(p in name for p in ['✅ COMPLETE', '✅ FIXED', 'DEPLOYED', 'RESOLVED', 'COMPLETE']):
        archive_ids.append(c)
        continue
    
    if any(p in desc for p in ['No executable directive', 'Non-crew card']):
        archive_ids.append(c)
        continue
    
    if any(p in name for p in ['[AUTO]', 'SYSTEM ONLINE', 'Webhook Event', 'SMART_TICKET']):
        archive_ids.append(c)
        continue

print(f'Cards to archive: {len(archive_ids)}')

archived = 0
for c in archive_ids:
    try:
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            archived += 1
        time.sleep(0.02)
    except:
        pass

print(f'Archived: {archived}')
print(f'Remaining open: {len(cards) - archived}')
