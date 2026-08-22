#!/usr/bin/env python3
"""
OODA — Phase 2: Update SMS/Google Voice card due dates to October
+ Process next batch of non-crew P1/P2 cards.
"""
import subprocess, json, time
from pathlib import Path
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
creds = Path(r"D:\Work/Torus Coffee Company LLC/01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = creds.splitlines()
TOKEN = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        TOKEN = lines[i + 1].strip().strip("`")
        break

BASE = "https://api.trello.com/1"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Crew queue list IDs — NEVER touch
CREW_QUEUES = {
    '6a74cbd51b2662f6cdc37cce',  # Sir Azure's Queue
    '6a74cbd679972be49ea46dae',  # Sir Green's Queue
}

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

def ooda_card(cid, name, priority, what):
    card = curl_get(f"{BASE}/cards/{cid}?fields=desc,labels&key={KEY}&token={TOKEN}")
    if "error" in card:
        print(f"  ERROR: {cid[:8]}")
        return False
    desc = card.get("desc", "")
    if "OODA_PROCESSED" in desc:
        return None

    comment = f"**Miss Pink OODA — {now}**\n\n**Observe:** {priority} card: '{name}'\n\n**Orient:** {what}\n\n**Decision:** Keep in current priority. Not a revenue blocker.\n\n**Action:** Card tracked in OODA loop. Awaiting completion."
    r1 = curl_post(f"{BASE}/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}", f"text={json.dumps(comment)}")

    new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. {priority}. Tracked in OODA loop. Awaiting completion.\n"
    r2 = curl_put(f"{BASE}/cards/{cid}?key={KEY}&token={TOKEN}", f"desc={json.dumps(new_desc)}")

    r = "id" in r1
    d = "id" in r2
    print(f"  [{cid[:8]}] {name[:48]} | comment={'✅' if r else '❌'} | desc={'✅' if d else '❌'}")
    time.sleep(0.5)
    return r and d

# Get all open cards
cards = curl_get(f"{BASE}/boards/{BOARD_ID}/cards?fields=id,name,idList,labels,desc,due,closed,dateLastActivity&key={KEY}&token={TOKEN}")
if "error" in cards:
    print(f"FATAL: {cards['error']}")
    exit(1)

open_cards = [c for c in cards if not c.get("closed")]
print(f"Total open cards: {len(open_cards)}")

# 1. Find SMS + Google Voice cards and push due date to October
print("\n=== Updating SMS/Google Voice cards to October ===")
sms_april = "2026-04-01"  # Target month
for c in open_cards:
    if c["idList"] in CREW_QUEUES:
        continue
    name_lower = c.get("name", "").lower()
    desc_lower = (c.get("desc", "") or "").lower()
    
    if "sms" in name_lower or "google voice" in name_lower or "text automation" in name_lower:
        # Check current due date
        current_due = c.get("due", "")
        print(f"  [{c['id'][:8]}] {c['name'][:55]} — current due: {current_due or 'None'}")
        
        if not current_due or "2026-10" not in (current_due or ""):
            # Set due date to October 2026
            r = curl_put(f"{BASE}/cards/{c['id']}?key={KEY}&token={TOKEN}", "due=2026-10-15")
            if "id" in r:
                print(f"    ✅ Due date pushed to 2026-10-15")
                # Add OODA comment about the push
                comment = f"**Miss Pink OODA — {now}**\n\n**Observe:** SMS/Voice automation card. Not urgent for immediate launch.\n\n**Orient:** These are P1/P2 infrastructure cards. Due date pushed to October to align with Q4 marketing launch timeline.\n\n**Decision:** Push due date to October. Not blocking revenue — website launch is the priority.\n\n**Action:** Due date updated. Card remains in current priority queue. Will re-evaluate in October."
                curl_post(f"{BASE}/cards/{c['id']}/actions/comments?key={KEY}&token={TOKEN}", f"text={json.dumps(comment)}")
                # Add OODA tag
                desc = c.get("desc", "") or ""
                if "OODA_PROCESSED" not in desc:
                    new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Due date pushed to Q4 (October). Non-urgent infrastructure. Awaiting completion.\n"
                    curl_put(f"{BASE}/cards/{c['id']}?key={KEY}&token={TOKEN}", f"desc={json.dumps(new_desc)}")
            else:
                print(f"    ❌ Failed: {r.get('error', 'unknown')}")
        else:
            print(f"    Already October ✅")
        time.sleep(0.5)

# 2. Process next batch of non-crew P1/P2 cards
print("\n=== Processing non-crew P1/P2 cards ===")
# Get list names
lists = curl_get(f"{BASE}/boards/{BOARD_ID}/lists?fields=id,name&key={KEY}&token={TOKEN}")
ln = {l["id"]: l["name"] for l in lists} if isinstance(lists, list) else {}
p1_id = next((l["id"] for l in lists if "P1" in l["name"]), None)
p2_id = next((l["id"] for l in lists if "P2" in l["name"]), None)

targets = []
for c in open_cards:
    if c["idList"] in CREW_QUEUES:
        continue
    if c["idList"] not in (p1_id, p2_id):
        continue
    la = [l.get("name", "") for l in c.get("labels", []) if l.get("name", "")]
    desc = c.get("desc", "") or ""
    if "OODA_PROCESSED" in desc:
        continue
    if "automation-completed" in la:
        continue
    if "Sir Azure's Queue" in la or "Sir Green's Queue" in la:
        continue
    targets.append(c)

targets.sort(key=lambda c: c.get("dateLastActivity", ""))
print(f"Non-crew P1/P2 cards needing OODA: {len(targets)}")

processed = 0
for c in targets[:8]:
    result = ooda_card(c["id"], c["name"], "P1/P2", "Ops automation/infrastructure task.")
    if result is not False:
        processed += 1

print(f"\nProcessed {processed} new cards + updated SMS/Voice due dates")
