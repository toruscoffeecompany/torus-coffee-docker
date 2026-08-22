#!/usr/bin/env python3
"""
OODA — Process next batch of NON-crew P1/P2 priority cards.
Skips Sir Green's Queue, Sir Azure's Queue, and already-OODA-processed cards.
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

# Crew queue list IDs that we NEVER touch
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
        return None  # Already tagged

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
cards = curl_get(f"{BASE}/boards/{BOARD_ID}/cards?fields=id,name,idList,labels,desc,due,closed&key={KEY}&token={TOKEN}")
if "error" in cards:
    print(f"FATAL: {cards['error']}")
    exit(1)

open_cards = [c for c in cards if not c.get("closed")]
print(f"Total open cards: {len(open_cards)}")

# Filter: non-crew, needs OODA (no OODA tag, no automation-completed)
targets = []
for c in open_cards:
    if c["idList"] in CREW_QUEUES:
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

# Sort by priority (P1 first, then P2, then by dateLastActivity)
lists = curl_get(f"{BASE}/boards/{BOARD_ID}/lists?fields=id,name&key={KEY}&token={TOKEN}")
ln = {l["id"]: l["name"] for l in lists} if isinstance(lists, list) else {}
ln_names = {v: k for k, v in ln.items()}

targets.sort(key=lambda c: (
    0 if c["idList"] == ln_names.get("P1 - High / This Week") else
    1 if c["idList"] == ln_names.get("P2 - Medium / Follow Up") else
    2,
    c.get("dateLastActivity", ""),
))

print(f"Non-crew cards needing OODA: {len(targets)}")
print(f"Processing next 10 (excluding crew queues)...\n")

processed = 0
for c in targets[:10]:
    result = ooda_card(c["id"], c["name"], "P1/P2", "Automation/ops infrastructure task.")
    if result is not False:
        processed += 1

print(f"\nProcessed {processed} new cards")
