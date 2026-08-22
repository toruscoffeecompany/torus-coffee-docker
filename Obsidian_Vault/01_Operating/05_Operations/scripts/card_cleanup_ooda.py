#!/usr/bin/env python3
"""
Miss Pink OODA — Card cleanup automation (v2).
Transfers Sir Green/Azure exclusive cards to VOID Ops board.
Archives stale/complete/auto-report cards on Torus board.
Properly handles cross-board card moves with idBoard param.
"""
import sys, os, json, requests, re, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'
VOID_BOARD = '6a595669b8f8f99c93392f4f'

# Get VOID board lists
r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
void_lists = {l['name']: l['id'] for l in r.json()}

# Route void cards to appropriate list based on name keywords
def route_void_list(name):
    if 'Sir Azure' in name or 'SIR AZURE' in name:
        return void_lists.get('Sir Azure\'s Queue', void_lists.get('P1 - High / This Week'))
    if 'Sir Green' in name or 'SIR GREEN' in name:
        return void_lists.get('Sir Green\'s Queue', void_lists.get('P1 - High / This Week'))
    if 'VOID Pirate' in name or 'Captain' in name:
        return void_lists.get('Pirate Captain\'s Future Ideas', void_lists.get('P2 - Medium / Follow Up'))
    if any(p in name for p in ['P0', 'CRITICAL', 'Alert']):
        return void_lists.get('P0 - Critical / Do Now')
    if any(p in name for p in ['P1', '[P1]']):
        return void_lists.get('P1 - High / This Week')
    if any(p in name for p in ['P2', '[P2]']):
        return void_lists.get('P2 - Medium / Follow Up')
    # Default: Sir Green's queue (most void cards are crew mesh / security infra)
    return void_lists.get('Sir Green\'s Queue')

# Get Torus board lists
r2 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
torus_lists = {l['id']: l['name'] for l in r2.json()}

# Get all open cards
r3 = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,idList,desc'}, timeout=60)
cards = r3.json()

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

void_cards = []
stale_cards = []

for c in cards:
    name = c['name']
    desc = c.get('desc', '')
    
    # Sir Green/Azure exclusive → VOID board
    if any(p in name for p in ['Sir Green', 'SIR GREEN', 'Sir Azure', 'SIR AZURE', 
                                'VOID Pirate', 'STEALTHATTACK', 'White Whale']):
        void_cards.append(c)
        continue
    
    # Already done
    if any(p in name for p in ['✅', 'COMPLETE', 'FIXED', 'DONE']):
        stale_cards.append(c)
        continue
    
    # Auto-generated stale
    if any(p in name for p in ['[AUTO]', '[FINAL]', '[OODA_AUTO]', 'SYSTEM ONLINE', 
                                'Webhook Event', 'Smart Ticket System v2', 'SMART TICKET AUTOMATION']):
        stale_cards.append(c)
        continue
    
    # Non-crew / no executable directive
    if any(p in desc for p in ['No executable directive', 'Non-crew card', 'Non-crew']):
        stale_cards.append(c)
        continue

print(f'Total: {len(cards)} | VOID transfer: {len(void_cards)} | Stale: {len(stale_cards)}')

# Transfer VOID cards
print(f'\n--- Transferring {len(void_cards)} VOID cards ---')
transferred = 0
for c in void_cards:
    try:
        target_list = route_void_list(c['name'])
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token},
            data={'idList': target_list, 'idBoard': VOID_BOARD,
                  'desc': c.get('desc', '') + f'\n\n🤖 Transferred by Miss Pink OODA on {now} — Sir Green/Azure scope.'},
            timeout=15)
        if r.status_code == 200:
            # Add comment
            requests.post(f'https://api.trello.com/1/cards/{c["id"]}/actions/comments',
                params={'key': key, 'token': token},
                data={'text': f'🤖 OODA: Transferred from Torus_Ops → VOID Ops. Owner: Sir Green/Sir Azure. Please work from VOID Ops board.'},
                timeout=10)
            transferred += 1
            if transferred % 20 == 0:
                print(f'  Progress: {transferred}/{len(void_cards)}')
        else:
            print(f'  ❌ {c["id"][:8]}: {r.status_code}')
    except Exception as e:
        print(f'  ❌ {c["id"][:8]}: {e}')
    time.sleep(0.05)  # Rate limit

print(f'Transferred: {transferred}')

# Archive stale cards
print(f'\n--- Archiving {len(stale_cards)} stale cards ---')
archived = 0
for c in stale_cards:
    try:
        requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=10)
        archived += 1
    except Exception:
        pass
    time.sleep(0.05)

print(f'Archived: {archived}')
print(f'\nTotal processed: {transferred + archived} cards')
