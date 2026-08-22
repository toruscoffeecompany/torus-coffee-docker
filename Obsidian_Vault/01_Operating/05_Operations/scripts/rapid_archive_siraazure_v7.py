#!/usr/bin/env python3
"""Miss Pink OODA — Rapid archiver for Sir Azure's Queue (946 duplicate cards)."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'
VOID_BOARD = '6a595669b8f8f99c93392f4f'

# Get lists from both boards
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
torus_lists = {l['name']: l for l in r.json()}

r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
void_lists = {l['name']: l for l in r.json()}

void_sir_azure = void_lists.get("Sir Azure's Queue", {}).get('id')

# Archive Sir Azure's Queue cards on TORUS board
sa_id = torus_lists.get("Sir Azure's Queue", {}).get('id')
if not sa_id:
    print("No Sir Azure's Queue found on Torus board")
    sys.exit(0)

r2 = requests.get(f'https://api.trello.com/1/lists/{sa_id}/cards',
    params={'key': key, 'token': token, 'fields': 'id,name'}, timeout=60)
cards = r2.json()
print(f"Sir Azure's Queue (Torus): {len(cards)} cards to archive")

archived = 0
for i, c in enumerate(cards):
    try:
        rr = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=10)
        if rr.status_code == 200:
            archived += 1
    except:
        pass
    if (i + 1) % 50 == 0:
        print(f"  Progress: {i+1}/{len(cards)} archived={archived}")
        time.sleep(2)  # Brief pause every 50

print(f"Archived: {archived}/{len(cards)}")

# Also check VOID board
sa_void = void_lists.get("Sir Azure's Queue", {}).get('id')
if sa_void:
    r3 = requests.get(f'https://api.trello.com/1/lists/{sa_void}/cards',
        params={'key': key, 'token': token, 'fields': 'id,name'}, timeout=60)
    void_cards = r3.json()
    print(f"Sir Azure's Queue (VOID): {len(void_cards)} cards")
    
    void_archived = 0
    for i, c in enumerate(void_cards):
        try:
            rr = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
                params={'key': key, 'token': token, 'closed': 'true'}, timeout=10)
            if rr.status_code == 200:
                void_archived += 1
        except:
            pass
        if (i + 1) % 50 == 0:
            print(f"  VOID Progress: {i+1}/{len(void_cards)} archived={void_archived}")
            time.sleep(2)
    
    print(f"VOID Archived: {void_archived}/{len(void_cards)}")

# Final count
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'closed'}, timeout=60)
total_open = sum(1 for c in r.json() if not c.get('closed', False))
print(f"\nTorus Ops remaining open: {total_open}")
