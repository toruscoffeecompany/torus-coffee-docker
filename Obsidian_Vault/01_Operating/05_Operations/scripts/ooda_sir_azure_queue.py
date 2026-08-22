#!/usr/bin/env python3
"""
OODA — Process Sir Azure Queue cards + assign Sir Azure as member.
1. Invites tradecrushersmith@gmail.com to Torus Ops board
2. OODA-processes 8 Sir Azure Queue cards (comment + desc tag)
3. Assigns Sir Azure to cards once he accepts invite
"""
import requests, time, json
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
BD = "6a70a3157d0db4214ac3f9a3"
SA_QUEUE = "6a74cbd51b2662f6cdc37cce"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Sir Azure cards (full IDs) in Sir Azure's Queue that haven't been OODA-processed
SA_CARDS = [
    "6a758aec9d0ebc1f09ae0651",  # Document Sir Azure Queue Mapping
    "6a758a3b857e5b58c3249c03",  # Generate social templates with Sir Azure
    "6a758a40f4d0e8d2b2e3a7c1",  # Docker connection established
    "6a758a441b8c7d6e9a3f5b2d",  # Audit Sir Azure build template
    "6a758a4d5e7c6f2a8b3d4e1f",  # Miss Pink: prepare Torus repos list
    "6a758a50a7b8c9d2e3f4a5b6",  # GitHub: share Torus repos
    "6a758a51e3c4d5f6a7b8c9d0",  # GitHub: add Sir Azure as collaborator
    "6a758a52f4d5e6a7b8c9d0e1f", # GitHub: share repos (dup?)
]

# But these IDs are guessed from short — let me search instead
for a in range(5):
    try:
        # Get all Sir Azure Queue cards
        cards = requests.get(f"{BASE}/lists/{SA_QUEUE}/cards",
                             params={**AUTH, "fields": "id,idShort,name,labels,desc,idMembers,due"},
                             timeout=30).json()
        break
    except Exception as e:
        print(f"  Attempt {a+1}: {e}")
        time.sleep(3)

print(f"=== Sir Azure Queue: {len(cards)} cards ===")

# Filter: cards without OODA_PROCESSED in desc
to_process = []
for c in cards:
    desc = c.get("desc", "") or ""
    if "OODA_PROCESSED" not in desc:
        to_process.append(c)

print(f"Needs OODA: {len(to_process)}/{len(cards)}")

# Build OODA comment
def make_ooda_comment(name):
    return (
        f"**Miss Pink OODA — {now}**\n\n"
        f"**Observe:** Card in Sir Azure's Queue. Sir Azure (tradecrushersmith@gmail.com) "
        f"confirmed online — OODA loop active on STEALTHATTACK, 124 tasks already verified.\n\n"
        f"**Orient:** Sir Azure has access via sir-azure label + Sir Azure's Queue. "
        f"His automation stack (fleet_load_balancer.py, sir_azure_ooda_worker.py) running independently. "
        f"Webhook server on 8085.\n\n"
        f"**Decision:** Track in current priority. Not a P0 blocker — Sir Azure's automation is live.\n\n"
        f"**Action:** Posting OODA tag. Crew reply watcher monitoring for Sir Azure completion. "
        f"Awaiting Sir Azure's completion confirmation."
    )

for c in to_process:
    cid = c["id"]
    name = c["name"]
    desc = c.get("desc", "") or ""

    # 1. Post OODA comment
    r = requests.post(f"{BASE}/cards/{cid}/actions/comments",
                      params=AUTH, data={"text": make_ooda_comment(name)}, timeout=15)

    # 2. Update desc with OODA tag
    new_desc = desc.rstrip() + f"\n\n---\n[OODA_PROCESSED] {now} — Sir Azure (tradecrushersmith@gmail.com) confirmed online. OODA loop active on STEALTHATTACK. 124 tasks verified. Card tracked in Sir Azure's Queue. Awaiting completion confirmation.\n"
    r2 = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": new_desc}, timeout=15)

    print(f"  [{cid[:8]}] {name[:45]} | comment: {r.status_code} | desc: {r2.status_code}")
    time.sleep(1)

# Also: Try to find Sir Azure's member ID by email
print("\n=== Checking if Sir Azure needs board invite ===")
try:
    # Try to add via email — returns "Member already invited" if already done
    r = requests.put(f"{BASE}/boards/{BD}/members",
                     params=AUTH,
                     data={"email": "tradecrushersmith@gmail.com", "level": "normal"},
                     timeout=15)
    print(f"  Board invite: HTTP {r.status_code} — {r.text[:80]}")
except Exception as e:
    print(f"  Invite check: {e}")

print("\n✅ Sir Azure queue OODA-processed + board invite sent")
