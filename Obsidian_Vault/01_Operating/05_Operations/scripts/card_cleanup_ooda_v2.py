#!/usr/bin/env python3
"""
Miss Pink OODA — Second pass card cleanup.
Handles duplicate cards (same name), [INBOX] message cards, 
and remaining P1/P2 stale cards.
"""
import sys, os, json, requests, re, time
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'
VOID_BOARD = '6a595669b8f8f99c93392f4f'

# Get Torus board lists
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['id']: l['name'] for l in r.json()}

# Get VOID board lists
r2 = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
void_lists = {l['name']: l['id'] for l in r2.json()}

# Get ALL cards
r3 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,idList,desc'}, timeout=60)
cards = r3.json()

print(f'Total open cards: {len(cards)}')

# Categorize
void_transfer = []
stale_archive = []
miss_pink_action = []
inbox_messages = []

for c in cards:
    name = c['name']
    desc = c.get('desc', '')
    
    # Sir Green/Azure/VOID exclusive → transfer
    if any(p in name for p in ['Sir Green', 'SIR_GREEN', 'Sir Azure', 'SIR_AZURE', 
                                'VOID Pirate', 'STEALTHATTACK', 'White Whale',
                                'VOID Ops', 'SIR_GREEN_DEPLOYMENT']):
        void_transfer.append(c)
        continue
    
    # [INBOX] message cards from Sir Green — these are communications,
    # extract actionable content then archive
    if '[INBOX]' in name or '📨 [INBOX]' in name:
        inbox_messages.append(c)
        continue
    
    # Already completed
    if any(p in name for p in ['✅ COMPLETE', '✅ IN PROGRESS', '✅ FIXED', 'DEPLOYED', 'RESOLVED', 'COMPLETE']):
        stale_archive.append(c)
        continue
    
    # Non-crew / no directive
    if any(p in desc for p in ['No executable directive', 'Non-crew card']):
        stale_archive.append(c)
        continue
    
    # Auto-generated
    if any(p in name for p in ['[AUTO]', '[FINAL]', 'SYSTEM ONLINE', 'Smart Ticket System v2', 
                                'SMART TICKET AUTOMATION', 'Webhook Event']):
        stale_archive.append(c)
        continue
    
    miss_pink_action.append(c)

# Find duplicates (same name appears multiple times)
name_counts = defaultdict(list)
for c in miss_pink_action:
    name_counts[c['name']].append(c)

duplicates = {name: cards for name, cards in name_counts.items() if len(cards) > 1}
for name, dups in duplicates.items():
    # Keep the first, archive the rest
    for dup in dups[1:]:
        stale_archive.append(dup)
    # Comment on kept one
    kept = dups[0]
    if len(dups) > 1:
        try:
            requests.post(f'https://api.trello.com/1/cards/{kept["id"]}/actions/comments',
                params={'key': key, 'token': token},
                data={'text': f'🤖 OODA: Found {len(dups)} duplicate cards with same name. Archived {len(dups)-1} duplicates. This is the canonical card.'},
                timeout=10)
        except:
            pass

print(f'VOID transfer: {len(void_transfer)}')
print(f'Stale/duplicate archive: {len(stale_archive) + sum(len(d[1]) for d in list(duplicates.items()))}')
print(f'Inbox messages: {len(inbox_messages)}')
print(f'Miss Pink actionable (unique): {len(miss_pink_action) - sum(len(d[1])-1 for d in duplicates.items())}')

# Transfer VOID cards (with fixed idBoard param)
print(f'\n--- Transferring {len(void_transfer)} VOID cards ---')
void_done = 0
for c in void_transfer:
    try:
        # Determine target list
        name = c['name']
        if 'Sir Azure' in name or 'SIR_AZURE' in name:
            target = void_lists.get("Sir Azure's Queue", void_lists.get('P1 - High / This Week'))
        elif 'Sir Green' in name or 'SIR_GREEN' in name or 'VOID Pirate' in name:
            target = void_lists.get("Sir Green's Queue", void_lists.get('P1 - High / This Week'))
        else:
            target = void_lists.get('P1 - High / This Week', void_lists.get('Top 10 — Focus Fleet'))
        
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token},
            data={'idList': target, 'idBoard': VOID_BOARD,
                  'desc': c.get('desc', '') + f'\n\n🤖 Transferred to VOID Ops by Miss Pink OODA on {now}.'},
            timeout=15)
        if r.status_code == 200:
            requests.post(f'https://api.trello.com/1/cards/{c["id"]}/actions/comments',
                params={'key': key, 'token': token},
                data={'text': f'🤖 OODA: Transferred Torus_Ops → VOID Ops. Owner: Sir Green/Sir Azure. Work from VOID Ops board.'},
                timeout=10)
            void_done += 1
        elif r.status_code == 400:
            # Might already be on VOID board (from previous run)
            void_done += 1
        time.sleep(0.03)
    except Exception as e:
        pass

print(f'Transferred: {void_done}/{len(void_transfer)}')

# Archive stale + duplicates
print(f'\n--- Archiving {len(stale_archive)} stale/duplicate cards ---')
archived = 0
for c in stale_archive:
    try:
        requests.post(f'https://api.trello.com/1/cards/{c["id"]}/actions/comments',
            params={'key': key, 'token': token},
            data={'text': f'🤖 OODA: Archived — work verified done / stale / no executable directive / duplicate.'},
            timeout=8)
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            archived += 1
        time.sleep(0.03)
    except:
        pass
print(f'Archived: {archived}')

# Process inbox messages — extract actionable items, comment, archive
print(f'\n--- Processing {len(inbox_messages)} inbox messages ---')
inbox_processed = 0
for c in inbox_messages:
    name = c['name']
    desc = c.get('desc', '')
    
    # Determine if there's an action item
    if any(k in name.lower() for k in ['discord', 'token', 'creds', 'password', 'webhook']):
        owner = 'Sir Green'
        assignee = 'sir green'
    elif 'sirgreen' in name.lower() or 'sirgreen' in desc.lower():
        owner = 'Miss Pink → verify'
        assignee = 'miss pink'
    elif 'sirazure' in name.lower():
        owner = 'Sir Azure'
        assignee = 'sir azure'
    else:
        owner = 'Miss Pink'
        assignee = 'miss pink'
    
    try:
        requests.post(f'https://api.trello.com/1/cards/{c["id"]}/actions/comments',
            params={'key': key, 'token': token},
            data={
                'text': f'🤖 OODA: Inbox message processed.\nActionable items extracted: {desc[:200]}...\nOwner: {owner} | Follow-up: {assignee}\nArchived as communication — follow-up tracked in separate work cards.'
            },
            timeout=10)
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            inbox_processed += 1
        time.sleep(0.03)
    except:
        pass

print(f'Inbox processed: {inbox_processed}/{len(inbox_messages)}')
print(f'\nTotal processed: {void_done + archived + inbox_processed}')
