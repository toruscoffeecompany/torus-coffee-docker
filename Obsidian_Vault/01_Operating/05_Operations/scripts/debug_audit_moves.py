#!/usr/bin/env python3
"""Debug: Find cards that would be moved by the audit."""
import requests, json, time, re
from pathlib import Path
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
text = (VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = text.splitlines()
token = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        token = lines[i + 1].strip().strip("`")
        break

AUTH = {"key": KEY, "token": token}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"

LIST_IDS = {
    'Top 10': '6a74cbd3aa052ed2b30c5644',
    'P0': '6a74cbd440270147ff04bd5b',
    'P1': '6a74cbd5e3d54d2d08be82e7',
    'P2': '6a74cbd4148f814483a64589',
    'P3': '6a70a32923622d3e001e07d70',
    "Sir Azure's Queue": '6a74cbd51b2662f6cdc37cce',
    "Sir Green's Queue": '6a74cbd679972be49ea46dae',
    'Future Ideas': '6a74cbd56a538340582a8897',
}

# Simplified classify
def classify(name, labels, desc=""):
    name_lower = name.lower()
    desc_lower = (desc or "").lower()
    label_names = [l.get('name', '').lower() for l in labels]

    if "OODA_PROCESSED" in desc or "Miss Pink OODA" in desc:
        return ""

    for prio in ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Top 10', 'Future Ideas']:
        if prio.lower() in label_names and prio in LIST_IDS:
            return prio

    for qname in ["Sir Azure's Queue", "Sir Green's Queue"]:
        if qname.lower() in label_names:
            return qname

    p1_signals = ['critical', 'urgent', 'emergency', 'blocker', 'p0', 'alert',
                  'do now', 'squidstation', 'void pirate github blocked',
                  'docker build failed', 'docker push failed', 'docker down']
    if any(k in name_lower for k in p1_signals):
        return 'P1'

    p2_signals = ['implement discord', 'integrate buffer', 'connect zapier',
                  'deploy torus', 'deploy dashboard', 'fix dashboard', 'fix docker',
                  'setup square', 'square payments', 'pos live', 'inventory live',
                  'website launch', 'launch payment', 'go live', 'production sop',
                  'first sale', 'first dollar', 'revenue stream', 'bug hunt',
                  'build automation dashboard', 'vault audit', 'audit sir']
    if any(k in name_lower for k in p2_signals):
        return 'P2'

    if 'sir azure' in name_lower or 'sirazure' in name_lower:
        return "Sir Azure's Queue"
    if 'sir green' in name_lower or 'sirgreen' in name_lower:
        return "Sir Green's Queue"

    # Default: check if in P2 already with P2 label
    for prio in ['P2', 'P3']:
        if prio.lower() in label_names and prio in LIST_IDS:
            return prio

    # Fallback
    return ""

# Get all open cards
cards = None
for a in range(3):
    try:
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "name,idList,labels,desc,dateLastActivity,due,closed,id"},
                             timeout=60).json()
        break
    except Exception as e:
        time.sleep(3)

if not cards:
    print("FAILED to fetch cards")
    exit(1)

open_cards = [c for c in cards if not c.get("closed")]
ln = {v: k for k, v in LIST_IDS.items()}

moves = []
for c in open_cards:
    desc = c.get("desc", "")
    labels = c.get("labels", [])
    classification = classify(c.get("name",""), labels, desc)

    if classification == "":
        continue

    target_list_id = LIST_IDS.get(classification)
    if not target_list_id:
        continue

    current_list_id = c.get("idList")
    if current_list_id != target_list_id:
        ooda = "OODA_PROCESSED" in desc
        current_list_name = ln.get(current_list_id, "???")
        label_names = [l.get("name","") for l in labels if l.get("name","")]
        moves.append(f"[{current_list_name} -> {classification}] [{c['id'][:8]}] {c['name'][:50]} | labels={label_names} | OODA={ooda}")

print(f"Would-move: {len(moves)} cards")
for m in moves[:20]:
    print(f"  {m}")
if len(moves) > 20:
    print(f"  ... and {len(moves)-20} more")
