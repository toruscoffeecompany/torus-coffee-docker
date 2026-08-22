#!/usr/bin/env python3
"""Deep dive reorganization of Torus_Ops Trello board.
Label unlabeled cards, move P1 blockers to To_Do, archive duplicates.
"""
import requests, json, re
from pathlib import Path
from collections import defaultdict

creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
secret = next(line for line in creds.splitlines() if line.startswith("`7a18")).strip("`")
board_id = "6a70a3157d0db4214ac3f9a3"

# List IDs
LISTS = {
    "VOID Ops": "6a73cfd8c1ba2e16d3491370",
    "Backlog": "6a70a3282e405a2460afc170",
    "To_Do": "6a70a328671131b71ae66f3a",
    "In_Progress": "6a70a32989b896ad4af9f4c6",
    "Review": "6a70a32923622d3e00107d70",
    "Done": "6a70a32a723c0312a3d5fbb4",
}

# Label IDs
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

# Priority keyword mapping
KEYWORDS = {
    "P1": ["blocked", "critical", "urgent", "p1", "security", "docker", "kubernetes", "deploy", "broken", "fix", "alert", "pirate", "dashboard", "status", "fleet", "tools", "security", "hw", "rig", "trello", "prometheus", "alertmanager", "vault", "quickadd", "obsidian", "connectivity", "502", "404", "401"],
    "P2": ["setup", "configure", "build", "create", "update", "sync", "automation", "deploy", "improve", "audit", "review", "website", "square", "discord", "sir green", "sir azure", "miss pink"],
    "P3": ["document", "template", "guide", "plan", "strategy", "design", "brand", "future", "q4", "q1", "campaign", "marketing"],
}

def guess_priority(name):
    lower = name.lower()
    for priority, keywords in KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return priority
    return "P2"

def guess_labels(name):
    labels = set()
    lower = name.lower()
    if any(k in lower for k in ["automation", "auto", "script", "cron", "ooda", "verifier"]):
        labels.add("automation")
    if any(k in lower for k in ["ops", "deploy", "docker", "k8s", "kubernetes", "fleet"]):
        labels.add("ops")
    if any(k in lower for k in ["crew", "sir green", "sir azure", "miss pink", "pirate"]):
        labels.add("crew")
    if any(k in lower for k in ["media", "image", "video", "audio", "art", "design"]):
        labels.add("media")
    if any(k in lower for k in ["inbox", "message", "send", "notify", "alert"]):
        labels.add("inbox")
    return labels

# Get all cards
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000},
    timeout=20,
).json()

print(f"TOTAL_CARDS: {len(cards)}")

# Label unlabeled cards
unlabeled = [c for c in cards if not c.get("labels") and c.get("idList") != LISTS["Done"]]
print(f"UNLABELED_CARDS: {len(unlabeled)}")

labeled = 0
for c in unlabeled:
    priority = guess_priority(c["name"])
    extra_labels = guess_labels(c["name"])
    
    # Add priority label
    label_ids = [LABEL_IDS[priority]]
    for lab in extra_labels:
        if lab in LABEL_IDS:
            label_ids.append(LABEL_IDS[lab])
    
    # Apply priority label
    r = requests.post(
        f"https://api.trello.com/1/cards/{c['id']}/idLabels",
        params={"key": key, "token": token},
        data={"value": LABEL_IDS[priority]},
        timeout=15,
    )
    if r.status_code == 200:
        labeled += 1
        if labeled <= 20:
            print(f"  LABELED {priority}: {c['name'][:60]}")

print(f"LABELED: {labeled}")

# Move high-priority P1 cards from Backlog to To_Do
backlog_p1 = [c for c in cards if c.get("idList") == LISTS["Backlog"] and any(l.get("name") == "P1" for l in c.get("labels", []))]
print(f"\nBACKLOG_P1_CARDS: {len(backlog_p1)}")

moved = 0
for c in backlog_p1[:20]:  # Move top 20 P1 cards
    r = requests.put(
        f"https://api.trello.com/1/cards/{c['id']}",
        params={"key": key, "token": token},
        data={"idList": LISTS["To_Do"]},
        timeout=15,
    )
    if r.status_code == 200:
        moved += 1
        if moved <= 10:
            print(f"  MOVED P1: {c['name'][:60]}")

print(f"MOVED_TO_TODO: {moved}")

# Archive obvious duplicates/obsolete cards in Done
done_cards = [c for c in cards if c.get("idList") == LISTS["Done"]]
print(f"\nDONE_CARDS: {len(done_cards)}")

# Check for duplicate names in Done
done_names = defaultdict(list)
for c in done_cards:
    done_names[c["name"].strip().lower()].append(c)

dupes_done = {k: v for k, v in done_names.items() if len(v) > 1}
print(f"DUPLICATES_IN_DONE: {len(dupes_done)}")

archived = 0
for name, dupes in dupes_done.items():
    for c in dupes[1:]:
        r = requests.put(
            f"https://api.trello.com/1/cards/{c['id']}",
            params={"key": key, "token": token},
            data={"closed": "true"},
            timeout=15,
        )
        if r.status_code == 200:
            archived += 1
            print(f"  ARCHIVED DUP: {c['name'][:60]}")

print(f"ARCHIVED_DUPES: {archived}")

# Save reorganization report
report = {
    "timestamp": "2026-08-06T15:45:00.000000+00:00",
    "total_cards": len(cards),
    "labeled": labeled,
    "moved_to_todo": moved,
    "archived_dupes": archived,
}
Path("10_Skills_Library/05_Operations/trello_reorganization_report.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print("\nREORGANIZATION_SAVED")
