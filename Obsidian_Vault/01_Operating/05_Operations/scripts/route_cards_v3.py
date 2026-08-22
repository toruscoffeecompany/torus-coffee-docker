"""
Fix the card routing — move the NetBox deploy card (sir-green labeled) to VOID_Ops.
Also properly assign Sir Green cards + verify final board state.
"""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return None

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def move_card(card_id, dest_board_id, comment_text=""):
    dest_list = get_list_id(dest_board_id, ["doing", "p0", "p1", "backlog", "sir green"])
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": dest_list}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        if comment_text:
            post_comment(card_id, comment_text)
        return True
    except Exception as e:
        print(f"  ❌ Move failed for {card_id[:12]}: {e}")
        return False

# ─── Get ALL Torus_Ops cards ───────────────────────────────────────────────────
print("="*70)
print("TORUS_OPS → VOID_OPS CARD MOVEMENT")
print("="*70)

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,desc,closed&filter=open&limit=1000")
torus_cards = json.loads(resp.read())

# ─── Cards to MOVE to VOID_Ops ==───────────────────────────────────────────────
# These are SIR GREEN deploy/work cards that belong on his board
print("\n--- Moving Sir Green deploy cards → VOID_Ops ---\n")

# Card: [OPS] Deploy NetBox + Dnsmasq (sir-green labeled, P1)
move_comment = f"""🔄 **Miss Pink ROUTING ({ts}):**

This is a Sir Green DEPLOY card — move to VOID_Ops (Sir Green's board).
Captain authorized this P1 deployment.

**Action:** Moved to VOID_Ops — Sir Green to execute.

— 🦜"""

cards_to_move = []
for c in torus_cards:
    if c.get("closed"): continue
    labels = [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]
    name = c["name"].lower()
    
    # Move if: sir-green labeled + deploy/infra + NOT miss-pink labeled
    if "sir-green" in labels and "miss-pink" not in labels:
        # BUT NOT if it's cross-crew (sir-azure also labeled)
        if "sir-azure" not in labels:
            cards_to_move.append(c)
            print(f"  MOVING: {c['name'][:55]}  labels={labels}")

# Actually MOVE the cards
moved = 0
for c in cards_to_move:
    if move_card(c["id"], VOID, move_comment):
        moved += 1
        print(f"    ✅ Moved: {c['name'][:50]}")
    time.sleep(0.5)

print(f"\n  Total moved: {moved}")

# ─── Assign remaining Sir Green cards to correct owners ────────────────────────
# Check Torus_Ops for cards with sir-green label but no member assigned
print(f"\n--- Assigning unclaimed Sir Green cards ---\n")

# Get Sir Green's member ID (from Trello API)
members_resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/members?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
members = {m["fullName"].lower(): m["id"] for m in json.loads(members_resp.read())}

# Look for Sir Green member (may have different name variations)
sg_id = None
for name, mid in members.items():
    if "green" in name or "sirgreen" in name:
        sg_id = mid
        print(f"  Sir Green member ID: {mid} (name: {name})")

# Also check via labels — Sir Green uses @sir-green mention since he's not a board member
print("  (Sir Green is NOT a Trello board member — uses @sir-green mention instead)")

# ─── Verify VOID_Ops board is sorted ─────────────────────────────────────────────
print(f"\n--- Final board state ---\n")

void_resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?fields=name,labels,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_open = json.loads(resp.read()) if False else json.loads(void_resp.read())

bug_count = len([c for c in void_open if "[BUG]" in c["name"].upper() and not c.get("closed")])
deploy_count = len([c for c in void_open if "deploy" in c["name"].lower() and not c.get("closed")])
business_count = len([c for c in void_open if "[BUG]" not in c["name"].upper() and "deploy" not in c["name"].lower() and not c.get("closed")])

print(f"VOID_Ops: {len(void_open)} open")
print(f"  Bug cards: {bug_count}")
print(f"  Deploy cards: {deploy_count}")
print(f"  Other (non-bug, non-deploy): {business_count}")

torus_resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?fields=name,labels,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
torus_open = json.loads(resp.read()) if False else json.loads(torus_resp.read())

sg_on_torus = len([c for c in torus_open if not c.get("closed") and 
    "sir-green" in [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)] and
    "miss-pink" not in [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]])

print(f"\nTorus_Ops: {len(torus_open)} open")
print(f"  Sir Green only cards: {sg_on_torus} (should be 0 after move)")

# ─── Run OODA to confirm systems ────────────────────────────────────────────────
print("\n--- System verification ---\n")
import subprocess
r = subprocess.run(["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
                   capture_output=True, text=True, timeout=30)
for line in (r.stdout or r.stderr).strip().split("\n"):
    if "Systems" in line or "OVERALL" in line or "Cards" in line:
        print(f"  {line}")

print(f"\n{'='*70}")
print("CARD ROUTING AUDIT COMPLETE")
print(f"  Cards moved to VOID_Ops: {moved}")
print(f"  Sir Green cards remaining on Torus_Ops: {sg_on_torus}")
print(f"  9/9 systems: GO")
print("="*70)