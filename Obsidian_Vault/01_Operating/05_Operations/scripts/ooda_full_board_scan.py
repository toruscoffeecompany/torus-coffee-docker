#!/usr/bin/env python3
"""
Full board scan — read all 354 open cards, categorize by list/priority, 
and generate a prioritized OODA task list.
"""
import requests, time, json
from datetime import datetime, timezone
from pathlib import Path

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
VAULT = "D:/Work/Torus Coffee Company LLC"

for a in range(5):
    try:
        lists = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=30).json()
        ln = {l["id"]: l["name"] for l in lists}
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed,desc,due,dateLastActivity"},
                             timeout=60).json()
        
        # Categorize all open cards
        categorized = {
            "needs_ooa_processing": [],  # OODA tag not in desc + no automation-completed
            "ooada_processed": [],      # Has OODA_PROCESSED in desc
            "automation_completed": [], # Has automation-completed label
            "done": [],                  # In Done list
        }
        
        done_id = next((l["id"] for l in lists if l["name"] == "Done"), None)
        
        # Priority order for task list
        list_priority = {
            "P0 - Alert / Critical / Do Now": 1,
            "Top 10 — Focus Fleet": 2,
            "P1 - High / Doing Now": 3,
            "Sir Azure's Queue": 4,
            "Sir Green's Queue": 5,
            "P2 - Med High / This Week": 6,
            "P3 - Medium / Follow Up": 7,
            "Future Ideas": 8,
        }
        
        for c in cards:
            if c.get("closed"): continue
            cid = c["id"]
            name = c["name"]
            list_name = ln.get(c["idList"], "?")
            labels = [l.get("name","") for l in c.get("labels",[]) if l.get("name","")]
            desc = c.get("desc","") or ""
            due = c.get("due","")
            activity = c.get("dateLastActivity","")[:19]
            
            if c["idList"] == done_id:
                categorized["done"].append(c)
                continue
            
            if "automation-completed" in labels:
                categorized["automation_completed"].append(c)
                continue
            
            if "OODA_PROCESSED" in desc or "Miss Pink OODA" in desc:
                categorized["ooada_processed"].append(c)
                continue
            
            categorized["needs_ooa_processing"].append(c)
        
        # Sort needs_ooda_processing by priority order + activity
        def sort_key(c):
            lp = list_priority.get(ln.get(c["idList"], ""), 99)
            return (lp, c.get("dateLastActivity",""))
        
        categorized["needs_ooa_processing"].sort(key=sort_key)
        
        # Generate report
        print("=" * 70)
        print("OOO LOOP TASK LIST — ALL CARDS NEEDING REVIEW")
        print("=" * 70)
        print(f"Total open cards: {sum(1 for c in cards if not c.get('closed'))}")
        print(f"Done: {len(categorized['done'])}")
        print(f"Automation-completed: {len(categorized['automation_completed'])}")
        print(f"OODA-processed: {len(categorized['ooada_processed'])}")
        print(f"NEEDS OODA: {len(categorized['needs_ooa_processing'])}")
        print()
        
        # Group by list for the task list
        by_list = {}
        for c in categorized["needs_ooa_processing"]:
            ln_name = ln.get(c["idList"], "?")
            by_list.setdefault(ln_name, []).append(c)
        
        idx = 0
        for list_name in sorted(by_list.keys(), key=lambda x: list_priority.get(x, 99)):
            cards_in_list = by_list[list_name]
            print(f"\n## [{list_name}] ({len(cards_in_list)} cards)")
            for c in cards_in_list[:5]:  # Show top 5 per list
                idx += 1
                nm = c["name"][:55]
                act = c.get("dateLastActivity","")[:19]
                due = c.get("due","")[:10] if c.get("due") else "none"
                desc_preview = (c.get("desc","") or "")[:60].replace("\n"," ")
                print(f"  {idx}. [{c['id'][:8]}] {nm}")
                print(f"     act={act} | due={due} | desc: {desc_preview}")
        
        total = len(categorized["needs_ooa_processing"])
        print(f"\n{'='*70}")
        print(f"TOTAL CARDS NEEDING OODA: {total}")
        print(f"Will process in priority order (P0 > Top10 > P1 > Sir Azure > Sir Green > P2 > P3 > Future)")
        print(f"{'='*70}")
        
        # Save full list to file
        outpath = Path(VAULT) / "02_Business_Operations" / "Communications" / "Outbox" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_misspink_all_cards_ooda_tasklist.msg.md"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        
        lines = ["# OODA Task List — All Remaining Cards", "", f"Generated: {now}", "", f"Total cards needing OODA: {total}", ""]
        idx = 0
        for list_name in sorted(by_list.keys(), key=lambda x: list_priority.get(x, 99)):
            cards_in_list = by_list[list_name]
            lines.append(f"## [{list_name}] ({len(cards_in_list)} cards)")
            for c in cards_in_list:
                idx += 1
                lines.append(f"{idx}. [{c['id'][:8]}] {c['name']}")
                lines.append(f"   - Activity: {c.get('dateLastActivity','')[:19]}")
                if c.get("due"): lines.append(f"   - Due: {c['due'][:10]}")
                lines.append(f"   - Auto-indexed: {'Auto-indexed' in (c.get('desc','') or '')}")
            lines.append("")
        
        outpath.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nTask list saved to: {outpath}")
        
        break
    except Exception as e:
        print(f"Attempt {a+1}: {e}")
        time.sleep(3)
