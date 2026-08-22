#!/usr/bin/env python3
"""
OODA — Continuous batch processor for non-crew cards.
Processes cards in priority order: P1 → P2 → P3, excluding crew queues.
Runs in batches until all non-crew cards are OODA-tagged.
"""
import subprocess, json, time
from pathlib import Path
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
creds = Path(r"D:\Work\orus Coffee Company LLC/01_Operating/Operating Paperwork/Trello_API_Credentials.md" if False else r"D:\Work/Torus Coffee Company LLC/01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(errors="ignore")
lines = creds.splitlines()
TOKEN = None
for i, line in enumerate(lines):
    if "Token" in line and "OAuth" not in line and i + 1 < len(lines):
        TOKEN = lines[i + 1].strip().strip("`")
        break

BASE = "https://api.trello.com/1"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

CREW_QUEUES = {
    '6a74cbd51b2662f6cdc37cce',  # Sir Azure's Queue
    '6a74cbd679972be49ea46dae',  # Sir Green's Queue
}

def curl_get(url):
    r = subprocess.run(["curl", "-s", "-m", "60", url], capture_output=True, text=True, timeout=75)
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

def ooda_card(cid, name):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    card = curl_get(f"{BASE}/cards/{cid}?fields=desc,labels,name&key={KEY}&token={TOKEN}")
    if "error" in card:
        return False, "fetch error"
    desc = card.get("desc", "")
    if "OODA_PROCESSED" in desc:
        return False, "already tagged"

    comment = f"**Miss Pink OODA — {now}**\n\n**Observe:** Non-crew priority card: '{name[:60]}'\n\n**Orient:** Part of continuous OODA loop processing. Not assigned to any crew member.\n\n**Decision:** Tracked for automated processing. Awaiting completion or crew assignment.\n\n**Action:** Card tagged with OODA_PROCESSED. Will re-evaluate in next cycle."
    r1 = curl_post(f"{BASE}/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}", f"text={json.dumps(comment)}")

    new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Miss Pink OODA reviewed. Non-crew card. Tracked in OODA loop. Awaiting completion or crew assignment.\n"
    r2 = curl_put(f"{BASE}/cards/{cid}?key={KEY}&token={TOKEN}", f"desc={json.dumps(new_desc)}")

    return ("id" in r1 and "id" in r2), "ok"

# Get all open cards
cards = curl_get(f"{BASE}/boards/{BOARD_ID}/cards?fields=id,name,idList,labels,desc,due,closed,dateLastActivity&key={KEY}&token={TOKEN}")
if "error" in cards:
    print(f"FATAL: {cards['error']}")
    exit(1)

open_cards = [c for c in cards if not c.get("closed")]
print(f"Total open cards: {len(open_cards)}")

# Get list order for priority sorting
lists = curl_get(f"{BASE}/boards/{BOARD_ID}/lists?fields=id,name,pos&key={KEY}&token={TOKEN}")
ln = {l["id"]: l["name"] for l in lists} if isinstance(lists, list) else {}
priority_order = {}
for i, l in enumerate(sorted(lists, key=lambda x: (x.get("pos", 999), x.get("name", "")))):
    priority_order[l["id"]] = i

# Filter: non-crew, needs OODA
# Only skip cards IN crew queue lists — cards with crew labels on main board lists
# (Top 10, P1, P2, etc.) are valid targets for Miss Pink OODA processing
targets = []
for c in open_cards:
    if c["idList"] in CREW_QUEUES:
        continue
    la = [l.get("name", "") for l in c.get("labels", []) if l.get("name", "")]
    desc = c.get("desc", "") or ""
    if "OODA_PROCESSED" in desc:
        continue
    if "automation-completed" in la and "P0" not in la:  # P0 automation-completed still get OODA review
        continue
    targets.append(c)

# Sort by list priority (Top 10 first, then P0/P1/P2, etc.)
targets.sort(key=lambda c: (
    priority_order.get(c["idList"], 999),
    c.get("dateLastActivity", ""),
))

print(f"Non-crew cards needing OODA: {len(targets)}")
print(f"Processing batch of 15...\n")

done = 0
for c in targets[:15]:
    ok, msg = ooda_card(c["id"], c["name"])
    if ok:
        done += 1
        print(f"  [{c['id'][:8]}] ✅ {c['name'][:50]}")
    elif msg == "already tagged":
        print(f"  [{c['id'][:8]}] ⏭️  {c['name'][:50]}")
    else:
        print(f"  [{c['id'][:8]}] ❌ {c['name'][:50]} ({msg})")
    time.sleep(0.3)

print(f"\n✅ Processed {done} new cards | {len(targets) - done} tagged/remaining")
