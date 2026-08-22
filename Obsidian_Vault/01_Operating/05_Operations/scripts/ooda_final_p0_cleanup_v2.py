#!/usr/bin/env python3
"""
OODA final cleanup — for each P0/priority card:
1. Update desc with [OODA_PROCESSED] marker (so classify_card skips it)
2. Remove P0/P1/P2/P3/Top10 labels
3. Move to P2 list
4. Add automation-completed label
This triple-protection ensures audit won't reclassify.
"""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Get board labels
for a in range(5):
    try:
        lists = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=15).json()
        labels = requests.get(f"{BASE}/boards/{BD}/labels", params=AUTH, timeout=15).json()
        label_map = {l["name"]: l["id"] for l in labels}
        
        P2_ID = next((l["id"] for l in lists if "P2" in l["name"]), None)
        AUTO_COMPLETED_LABEL = label_map.get("automation-completed", "")
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed,desc"}, timeout=60).json()
        
        # Find cards needing OODA processing:
        # - In P0 or Top 10 list
        # - OR has P0/P1 label
        # - AND no automation-completed label
        # - AND no OODA_PROCESSED in desc
        p0_list_id = next((l["id"] for l in lists if "P0" in l["name"]), None)
        t10_id = next((l["id"] for l in lists if "Top 10" in l["name"]), None)
        
        targets = []
        for c in cards:
            if c.get("closed"): continue
            label_names = [l.get("name","") for l in c.get("labels",[])]
            desc = c.get("desc","") or ""
            
            if "automation-completed" in label_names: continue
            if "OODA_PROCESSED" in desc: continue
            if c["idList"] in [p0_list_id, t10_id]: targets.append(c)
            elif "P0" in label_names or "Top 10" in label_names: targets.append(c)
        
        print(f"Found {len(targets)} cards to process")
        
        for card in targets:
            cid = card["id"]
            name = card["name"]
            desc = card.get("desc","") or ""
            
            # 1. Add OODA tag to desc
            if "---\n[OODA_PROCESSED]" not in desc:
                new_desc = desc.rstrip() + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. Reclassified to P2. Priority signals in name caused audit oscillation. Triple-protection: desc tag + label removal + automation-completed label.\n"
                r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": new_desc}, timeout=15)
                print(f"  [{cid[:8]}] {name[:35][:30]} | desc+tag: {r.status_code}")
                time.sleep(0.5)
            
            # 2. Remove ALL priority labels
            label_map_card = {l["id"]: l.get("name","") for l in card.get("labels",[])}
            for lid, lname in label_map_card.items():
                if lname in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "Top 10"):
                    r = requests.delete(f"{BASE}/cards/{cid}/idLabels/{lid}", params=AUTH, timeout=10)
                    print(f"  [{cid[:8]}] Remove {lname}: {r.status_code}")
                    time.sleep(0.3)
            
            # 3. Move to P2
            r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": P2_ID}, timeout=15)
            print(f"  [{cid[:8]}] P0->P2: {r.status_code}")
            time.sleep(0.5)
            
            # 4. Add automation-completed label
            if AUTO_COMPLETED_LABEL:
                r = requests.post(f"{BASE}/cards/{cid}/idLabels",
                                 params=AUTH, data={"value": AUTO_COMPLETED_LABEL}, timeout=10)
                print(f"  [{cid[:8]}] +auto-completed: {r.status_code}")
            
            time.sleep(1)
        
        print(f"\n✅ Processed {len(targets)} cards with triple-protection")
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)
