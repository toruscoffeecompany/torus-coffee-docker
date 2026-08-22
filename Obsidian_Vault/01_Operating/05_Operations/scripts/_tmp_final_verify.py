#!/usr/bin/env python3
"""Final live verification after full Trello automation pass."""
from pathlib import Path
import requests
from collections import Counter

creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
key = lines[0].strip("`")
token = lines[2].strip("`")
board_id = "6a70a3157d0db4214ac3f9a3"

lists = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=10,
).json()
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels,due,desc", "limit": 1000, "filter": "all"},
    timeout=30,
).json()

list_counts = Counter()
label_counts = Counter()
missing_due = 0
missing_desc = 0
for c in cards:
    list_counts[c.get('idList')] += 1
    for l in c.get('labels', []):
        label_counts[l['name']] += 1
    if not c.get('due'):
        missing_due += 1
    desc = c.get('desc', '') or ''
    if 'Auto-indexed:' not in desc:
        missing_desc += 1

print('=== FINAL VERIFICATION ===')
print(f"Total cards: {len(cards)}")
for l in lists:
    print(f"  {l['name']}: {list_counts.get(l['id'],0)}")
print(f"\nLabel counts:")
for k in ['P0','Top 10','P1','P2','P3','P4','P5','P6','Future Ideas',"Sir Azure's Queue","Sir Green's Queue"]:
    print(f"  {k}: {label_counts.get(k,0)}")
print(f"\nMissing due dates: {missing_due}")
print(f"Missing auto-descriptions: {missing_desc}")

if label_counts.get('Top 10', 0) == 10 and missing_desc == 0:
    print("\n✓ PASS: Top 10 exact and all cards have auto-descriptions")
else:
    print(f"\n✗ NEEDS WORK: Top 10={label_counts.get('Top 10',0)}, missing_desc={missing_desc}")
