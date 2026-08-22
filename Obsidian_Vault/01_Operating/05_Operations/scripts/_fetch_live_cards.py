#!/usr/bin/env python3
"""Fetch all open cards from Torus_Ops board using credential_loader."""
import json, sys, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials
import requests

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

# Fetch all open cards
url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards/open"
params = {
    "key": key, "token": token,
    "fields": "id,name,desc,idList,dateLastActivity,due,dueComplete,dueComplete",
    "limit": 1000,
}
resp = requests.get(url, params=params, timeout=30)
print(f"STATUS: {resp.status_code}")
if resp.status_code != 200:
    print(f"ERR: {resp.text[:500]}")
    sys.exit(1)

cards = resp.json()
print(f"TOTAL_OPEN_CARDS: {len(cards)}")

# Fetch list names
lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
lists_resp = requests.get(lists_url, params={"key": key, "token": token}, timeout=30)
list_names = {}
if lists_resp.status_code == 200:
    for l in lists_resp.json():
        list_names[l["id"]] = l["name"]

# Fetch labels
labels_url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
labels_resp = requests.get(labels_url, params={"key": key, "token": token}, timeout=30)
label_map = {}
if labels_resp.status_code == 200:
    for lb in labels_resp.json():
        label_map[lb["id"]] = lb["name"]

# Enrich cards with list names and label names
for c in cards:
    c["listName"] = list_names.get(c.get("idList"), "UNKNOWN")
    c["labelNames"] = [label_map.get(lid, lid) for lid in c.get("idLabels", [])]

# Save full dump
out = Path(__file__).parent / "_trello_live_dump.json"
out.write_text(json.dumps(cards, indent=2), encoding="utf-8")
print(f"SAVED: {out}")

# Print summary: cards grouped by list
from collections import Counter
list_counts = Counter(c["listName"] for c in cards)
print("\n--- CARDS BY LIST ---")
for list_name, count in sorted(list_counts.items()):
    print(f"  {list_name}: {count}")

# Print actionable cards (Top 10, P0, P1, P2, P3 lists)
actionable_lists = {
    "Top 10 — Focus Fleet",
    "P0 - Alert / Critical / Do Now",
    "P1 - High / Doing Now",
    "P2 - Med High / This Week",
    "P3 - Medium / Follow Up",
}
print("\n--- ACTIONABLE TICKETS (Top 10/P0/P1/P2/P3) ---")
actionable = [c for c in cards if c["listName"] in actionable_lists]
for c in sorted(actionable, key=lambda x: (list(c["listName"]), x.get("dateLastActivity","") )):
    print(f"  [{c['listName'][:20]:>20}] {c['name'][:70]}")

print(f"\nACTIONABLE_COUNT: {len(actionable)}")
