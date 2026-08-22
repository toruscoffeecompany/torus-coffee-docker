#!/usr/bin/env python3
"""Miss Pink OODA — Analyze Sir Green queue card patterns."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

r = requests.get(f'https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
lists = {l['name']: l for l in r.json()}
sg_id = lists["Sir Green's Queue"]["id"]

r2 = requests.get(f'https://api.trello.com/1/lists/{sg_id}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,desc'}, timeout=30)
cards = r2.json()

print(f'Sir Green queue: {len(cards)} cards')

# Show first 15
print('=== First 15 ===')
for c in cards[:15]:
    print(f'  {c["name"][:65]}')

# Categorize
patterns = {}
for c in cards:
    name = c['name']
    if 'sir_green' in name.lower():
        p = 'sir_green_tagged'
    elif 'toruscoffee' in name.lower() or 'Torus_Ops' in name or 'torus-coffee' in name:
        p = 'github_issue'
    elif 'miss_pink' in name.lower():
        p = 'miss_pink_tagged'
    elif 'AUTO' in name or 'SYSTEM' in name or 'Webhook' in name or 'Alert' in name:
        p = 'auto_generated'
    elif 'Bug hunt' in name or 'Verify' in name:
        p = 'verification'
    elif 'P3:' in name or 'P2:' in name or 'P1:' in name:
        p = 'priority_tagged'
    else:
        p = 'other'
    patterns[p] = patterns.get(p, 0) + 1

print('\n=== Patterns ===')
for p, count in sorted(patterns.items(), key=lambda x: -x[1]):
    print(f'  {p}: {count}')
