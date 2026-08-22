#!/usr/bin/env python3
"""
Move all P0/Top10 cards with automation-completed label back to Done.
Prevents audit loop from re-classifying resolved cards.
"""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
DONE_LIST = "6a70a32a723c0312a3d5fbb4"

for a in range(5):
    try:
        cards = requests.get(f"{BASE}/boards/{BD}/cards", params={**AUTH, "fields": "id,name,idList,labels,closed"}, timeout=60).json()
        
        moved = 0
        for c in cards:
            if c.get("closed"):
                continue
            labels = [l.get("name", "") for l in c.get("labels", [])]
            if "automation-completed" in labels and c["idList"] != DONE_LIST:
                r = requests.put(f"{BASE}/cards/{c['id']}", params=AUTH, data={"idList": DONE_LIST}, timeout=20)
                print(f"  [{c['id'][:8]}] {c['name'][:40]} -> Done: {r.status_code}")
                moved += 1
        
        # Also refresh index to note changes
        requests.get(f"{BASE}/boards/{BD}/cards", params={**AUTH, "fields": "id,name,idList"}, timeout=30)
        print(f"\n✅ Moved {moved} automation-completed cards back to Done")
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)
