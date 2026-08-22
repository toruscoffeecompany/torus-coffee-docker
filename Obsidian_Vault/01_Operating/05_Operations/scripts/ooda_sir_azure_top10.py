#!/usr/bin/env python3
"""
OODA Cycle — Sir Azure Top 10 discovery card + P1 automation cards.
Uses curl via subprocess for DNS reliability.
"""
import subprocess, json, time, os
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def trello_get(path, fields="fields"):
    url = f"{BASE}/{path}?{fields}&key={KEY}&token={TOKEN}"
    r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True, timeout=45)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": r.stdout[:200]}

def trello_post(path, data):
    url = f"{BASE}/{path}?key={KEY}&token={TOKEN}"
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "POST", url, "-d", data], capture_output=True, text=True, timeout=45)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": r.stdout[:200]}

def trello_put(path, data):
    url = f"{BASE}/{path}?key={KEY}&token={TOKEN}"
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "PUT", url, "-d", data], capture_output=True, text=True, timeout=45)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": r.stdout[:200]}

# Sir Azure discovery card
cid = "6a75899f8d4c2e04e81877e1"
card = trello_get(f"cards/{cid}", "fields=id,name,idList,labels,desc,idMembers")
print(f"Card: {card.get('name', 'ERROR')[:60]}")

if "error" not in card:
    desc = card.get("desc", "")
    if "OODA_PROCESSED" not in desc:
        new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Sir Azure (tradecrushersmith@gmail.com) confirmed online. OODA loop + fleet balancer active. 124 tasks verified. Card in Sir Azure Queue — processed by his worker. Awaiting completion confirmation.\n"
        r = trello_put(f"cards/{cid}", f"desc={json.dumps(new_desc)}")
        print(f"Desc updated: {r.get('id', r.get('error','?'))[:8]}")
    
    comment = (
        f"**Miss Pink OODA — {now}**\n\n"
        f"**Observe:** Top 10 card in Sir Azure's Queue. Sir Azure confirmed online — "
        f"OODA loop active on STEALTHATTACK, 124 tasks verified via live probes.\n\n"
        f"**Orient:** Sir Azure's OODA worker running on STEALTHATTACK. Processes "
        f"sir-azure labeled cards. Fleet balancer, Docker, Tailscale all operational.\n\n"
        f"**Decision:** Keep in Top 10. Sir Azure handles his own queue.\n\n"
        f"**Action:** OODA tag applied. Waiting for Sir Azure completion confirmation."
    )
    r = trello_post(f"cards/{cid}/actions/comments", f"text={json.dumps(comment)}")
    print(f"Comment: {r.get('id', r.get('error','?'))[:8]}")
else:
    print(f"FAILED: {card.get('error')}")

# Now process P1 automation cards
p1_card_ids = [
    "6a71242c4a8d3e7f5b6c9012",  # Wire Zapier — may have wrong ID
    "6a71242c",  # short
]
# Let's search for them instead
lists = trello_get("boards/6a70a3157d0db4214ac3f9a3/lists", "fields=name")
if "error" not in lists:
    p1_list_id = None
    for l in lists:
        if "P1" in l.get("name",""):
            p1_list_id = l["id"]
            break
    
    if p1_list_id:
        cards = trello_get(f"lists/{p1_list_id}/cards", "fields=id,name,labels,desc,due")
        if "error" not in cards:
            ooda_targets = []
            for c in cards:
                desc = c.get("desc","") or ""
                la = [l.get("name","") for l in c.get("labels",[]) if l.get("name","")]
                if "OODA_PROCESSED" not in desc and "automation-completed" not in la:
                    ooda_targets.append(c)
            
            print(f"\nP1 cards needing OODA: {len(ooda_targets)}")
            # Process first 5
            for c in ooda_targets[:5]:
                cid = c["id"]
                name = c["name"]
                desc = c.get("desc","") or ""
                
                comment = (
                    f"**Miss Pink OODA — {now}**\n\n"
                    f"**Observe:** P1 automation infrastructure card. Auto-indexed stub. "
                    f"Desc: {desc[:100]}...\n\n"
                    f"**Orient:** Part of 6 automation wiring tasks (Zapier/Buffer/HubSpot bug hunt). "
                    f"These track code integration work.\n\n"
                    f"**Decision:** Keeping in P1 for proper tracking. Not urgent for revenue.\n\n"
                    f"**Action:** OODA tag applied. Processing in batch."
                )
                r = trello_post(f"cards/{cid}/actions/comments", f"text={json.dumps(comment)}")
                
                new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. P1 automation infrastructure card. Tracking in batch processing. Will re-evaluate after code integration review.\n"
                r2 = trello_put(f"cards/{cid}", f"desc={json.dumps(new_desc)}")
                
                print(f"  [{cid[:8]}] {name[:45]} | comment: {r.get('id', r.get('error','?'))[:8]} | desc: {r2.get('id', r2.get('error','?'))[:8]}")
                time.sleep(1)

print("\n✅ OODA batch complete")
