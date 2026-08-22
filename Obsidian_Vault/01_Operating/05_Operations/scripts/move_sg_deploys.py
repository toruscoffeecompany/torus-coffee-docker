"""
Move Sir Green deploy cards from Torus_Ops → VOID_Ops with CORRECT list IDs.
Also handle the Crownless Fortune + tornado-inventory cards (business, not deploy).
"""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"

# REAL VOID_Ops list IDs (FULL IDs — not truncated)
VOID_LISTS = {
    "sg_queue": "6a777169cd5feec20ef26ede",   # Sir Green's Queue
    "mp_queue": "6a74dd281f14adee0956cfc9",   # Miss Pink's Queue
    "sa_inbox": "6a7433843ab8c43597480116",   # Sir Azure's Inbox
    "p0": "6a73abbf4539aaa060199c07",         # P0 Critical
    "p1": "6a73abbf8482da2937217d6f",         # P1 High
    "p2": "6a73abbf275aa5c96ab03e67",         # P2 Medium
}

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def move_card_to_void(card_id, list_key, comment=""):
    dest_list = VOID_LISTS[list_key]
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": dest_list}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        if comment:
            post_comment(card_id, comment)
        return True
    except Exception as e:
        print(f"  ❌ Move failed: {e}")
        return False

# ─── Get Torus_Ops sir-green labeled cards ─────────────────────────────────────
print("="*70)
print("MOVING SIR GREEN DEPLOY CARDS → VOID_OPS")
print("="*70)

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,desc,closed&filter=open&limit=1000")
torus_cards = json.loads(resp.read())

move_comment = f"""🔄 **Miss Pink ROUTING ({ts}):**

Sir Green DEPLOY card — moved to VOID_Ops (Sir Green's board) for execution.
This is Captain-authorized P1 deployment work.

— 🦜"""

deploy_comment = f"""🔄 **Miss Pink ROUTING ({ts}):**

Deploy card — moved to VOID_Ops Sir Green's Queue.
Owner: Sir Green (SQUIDSTATION Docker access required).

— 🦜"""

business_comment = f"""🔄 **Miss Pink ROUTING ({ts}):**

Business card — moved to VOID_Ops Sir Green's Queue (tagged sir-green by project sync).
This is a shared/business item needing Sir Green's input.

— 🦜"""

moved = 0
for c in torus_cards:
    if c.get("closed"): continue
    labels = [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]
    name = c["name"].lower()
    
    # Move only SIR GREEN-only cards (not cross-crew)
    if "sir-green" in labels and "miss-pink" not in labels and "sir-azure" not in labels:
        print(f"\n  Card: {c['name'][:55]}")
        print(f"  Labels: {labels}")
        
        card_id = c["id"]
        if "deploy" in name:
            dest = "sg_queue"
            cm = deploy_comment
        elif "crownless" in name or "inventory" in name or "tornado" in name:
            # These look like business cards that got sir-green label
            dest = "sg_queue"
            cm = business_comment
        else:
            dest = "sg_queue"
            cm = move_comment
        
        if move_card_to_void(card_id, dest, cm):
            moved += 1
            print(f"    ✅ Moved to VOID_Ops ({dest})")
        time.sleep(0.5)

print(f"\n{'='*70}")
print(f"DONE — {moved} cards moved to VOID_Ops")
print("="*70)

# ─── Final board state ──────────────────────────────────────────────────────────
print(f"\n--- Final board state ---\n")
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?fields=name,labels,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_open = json.loads(resp2.read())
resp3 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?fields=name,labels,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
torus_open = json.loads(resp3.read())

print(f"VOID_Ops: {len(void_open)} open (all Sir Green + bugs)")
print(f"Torus_Ops: {len(torus_open)} open (business + cross-crew)")

sg_remaining = len([c for c in torus_open if not c.get("closed") and 
    "sir-green" in [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)] and
    "miss-pink" not in [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)] and
    "sir-azure" not in [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]])
print(f"Sir Green only remaining on Torus_Ops: {sg_remaining}")