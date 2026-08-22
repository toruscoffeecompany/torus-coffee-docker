#!/usr/bin/env python3
"""Label cards missing P1/P2/P3 priority labels."""
import requests, json
from pathlib import Path

creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
secret = next(line for line in creds.splitlines() if line.startswith("`7a18")).strip("`")
board_id = "6a70a3157d0db4214ac3f9a3"

LABEL_IDS = {
    "P1": "6a70acc569135c796d8eba5d",
    "P2": "6a70acc56f143597877f576e",
    "P3": "6a70acc6fddcac79f411267f",
}

KEYWORDS = {
    "P1": ["blocked", "critical", "urgent", "p1", "security", "docker", "kubernetes", "deploy", "broken", "fix", "alert", "pirate", "dashboard", "status", "fleet", "tools", "hw", "rig", "trello", "prometheus", "alertmanager", "vault", "quickadd", "obsidian", "connectivity", "502", "404", "401", "regression", "timeout"],
    "P2": ["setup", "configure", "build", "create", "update", "sync", "automation", "deploy", "improve", "audit", "review", "website", "square", "discord", "sir green", "sir azure", "miss pink", "bios", "svm", "virtualization"],
    "P3": ["document", "template", "guide", "plan", "strategy", "design", "brand", "future", "q4", "q1", "campaign", "marketing"],
}

def guess_priority(name):
    lower = name.lower()
    for priority, keywords in KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return priority
    return "P2"

# Get all cards
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000},
    timeout=20,
).json()

print(f"TOTAL_CARDS: {len(cards)}")

# Find cards without P1/P2/P3
no_priority = []
for c in cards:
    label_names = [l.get("name") for l in c.get("labels", [])]
    if not any(p in label_names for p in ["P1", "P2", "P3"]):
        no_priority.append(c)

print(f"CARDS_WITHOUT_P1/P2/P3: {len(no_priority)}")

labeled = 0
for c in no_priority:
    priority = guess_priority(c["name"])
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

# Verify
cards2 = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000},
    timeout=20,
).json()

no_priority2 = [c for c in cards2 if not any(l.get("name") in ["P1","P2","P3"] for l in c.get("labels", []))]
print(f"\nREMAINING_WITHOUT_PRIORITY: {len(no_priority2)}")

Path("10_Skills_Library/05_Operations/trello_priority_label_report.json").write_text(
    json.dumps({"total": len(cards2), "labeled": labeled, "remaining_unlabeled_priority": len(no_priority2)}, indent=2),
    encoding="utf-8"
)
print("REPORT_SAVED")
