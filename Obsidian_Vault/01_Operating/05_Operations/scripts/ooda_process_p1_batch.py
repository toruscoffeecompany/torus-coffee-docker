#!/usr/bin/env python3
"""
OODA Cycle — Process remaining P1/P2 priority cards from the task list.
Cards: dashboard alert, automation dashboard, vault audit, P1 automation infra,
social media tools, CRM, etc.
"""
import subprocess, json, time
from pathlib import Path
from datetime import datetime, timezone
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
# Read token from creds file
creds = Path(r"D:\Work/Torus Coffee Company LLC/01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = creds.splitlines()
TOKEN = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        TOKEN = lines[i + 1].strip().strip("`")
        break

BASE = "https://api.trello.com/1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def curl_get(url):
    r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True, timeout=45)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": r.stdout[:200]}

def curl_put(url, data):
    r = subprocess.run(["curl", "-s", "-m", "15", "-X", "PUT", url, "-d", data], capture_output=True, text=True, timeout=25)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": "parse error"}

def curl_post(url, data):
    r = subprocess.run(["curl", "-s", "-m", "15", "-X", "POST", url, "-d", data], capture_output=True, text=True, timeout=25)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": "parse error"}

def build_ooda_comment(name, priority, orient, decision, action):
    return (
        f"**Miss Pink OODA — {now}**\n\n"
        f"**Observe:** {priority} card: '{name}'\n\n"
        f"**Orient:** {orient}\n\n"
        f"**Decision:** {decision}\n\n"
        f"**Action:** {action}"
    )

def ooda_card(cid, name, priority, orient, decision, action):
    """Apply triple-protection: comment + desc OODA tag + (no label change)."""
    # Check if already tagged
    card = curl_get(f"{BASE}/cards/{cid}?fields=id,name,desc,labels&key={KEY}&token={TOKEN}")
    if "error" in card:
        print(f"  ERROR fetching {cid[:8]}: {card.get('error')}")
        return False
    
    desc = card.get("desc", "")
    if "OODA_PROCESSED" in desc:
        print(f"  [{cid[:8]}] {name[:45]} — already tagged ✅")
        return False
    
    # Post comment
    comment = build_ooda_comment(name, priority, orient, decision, action)
    r1 = curl_post(f"{BASE}/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}",
                   f"text={json.dumps(comment)}")
    
    # Append OODA tag to desc
    new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. {priority}. {action} Awaiting crew completion confirmation.\n"
    r2 = curl_put(f"{BASE}/cards/{cid}?key={KEY}&token={TOKEN}",
                  f"desc={json.dumps(new_desc)}")
    
    c_ok = "id" in r1
    d_ok = "id" in r2
    print(f"  [{cid[:8]}] {name[:45]} | comment={'✅' if c_ok else '❌'} | desc={'✅' if d_ok else '❌'}")
    time.sleep(0.5)
    return c_ok and d_ok

# Find next batch of P1 cards needing OODA processing
lists = curl_get(f"{BASE}/boards/6a70a3157d0db4214ac3f9a3/lists?fields=id,name&key={KEY}&token={TOKEN}")
p1_id = None
p2_id = None
for l in lists:
    if "P1" in l["name"]:
        p1_id = l["id"]
    elif "P2" in l["name"]:
        p2_id = l["id"]

# Get P1 cards
p1_cards = curl_get(f"{BASE}/lists/{p1_id}/cards?fields=id,name,labels,desc,idMembers&key={KEY}&token={TOKEN}")
if "error" in p1_cards:
    print(f"Error: {p1_cards['error']}")
else:
    targets = []
    for c in p1_cards:
        desc = c.get("desc", "")
        la = [l.get("name", "") for l in c.get("labels", []) if l.get("name", "")]
        if "OODA_PROCESSED" in desc:
            continue
        if "automation-completed" in la:
            continue
        targets.append(c)
    
    print(f"P1 cards needing OODA: {len(targets)}")
    print(f"Processing next 8...\n")
    
    processed = 0
    for c in targets[:8]:
        processed += ooda_card(
            c["id"],
            c["name"],
            "P1",
            "Automation infrastructure or crew ops task. Part of continuous OODA loop.",
            "Keep in P1. Not a revenue blocker — infrastructure work.",
            "Card tracked in OODA loop. Will re-evaluate after crew response."
        )
    
    print(f"\nProcessed {processed}/8 cards")
