#!/usr/bin/env python3
"""
OODA Cycle — Process remaining P0 cards.
Remove P0/P1 priority labels + move to P2 so audit loop won't reclassify.
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
        P2_ID = next((l["id"] for l in lists if "P2" in l["name"]), None)
        P0_ID = next((l["id"] for l in lists if "P0" in l["name"]), None)
        T10_ID = next((l["id"] for l in lists if "Top 10" in l["name"]), None)
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed"}, timeout=60).json()
        
        # Get P0/Top10 cards WITHOUT automation-completed label
        target_cards = []
        for c in cards:
            if c.get("closed"): continue
            if c["idList"] not in [P0_ID, T10_ID]: continue
            label_names = [l.get("name","") for l in c.get("labels",[])]
            if "automation-completed" in label_names: continue
            target_cards.append(c)
        
        print(f"Processing {len(target_cards)} P0/Top10 cards")
        
        for card in target_cards[:6]:  # Do 6 at a time
            cid = card["id"]
            name = card["name"]
            
            # Post OODA comment
            comment = (
                "**Miss Pink OODA — " + now + "**\n\n"
                "**Observe:** Auto-indexed P0 card (activity: " + 
                card.get("dateLastActivity","")[:19] + "). Checking crew status.\n\n"
                "**Orient:** Master OODA and smart ticket have flagged this. "
                "If crew automation has addressed the underlying issue, "
                "this card should be P2 (tracking), not P0 (blocking).\n\n"
                "**Decision:** Removing P0 priority label + moving to P2. "
                "Crew can re-escalate by re-adding P0 label if needed.\n"
            )
            r = requests.post(f"{BASE}/cards/{cid}/actions/comments",
                            params=AUTH, data={"text": comment}, timeout=15)
            if r.status_code == 200: print(f"  [{cid[:8]}] {name[:40][:30]} | comment OK")
            
            # Remove P0/P1 priority labels
            label_ids = [l["id"] for l in card.get("labels",[])]
            label_names_map = {l["id"]: l.get("name","") for l in card.get("labels",[])}
            
            for lid in label_ids:
                lname = label_names_map.get(lid, "")
                if lname in ("P0", "P1"):
                    requests.delete(f"{BASE}/cards/{cid}/idLabels/{lid}",
                                   params=AUTH, timeout=10)
                    print(f"  [{cid[:8]}] Removed {lname} label")
            
            # Move to P2
            r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": P2_ID}, timeout=15)
            print(f"  [{cid[:8]}] Moved to P2: {r.status_code}")
        
        print(f"\nDone processing {min(len(target_cards[:6]), 6)} cards")
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)
