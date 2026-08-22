#!/usr/bin/env python3
"""Fetch full card details (desc, checklists, labels) for actionable cards."""
import json, sys, os, re
from pathlib import Path
import requests
import csv, io

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

# Fetch lists
lists_resp = requests.get(f"https://api.trello.com/1/boards/{BOARD_ID}/lists", 
    params={"key": key, "token": token}, timeout=30)
lists_map = {l["id"]: l["name"] for l in lists_resp.json()}

# Fetch labels
labels_resp = requests.get(f"https://api.trello.com/1/boards/{BOARD_ID}/labels",
    params={"key": key, "token": token}, timeout=30)
labels_map = {l["id"]: l["name"] for l in labels_resp.json()}

# Fetch all open cards with full fields
cards_resp = requests.get(f"https://api.trello.com/1/boards/{BOARD_ID}/cards/open",
    params={"key": key, "token": token, "fields": "id,name,desc,idList,dateLastActivity,due,dueComplete,idLabels"},
    timeout=30)
cards = cards_resp.json()

# Actionable lists
actionable_lists = {
    "Top 10 — Focus Fleet",
    "P0 - Alert / Critical / Do Now",
    "P1 - High / Doing Now",
    "P2 - Med High / This Week",
    "P3 - Medium / Follow Up",
}

# Sir Green / Sir Azure queues - skip per OODA rules
crew_queues = {"Sir Azure's Queue", "Sir Green's Queue"}

actionable = []
for c in cards:
    list_name = lists_map.get(c.get("idList"), "UNKNOWN")
    label_names = [labels_map.get(lid, "") for lid in c.get("idLabels", [])]
    
    # Skip crew queue cards
    if list_name in crew_queues:
        continue
    # Skip Sir Green/Sir Azure labeled cards
    if any(l in ("sir-green", "sir-azure", "Sir Green's Queue", "Sir Azure's Queue") for l in label_names):
        continue
    # Skip cards already marked automation-completed
    if "automation-completed" in label_names:
        continue
    
    if list_name in actionable_lists:
        actionable.append(c)

# Sort by priority: Top 10 > P0 > P1 > P2 > P3
priority_order = {
    "Top 10 — Focus Fleet": 0,
    "P0 - Alert / Critical / Do Now": 1,
    "P1 - High / Doing Now": 2,
    "P2 - Med High / This Week": 3,
    "P3 - Medium / Follow Up": 4,
}
actionable.sort(key=lambda c: (
    priority_order.get(lists_map.get(c.get("idList"), "UNKNOWN"), 9),
    lists_map.get(c.get("idList"), "UNKNOWN")
))

print(f"=== {len(actionable)} ACTIONABLE CARDS (excluding crew queues) ===\n")

# Show top 30 actionable cards with description
for i, c in enumerate(actionable[:30]):
    list_name = lists_map.get(c.get("idList"), "UNKNOWN")
    label_names = [labels_map.get(lid, "") for lid in c.get("idLabels", [])]
    
    # Fetch checklists for each card
    checklists_resp = requests.get(
        f"https://api.trello.com/1/cards/{c['id']}/checklists",
        params={"key": key, "token": token}, timeout=10
    )
    checklists = checklists_resp.json() if checklists_resp.status_code == 200 else []
    
    print(f"--- CARD {i+1}: [{list_name[:25]}] {c['name'][:80]} ---")
    print(f"  ID: {c['id']}")
    print(f"  URL: https://trello.com/c/{c['id']}")
    print(f"  Labels: {', '.join(label_names) if label_names else '(none)'}")
    desc = c.get("desc", "")[:500] if c.get("desc") else "(empty)"
    print(f"  Desc: {desc}")
    if checklists:
        for cl in checklists[:2]:
            items = cl.get("checkItems", [])
            checked = [i for i in items if i.get("state") == "complete"]
            print(f"  Checklist '{cl.get('name','')[:40]}': {len(checked)}/{len(items)} done")
    print()
