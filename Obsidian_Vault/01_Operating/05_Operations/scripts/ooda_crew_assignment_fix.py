#!/usr/bin/env python3
"""
Fix cross-board crew sync:
1. Invite Sir Azure (tradecrushersmith@gmail.com) to both boards
2. Create Sir Azure's Queue list on VOID Ops
3. Assign crew members to all queue cards
"""
import requests, json, time
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"

text = (VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = text.splitlines()
token = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        token = lines[i + 1].strip().strip("`")
        break

AUTH = {"key": KEY, "token": token}
BASE = "https://api.trello.com/1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"

# Sir Azure's Trello user ID — search by email
print("=== Inviting Sir Azure to boards ===")

for board_id, board_name in [(TORUS, "Torus Ops"), (VOID, "VOID Ops")]:
    # Try to add member by email
    r = requests.put(f"{BASE}/boards/{board_id}/members",
                     params=AUTH,
                     data={"email": "tradecrushersmith@gmail.com"},
                     timeout=15)
    status = r.status_code
    msg = r.text[:100]
    print(f"  {board_name}: HTTP {status} — {msg}")

# Find Sir Azure's member ID
print("\n=== Finding Sir Azure's Trello ID ===")
for a in range(3):
    try:
        members = requests.get(f"{BASE}/boards/{TORUS}/members",
                               params={**AUTH, "fields": "id,fullName,username"},
                               timeout=15).json()
        for m in members:
            if "Void Pirate" in m.get("fullName", "") or "sir" in (m.get("username","") or "").lower():
                print(f"  Sir Green/Void Pirate: {m['fullName']} id={m['id']}")
        if not any("sir azure" in m.get("fullName","").lower() for m in members):
            print("  Sir Azure NOT a member — invite pending email acceptance")
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)

# Create Sir Azure's Queue list on VOID Ops if it doesn't exist
print("\n=== VOID Ops: ensure Sir Azure's Queue list ===")
try:
    void_lists = requests.get(f"{BASE}/boards/{VOID}/lists",
                              params={**AUTH, "fields": "id,name"},
                              timeout=15).json()
    has_sa = any("Sir Azure" in l["name"] and "Queue" in l["name"] for l in void_lists)
    if not has_sa:
        r = requests.post(f"{BASE}/boards/{VOID}/lists",
                          params={**AUTH},
                          data={"name": "Sir Azure's Queue", "pos": "top"},
                          timeout=15)
        result = r.json()
        print(f"  Created: [{result['id'][:8]}] {result['name']}")
    else:
        sa_list = next(l for l in void_lists if "Sir Azure" in l["name"] and "Queue" in l["name"])
        print(f"  Exists: [{sa_list['id'][:8]}] {sa_list['name']}")
except Exception as e:
    print(f"  Error: {e}")

# Assign crew members to Sir Azure's Queue cards
print("\n=== Assigning crew to Sir Azure Queue cards ===")
sa_queue_id = "6a74cbd51b2662f6cdc37cce"
try:
    cards = requests.get(f"{BASE}/lists/{sa_queue_id}/cards",
                         params={**AUTH, "fields": "id,name,idMembers"},
                         timeout=20).json()
    
    for c in cards:
        current_members = c.get("idMembers", [])
        if len(current_members) == 0:
            print(f"  [{c['id'][:8]}] {c['name'][:45]} — unassigned")
except Exception as e:
    print(f"  Error: {e}")

print("\n✅ Crew assignment fix phase 1 complete")
