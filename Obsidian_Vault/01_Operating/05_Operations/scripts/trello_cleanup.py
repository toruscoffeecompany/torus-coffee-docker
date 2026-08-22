#!/usr/bin/env python3
"""Trello board cleanup: merge duplicates and label unlabeled cards."""
import requests
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(r"D:\Work\Torus Coffee Company LLC") / "10_Skills_Library/05_Operations/scripts"))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
api_key = creds["api_key"]
token = creds["token"]

bid = "6a70a3157d0db4214ac3f9a3"

# Priority mapping for unlabeled cards
KEYWORDS = {
    "P1": ["blocked", "critical", "urgent", "p1", "security", "docker", "kubernetes", "deploy", "broken", "fix", "alert", "pirate"],
    "P2": ["setup", "configure", "build", "create", "update", "sync", "automation", "obsidian", "trello", "github", "discord", "sir green", "sir azure", "miss pink"],
    "P3": ["review", "document", "template", "guide", "plan", "strategy", "design", "brand"],
}

LABEL_IDS = {
    "P1": "6a70acc569135c796d8eba5d",
    "P2": "6a70acc56f143597877f576e",
    "P3": "6a70acc6fddcac79f411267f",
    "inbox": "6a739cca5b6ba1e16abcd5f3",
    "automation": "6a739cca616c68bad376bcef",
    "ops": "6a739ccb921a250c77d804ea",
    "crew": "6a739cca998cea6096d11667",
    "media": "6a739ccb632522fbda15db50",
}

def guess_priority(name):
    lower = name.lower()
    for priority, keywords in KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return priority
    return "P2"

def get_cards():
    r = requests.get(
        f"https://api.trello.com/1/boards/{bid}/cards",
        params={"key": api_key, "token": token, "fields": "name,idList,labels,desc"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def archive_card(card_id):
    # Move to Done list to effectively archive
    done_list_id = "6a70a32a723c0312a3d5fbb4"
    r = requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": api_key, "token": token},
        data={"idList": done_list_id, "closed": "true"},
        timeout=15,
    )
    return r.status_code

def add_label(card_id, label_id):
    r = requests.post(
        f"https://api.trello.com/1/cards/{card_id}/idLabels",
        params={"key": api_key, "token": token},
        data={"value": label_id},
        timeout=15,
    )
    return r.status_code

cards = get_cards()

# Find duplicates
from collections import defaultdict
by_name = defaultdict(list)
for c in cards:
    by_name[c["name"]].append(c)

duplicates = {name: cards_list for name, cards_list in by_name.items() if len(cards_list) > 1}
print(f"DUPLICATES_FOUND: {len(duplicates)}")

# Archive duplicates (keep first, archive rest)
archived = 0
for name, cards_list in duplicates.items():
    for c in cards_list[1:]:
        status = archive_card(c["id"])
        if status == 200:
            archived += 1
            print(f"  ARCHIVED: {name} ({c['id']})")

print(f"ARCHIVED: {archived}")

# Label unlabeled cards
unlabeled = [c for c in cards if not c.get("labels") and c.get("idList") != "6a70a32a723c0312a3d5fbb4"]
labeled = 0
for c in unlabeled:
    priority = guess_priority(c["name"])
    status = add_label(c["id"], LABEL_IDS[priority])
    if status == 200:
        labeled += 1
        if labeled <= 10:
            print(f"  LABELED {priority}: {c['name']}")

print(f"LABELED: {labeled}")

# Save cleanup report
report = {
    "timestamp": "2026-08-06T08:40:00.000000+00:00",
    "duplicates_found": len(duplicates),
    "duplicates_archived": archived,
    "unlabeled_found": len(unlabeled),
    "unlabeled_labeled": labeled,
    "duplicate_names": list(duplicates.keys()),
}
out = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\trello_cleanup_report.json")
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"CLEANUP_SAVED {out}")
