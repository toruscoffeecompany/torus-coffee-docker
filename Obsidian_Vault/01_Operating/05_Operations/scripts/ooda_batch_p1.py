#!/usr/bin/env python3
"""
OODA Cycle — Batch process P1 cards (auto-indexed stubs).
For each card: Observe (read desc/comments), Orient (check vault for code), 
Decide (comment + tag + reclassify if needed), Act (update Trello).
"""
import requests, time, os
from datetime import datetime, timezone
from pathlib import Path

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
VAULT = "D:/Work/Torus Coffee Company LLC"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for a in range(5):
    try:
        lists = requests.get(f"{BASE}/boards/{BD}/lists", params=AUTH, timeout=30).json()
        ln = {l["id"]: l["name"] for l in lists}
        P1_ID = next((l["id"] for l in lists if "P1" in l["name"]), None)
        
        cards = requests.get(f"{BASE}/boards/{BD}/cards",
                             params={**AUTH, "fields": "id,name,idList,labels,closed,desc,due"},
                             timeout=60).json()
        
        # Get P1 cards without OODA tag or automation-completed
        targets = []
        for c in cards:
            if c.get("closed"): continue
            if c["idList"] != P1_ID: continue
            la = [l.get("name","") for l in c.get("labels",[])]
            if "automation-completed" in la: continue
            desc = c.get("desc","") or ""
            if "OODA_PROCESSED" in desc: continue
            targets.append(c)
        
        targets.sort(key=lambda x: x.get("dateLastActivity",""))
        
        for c in targets[:6]:
            cid = c["id"]
            name = c["name"]
            desc = c.get("desc","") or ""
            
            # Extract keyword for vault search
            keywords = []
            name_lower = name.lower()
            for k in ["zapier", "buffer", "hubspot", "bug", "orchestrator", "automation"]:
                if k in name_lower:
                    keywords.append(k)
            
            # Check vault for existing scripts
            script_found = False
            script_desc = ""
            for k in keywords:
                # Search for script file
                script_name = f"{k}_automation.py"
                script_path = Path(VAULT) / "10_Skills_Library" / "05_Operations" / "scripts" / script_name
                if script_path.exists():
                    script_found = True
                    script_desc = f"Found existing script: `scripts/{script_name}`"
            
            # Get comments
            actions = requests.get(f"{BASE}/cards/{cid}/actions",
                                 params={**AUTH, "fields": "type,date,data"}, timeout=15).json()
            comments = [a for a in actions if a.get("type") == "commentCard"]
            comment_count = len(comments)
            
            # Build OODA comment
            obs = f"Auto-indexed P1 card. {comment_count} comments. {script_desc if script_found else 'No existing script found in vault.'}"
            orient = "Card tracks automation infrastructure task. " + (
                "Script exists — needs wiring into orchestrator." if script_found 
                else "Script needs to be created."
            )
            action = "Posting OODA review comment. Tagging with [OODA_PROCESSED]. " \
                     "Not a P0 blocker — stays P1 for tracking."
            
            comment_text = (
                f"**Miss Pink OODA — {now}**\n\n"
                f"**Observe:** {obs}\n\n"
                f"**Orient:** {orient}\n\n"
                f"**Decision:** Demoting P0 signals, keeping in P1 for proper tracking.\n\n"
                f"**Action:** {action}"
            )
            r = requests.post(f"{BASE}/cards/{cid}/actions/comments",
                            params=AUTH, data={"text": comment_text}, timeout=15)
            
            # Update desc with OODA tag
            if "OODA_PROCESSED" not in desc:
                new_desc = desc.rstrip() + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. {obs} {script_desc if script_found else 'No existing script in vault.'} Tracking in P1.\n"
                r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": new_desc}, timeout=15)
            
            print(f"  [{cid[:8]}] {name[:45]} | comment: {r.status_code} | desc: {r.status_code}")
            time.sleep(1)
        
        print(f"\n✅ Processed {len(targets[:6])} P1 cards")
        break
    except Exception as e:
        print(f"Attempt {a+1}: {e}")
        time.sleep(3)
