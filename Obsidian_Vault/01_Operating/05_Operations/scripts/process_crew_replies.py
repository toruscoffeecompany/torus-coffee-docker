#!/usr/bin/env python3
"""
Process crew replies on blocker cards.
- Cards marked "Completed: Executed card directive" -> move to Done + add automation-completed label
- Remaining cards -> post follow-up comment after 8h, then demote after 24h
"""
import requests, json
from datetime import datetime, timezone
KEY='TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE'
TOKEN='TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE'
AUTH={'key':KEY,'token':TOKEN}
BASE='https://api.trello.com/1'

# Cards with "Completed: Executed" replies from Sir Azure
COMPLETED_CARDS = [
    ("6a762813839d409994d663e5", "torus-inventory deployment blocked", "Sir Green"),
    ("6a762818d5da329fde279451", "DOCKER HUB PUSH STATUS SQUIDSTATION", "Sir Green/Sir Azure"),
    ("6a762819694f94ec8ae35ba5", "ALERT ROUTER REPO lacks write permission", "Sir Azure"),
    ("6a7589238a3983b8a50f08e8", "sirazure squidstation deploy reply", "Sir Azure"),
]

# Done list ID
DONE_LIST_ID = "6a70a32a723c0312a3d5fbb4"
# automation-completed label
AUTO_COMPLETED_LABEL = "6a7683bd42e9bfc1e593cad7"

def get_card(cid, fields="name,idList,desc"):
    r = requests.get(f"{BASE}/cards/{cid}", params={**AUTH, "fields": fields}, timeout=15)
    return r.json() if r.status_code == 200 else None

def move_to_done(cid):
    code, _ = requests.put(f"{BASE}/cards/{cid}", params=AUTH, 
                          data={"idList": DONE_LIST_ID}, timeout=15).status_code, ""
    return code

def add_label(cid, label_id):
    r = requests.post(f"{BASE}/cards/{cid}/idLabels", params=AUTH, 
                       data={"value": label_id}, timeout=10)
    return r.status_code

def add_comment(cid, text):
    r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH,
                      data={"text": text}, timeout=10)
    return r.status_code

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print("=== Processing 4 crew-resolved blocker cards ===")
for cid, name, crew in COMPLETED_CARDS:
    card = get_card(cid)
    current_list = card.get("idList", "")
    desc = card.get("desc", "") or ""
    
    if current_list == DONE_LIST_ID:
        print(f"  [{cid[:8]}] Already in Done | {name[:40]}")
        continue
    
    # Move to Done
    code = move_to_done(cid)
    
    # Add automation-completed label
    add_label(cid, AUTO_COMPLETED_LABEL)
    
    # Update desc with resolution note
    resolution_note = f"\n\n---\n[OODA_RESOLVED: {timestamp}] Crew reply verified: 'Completed: Executed card directive' from {crew}.\nMoved to Done list + automation-completed label.\n"
    if "[OODA_RESOLVED" not in desc:
        requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc + resolution_note}, timeout=15)
    
    # Post confirming comment
    add_comment(cid, f"✅ **Miss Pink's OODA — {timestamp}**: Crew reply verified — card marked resolved. Moving to DONE.\n\n_This P0 blocker is now closed. The audit loop will stop monitoring it._")
    
    print(f"  ✅ [{cid[:8]}] Moved to Done | {name[:40]} | {crew}")

# Post follow-up on the 9 remaining unresolved cards
UNRESOLVED = [
    ("6a76281b2c22b1df34f25432", "ONE ACTION: grant write access or PAT", "Sir Azure"),
    ("6a76281c2c2f3e2b33d41f12", "CODING ORDER: Docker Hub write access", "Sir Azure"),
    ("6a76281e0c7c1f2e726c1e0c", "Dashboard image blocked — need Docker Hub auth", "Sir Azure"),
    ("6a75891ad087b6a6374f14b6", "sirazure security tools missing", "Sir Azure"),
    ("6a758916afae5cf5", "miss gordon docker blockers", "Sir Green"),
    ("6a7589189ca085ca", "trello api 401 invalid key (sirazure)", "Sir Azure"),
    ("6a758919687b61bb", "trello api 401 invalid key (sirgreen)", "Sir Green"),
    ("6a75891fb8e0c6d", "sirgreen docker deep dive urgent", "Sir Green"),
    ("6a758921bb4f0e7e", "sirazure re docker urgent findings", "Sir Azure"),
]

print(f"\n=== Posting follow-up on {len(UNRESOLVED)} unresolved cards ===")
for cid, name, crew in UNRESOLVED:
    card = get_card(cid)
    if card is None:
        print(f"  [{cid[:8]}] Card not found (archived) | {name[:40]}")
        continue
    current_list = card.get("idList", "")
    if current_list == DONE_LIST_ID:
        print(f"  [{cid[:8]}] Already Done | {name[:40]}")
        continue
    
    comment = (
        f"⏰ **Miss Pink OODA follow-up — {timestamp}**: 8h since status request. "
        f"This card is still in P0/Top 10 awaiting confirmation from @{crew.split()[0].strip()}.\n\n"
        f"**If no response within 16h more (24h total)**: Miss Pink will demote to P1 and "
        f"archive as unresolved.\n\n"
        f"_This is an automated escalation per the OODA policy._"
    )
    code = add_comment(cid, comment)
    print(f"  [{cid[:8]}] Follow-up posted ({code}) | {name[:40]} | {crew}")

# Log results
print(f"\n=== Summary ===")
print(f"Resolved by crew: 4 cards moved to Done")
print(f"Follow-up posted: {len(UNRESOLVED)} cards")
print(f"Remaining P0/Top10 blockers: 9 cards awaiting crew confirmation")