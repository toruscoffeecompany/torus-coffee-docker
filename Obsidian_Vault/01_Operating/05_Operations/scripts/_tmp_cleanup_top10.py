#!/usr/bin/env python3
"""One-time cleanup: remove Top 10 labels from cards outside canonical Top 10 list."""
from pathlib import Path
import requests
import json

creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
key = lines[0].strip("`")
token = lines[2].strip("`")
# Credentials redacted per ops policy
print('credentials loaded')
board_id = "6a70a3157d0db4214ac3f9a3"

# Load lists and labels
lists = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=10,
).json()
list_map = {l['id']: l['name'] for l in lists}
labels = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/labels",
    params={"key": key, "token": token, "fields": "id,name,color"},
    timeout=10,
).json()
label_map = {l['name']: l['id'] for l in labels}

# Canonical Top 10 list IDs
canonical_candidates = [k for k in list_map.keys() if 'Top 10' in list_map.get(k, '')]
print('canonical candidates', [list_map.get(k) for k in canonical_candidates])
canonical = None
for cid in canonical_candidates:
    name = list_map.get(cid, '')
    if 'Focus Fleet' in name or 'Top 10 — Focus Fleet' in name:
        canonical = cid
        break
if not canonical:
    canonical = canonical_candidates[0]
print('canonical', canonical, list_map.get(canonical))

top10_label_id = label_map.get('Top 10')
print('top10_label_id', top10_label_id)

# Fetch all board cards
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000, "filter": "all"},
    timeout=30,
).json()
print('total cards', len(cards))

stray = [c for c in cards if top10_label_id in [l['id'] for l in c.get('labels', [])] and c.get('idList') != canonical]
print('stray labeled cards', len(stray))
for c in stray:
    r = requests.delete(
        f"https://api.trello.com/1/cards/{c['id']}/idLabels/{top10_label_id}",
        params={"key": key, "token": token},
        timeout=10,
    )
    print(r.status_code, c['id'], c['name'][:60])

# Verify
cards2 = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000, "filter": "all"},
    timeout=30,
).json()
stray2 = [c for c in cards2 if top10_label_id in [l['id'] for l in c.get('labels', [])] and c.get('idList') != canonical]
list_count = sum(1 for c in cards2 if c.get('idList') == canonical)
label_count = sum(1 for c in cards2 if top10_label_id in [l['id'] for l in c.get('labels', [])])
print('after cleanup: stray', len(stray2), 'list', list_count, 'label', label_count)
