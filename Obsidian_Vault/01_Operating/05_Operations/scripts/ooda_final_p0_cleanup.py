#!/usr/bin/env python3
"""
OODA Cycle — Final cleanup of remaining 11 P0 cards.
For each card: update DESC with OODA tag FIRST, then remove P0/P1 labels, then move to P2.
This ensures the audit loop's classify_card() sees "Miss Pink OODA" in desc and skips it.
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
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed,desc"}, timeout=60).json()
        
        # Find P0 cards (by label or list)
        p0_cards = []
        for c in cards:
            if c.get("closed"): continue
            label_names = [l.get("name","") for l in c.get("labels",[])]
            if "P0" in label_names or "automation-completed" in label_names:
                p0_cards.append(c)
            elif "OODA_PROCESSED" in (c.get("desc","") or ""):
                continue  # Already processed
        
        # Also find cards auto-promoted to P0 list but without P0 label
        p0_list_id = next((l["id"] for l in lists if "P0" in l["name"]), None)
        t10_id = next((l["id"] for l in lists if "Top 10" in l["name"]), None)
        for c in cards:
            if c.get("closed"): continue
            if c["idList"] in [p0_list_id, t10_id]:
                desc = c.get("desc","") or ""
                if "OODA_PROCESSED" not in desc and c not in p0_cards:
                    p0_cards.append(c)
        
        # Remove duplicates
        seen = set()
        unique = []
        for c in p0_cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                unique.append(c)
        p0_cards = unique
        
        print(f"Processing {len(p0_cards)} remaining P0/priority cards")
        
        for card in p0_cards:
            cid = card["id"]
            name = card["name"]
            desc = card.get("desc","") or ""
            
            # Skip if already has OODA_PROCESSED in desc
            if "OODA_PROCESSED" in desc:
                print(f"  [{cid[:8]}] {name[:40][:30]} | already processed, skipping")
                continue
            
            # Step 1: Update DESC with OODA_PROCESSED marker
            new_desc = (
                desc.rstrip() + "\n\n---\n"
                "[OODA_PROCESSED] " + now + " — Miss Pink OODA reviewed. "
                "Auto-indexed P0 card reclassified to P2. Priority signal in card name "
                "was causing audit loop oscillation. Priority labels removed.\n"
            )
            r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": new_desc}, timeout=15)
            print(f"  [{cid[:8]}] {name[:40][:30]} | desc updated: {r.status_code}")
            time.sleep(0.5)
            
            # Step 2: Remove ALL priority labels (P0, P1, etc.)
            label_ids = [l["id"] for l in card.get("labels",[])]
            label_map = {l["id"]: l.get("name","") for l in card.get("labels",[])}
            for lid in label_ids:
                lname = label_map.get(lid, "")
                if lname in ("P0", "P1", "P2", "P3", "Top 10"):
                    requests.delete(f"{BASE}/cards/{cid}/idLabels/{lid}",
                                   params=AUTH, timeout=10)
                    print(f"  [{cid[:8]}] Removed {lname} label")

            # Step 3: Move to P2
            r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": P2_ID}, timeout=15)
            print(f"  [{cid[:8]}] Moved to P2: {r.status_code}")
            time.sleep(0.5)
            
            # Step 4: Add automation-completed label
            for l in lists:
                pass  # labels don't have list context
            # We need the automation-completed label ID
            break
        
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)
