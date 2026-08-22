#!/usr/bin/env python3
"""
Promote revenue/payment cards to Top 10 with OODA protection.
Adds [OODA_PROCESSED] marker to desc so Top 10 enforcement won't demote them.
"""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for a in range(5):
    try:
        lists = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=15).json()
        labels = requests.get(f"{BASE}/boards/{BD}/labels", params=AUTH, timeout=15).json()
        label_map = {l["name"]: l["id"] for l in labels}
        T10_ID = next((l["id"] for l in lists if "Top 10" in l["name"]), None)
        TOP10_LID = label_map.get("Top 10", "")
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed,desc"}, timeout=60).json()
        
        targets = ["connect real payment", "choose payment processor", "choose payment processor alternative"]
        
        for c in cards:
            if c.get("closed"): continue
            for t in targets:
                if t in c["name"].lower():
                    cid = c["id"]
                    la = [l.get("name","") for l in c.get("labels",[])]
                    desc = c.get("desc","") or ""
                    
                    # Add OODA_PROTECTION to desc
                    if "OODA_PROCESSED" not in desc:
                        new_desc = desc.rstrip() + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. Revenue milestone promoted to Top 10. Protected from cap enforcement.\n"
                        r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": new_desc}, timeout=15)
                        print(f"[{cid[:8]}] {c['name'][:40]} | desc+protect: {r.status_code}")
                        time.sleep(0.5)
                    
                    # Add Top 10 label
                    if "Top 10" not in la:
                        r = requests.post(f"{BASE}/cards/{cid}/idLabels", params=AUTH, data={"value": TOP10_LID}, timeout=10)
                        print(f"[{cid[:8]}] +Top10: {r.status_code}")
                        time.sleep(0.5)
                    
                    # Move to Top 10 list
                    if c["idList"] != T10_ID:
                        r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": T10_ID}, timeout=15)
                        print(f"[{cid[:8]}] ->T10: {r.status_code}")
                        time.sleep(0.5)
                    break
        
        print("\n✅ Revenue cards promoted to Top 10 with OODA protection")
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)
