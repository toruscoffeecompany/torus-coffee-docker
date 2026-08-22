#!/usr/bin/env python3
"""
OODA Deep Dive — Cross-board crew sync verification.
1. Read Trello creds from file
2. Check both board members
3. Verify VOID Ops has Sir Azure's Queue + Sir Green's Queue lists
4. Check Sir Azure's Queue cards need cross-board mirroring
5. Verify crew assignment labels
"""
import requests, json, sys, time
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"

# Read token from creds file
text = (VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = text.splitlines()
token = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        token = lines[i + 1].strip().strip("`")
        break

if not token:
    print("ERROR: No token found")
    sys.exit(1)

print(f"Token loaded: {token[:10]}...{token[-4:]}")
AUTH = {"key": KEY, "token": token}
BASE = "https://api.trello.com/1"

# Board IDs
TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"

for attempt in range(3):
    try:
        # 1. Check board members
        print("\n=== TORUS OPS members ===")
        torus_members = requests.get(f"{BASE}/boards/{TORUS}/members", params={**AUTH, "fields": "id,fullName,username"}, timeout=20).json()
        for m in torus_members:
            print(f"  {m['fullName']} ({m.get('username','no-username')}) id={m['id'][:8]}")
        
        print("\n=== VOID OPS members ===")
        void_members = requests.get(f"{BASE}/boards/{VOID}/members", params={**AUTH, "fields": "id,fullName,username"}, timeout=20).json()
        for m in void_members:
            print(f"  {m['fullName']} ({m.get('username','no-username')}) id={m['id'][:8]}")

        # 2. Check VOID Ops lists
        print("\n=== VOID OPS lists ===")
        void_lists = requests.get(f"{BASE}/boards/{VOID}/lists", params={**AUTH, "fields": "id,name"}, timeout=20).json()
        for l in void_lists:
            # get card count
            cards = requests.get(f"{BASE}/lists/{l['id']}/cards", params={**AUTH, "fields": "id"}, timeout=20).json()
            # check for Sir Azure/Green queues
            flag = " <-- CREW QUEUE" if "sir" in l['name'].lower() or "queue" in l['name'].lower() else ""
            print(f"  [{l['id'][:8]}] {l['name']:40s} | {len(cards)} cards{flag}")

        # 3. Check Sir Azure's Queue on Torus Ops
        print("\n=== TORUS OPS: Sir Azure's Queue ===")
        sa_list_id = "6a74cbd51b2662f6cdc37cce"
        sa_cards = requests.get(f"{BASE}/lists/{sa_list_id}/cards", params={**AUTH, "fields": "id,name,labels,idMembers,desc,due"}, timeout=20).json()
        print(f"Cards: {len(sa_cards)}")
        for c in sa_cards:
            la = [l.get("name","") for l in c.get("labels",[]) if l.get("name","")]
            members = c.get("idMembers", [])
            desc = c.get("desc","") or ""
            ooda = "✅" if "OODA_PROCESSED" in desc else "❌"
            print(f"  [{c['id'][:8]}] {c['name'][:50]} | labels={la} | members={len(members)} | OODA={ooda}")

        # 4. Check if VOID Ops has matching Sir Azure Queue
        print("\n=== VOID OPS: Sir Azure lists ===")
        for l in void_lists:
            if "sir" in l['name'].lower():
                cards = requests.get(f"{BASE}/lists/{l['id']}/cards", params={**AUTH, "fields": "id,name,labels"}, timeout=20).json()
                print(f"  [{l['id'][:8]}] {l['name']} | {len(cards)} cards")
                for c in cards[:5]:
                    print(f"    [{c['id'][:8]}] {c['name'][:45]}")
                if len(cards) > 5:
                    print(f"    ... and {len(cards)-5} more")

        break
    except Exception as e:
        print(f"Attempt {attempt+1}: {e}")
        time.sleep(3)
