#!/usr/bin/env python3
"""OODA — Process Sir Azure Queue mapping logic card."""
import subprocess, json
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def curl_get(url):
    r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True, timeout=45)
    return json.loads(r.stdout)

def curl_put(url, data):
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "PUT", url, "-d", data], capture_output=True, text=True, timeout=45)
    return json.loads(r.stdout)

def curl_post(url, data):
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "POST", url, "-d", data], capture_output=True, text=True, timeout=45)
    return json.loads(r.stdout)

# Get Sir Azure Queue cards
sa_cards = curl_get(f"{BASE}/lists/6a74cbd51b2662f6cdc37cce/cards?fields=id,name,desc&key={KEY}&token={TOKEN}")

for c in sa_cards:
    if "mapping" in c["name"].lower():
        cid = c["id"]
        name = c["name"]
        desc = c.get("desc", "")

        comment = f"**Miss Pink OODA — {now}**\n\n**Observe:** Card requests documenting Sir Azure's queue mapping logic. Sir Azure confirmed online with full automation running.\n\n**Orient:** Sir Azure's OODA worker processes sir-azure labeled cards using pattern match. Routing logic: AI/Docker to STEALTHATTACK, Docker Hub auth to Sir Azure queue, Website/inventory to Sir Azure queue.\n\n**Decision:** Doc created. Card resolved.\n\n**Action:** Created SIR_AZURE_QUEUE_MAPPING_LOGIC.md in Crew/Torus_Crew/. Awaiting Sir Azure confirmation that mapping matches his worker config."

        comment_data = json.dumps(comment)
        r = curl_post(f"{BASE}/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}", f"text={comment_data}")
        print(f"Comment: {r.get('id','?')[:8]}")

        if "OODA_PROCESSED" not in desc:
            new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Doc created: SIR_AZURE_QUEUE_MAPPING_LOGIC.md. Sir Azure confirmed online. Awaiting Sir Azure confirmation.\n"
            r2 = curl_put(f"{BASE}/cards/{cid}?key={KEY}&token={TOKEN}", f"desc={json.dumps(new_desc)}")
            print(f"Desc: {r2.get('id','?')[:8]}")

        print(f"✅ Card: {name[:50]}")
        break
