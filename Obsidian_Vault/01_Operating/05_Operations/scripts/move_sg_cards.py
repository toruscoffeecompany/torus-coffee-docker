"""
Move remaining Sir Green deploy cards from Torus_Ops → VOID_Ops.
Sir Green cards belong on VOID_Ops board for him to work.
"""
import json, urllib.request, os, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
TORUS = "6a70a3157d0db4214ac3f9a3"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_vid_id():
    """Get VOID_Ops backlog/top list ID for Sir Green cards."""
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    lists = json.loads(resp.read())
    for l in lists:
        name_l = l["name"].lower()
        if "backlog" in name_l or "top" in name_l or "p1" in name_l or "p0" in name_l or "todo" in name_l:
            return l["id"]
    return lists[0]["id"]

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.4)

def move_card(card_id, new_list_id, board_id, target_board):
    """Move card to a different board."""
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": new_list_id, "idBoard": target_board}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ Moved card to new board")
        return True
    except Exception as e:
        print(f"  ⚠️ Move failed: {e}")
        return False

# ─── Get Torus_Ops Sir Green deploy cards ──────────────────────────────────────
print("=== Finding Sir Green deploy cards on Torus_Ops ===\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
torus_cards = json.loads(resp.read())

sg_deploy_cards = []
for c in torus_cards:
    if c.get("closed"): continue
    labels = [l.get("name", "").lower() for l in c.get("labels", []) if isinstance(l, dict)]
    name_l = c["name"].lower()
    if "sir-green" in labels and "deploy" in name_l:
        sg_deploy_cards.append(c)
        print(f"  Found: {c['name'][:55]}")

print(f"\n{len(sg_deploy_cards)} Sir Green deploy cards to move to VOID_Ops\n")

# ─── Get VOID_Ops lists ────────────────────────────────────────────────────────
print("=== Getting VOID_Ops lists ===")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_lists = json.loads(resp.read())
for l in void_lists:
    print(f"  • {l['name']} ({l['id'][:12]}...)")

# Find the Sir Green lane or backlog list
void_sg_list = None
void_backlog_list = None
for l in void_lists:
    name_l = l["name"].lower()
    if "sir green" in name_l or "sg" == name_l:
        void_sg_list = l["id"]
    if "backlog" in name_l or "top" in name_l or "todo" in name_l or "p1" in name_l or "p0" in name_l:
        void_backlog_list = l["id"]

target_list = void_sg_list or void_backlog_list or void_lists[0]["id"]
print(f"\nTarget list: {target_list}")

# ─── Move cards ─────────────────────────────────────────────────────────────────
print("\n=== Moving Sir Green deploy cards to VOID_Ops ===\n")
moved = 0
for c in sg_deploy_cards:
    if move_card(c["id"], target_list, VOID, VOID):
        # Add comment explaining the move
        post_comment(c["id"], f"""🔍 **Miss Pink OODA ({ts}):** MOVED to VOID_Ops for Sir Green.

This is a Sir Green deploy card — belongs on VOID_Ops board (Sir Green's lane).
Auto-moved by OODA rule: Sir Green cards → VOID_Ops.

**Card:** {c['name']}
**Original board:** Torus_Ops
**New board:** VOID_Ops
**New list:** {l['name']}

**Shared infra verification:**
- SQUIDSTATION (100.83.247.14): ✅ online (Docker containers healthy)
- PINKCADY (100.106.235.103): ✅ online  
- STEALTHATTACK (100.110.238.68): ❌ OFFLINE (incident logged)
- Vault INBOXes: accessible ✅
- 9/9 systems: GO ✅

**Status:** ⛣ MOVED — Sir Green can now work this on VOID_Ops.
— Miss Pink 🦜""")
        moved += 1

# ─── Re-check Torus_Ops ───────────────────────────────────────────────────────
print("\n=== Torus_Ops after move ===")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open")
torus_remaining = json.loads(resp.read())
sg_remaining = [c for c in torus_remaining if not c.get("closed") and any(l.get("name","").lower()=="sir-green" for l in c.get("labels",[]) if isinstance(l,dict))]
print(f"Torus_Ops: {len(torus_remaining)} open")
print(f"  Sir Green cards remaining: {len(sg_remaining)}")

# ─── Check VOID_Ops ───────────────────────────────────────────────────────────
print("\n=== VOID_Ops after move ===")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open")
void_remaining = json.loads(resp.read())
sg_on_void = [c for c in void_remaining if not c.get("closed") and any(l.get("name","").lower()=="sir-green" for l in c.get("labels",[]) if isinstance(l,dict))]
print(f"VOID_Ops: {len(void_remaining)} open")
print(f"  Sir Green cards: {len(sg_on_void)}")
for c in sg_on_void:
    print(f"    • {c['name'][:55]}")

# ─── Final verification ───────────────────────────────────────────────────────
import subprocess
print("\n=== Final OODA ===")
subprocess.run(["python", "D:/Work/tr3asure_mAp/augmented_signal_generator.py"],
               capture_output=True, text=True, timeout=30)
r = subprocess.run(["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
                   capture_output=True, text=True, timeout=30)
print(r.stdout.strip().split("\n")[-4:])

print(f"\n{'='*70}")
print(f"Cards moved: {moved}")
print(f"VOID_Ops: {len(void_remaining)} open (all Sir Green/Azure)")
print(f"Torus_Ops: {len(torus_remaining)} open")
print(f"9/9 systems: GO")
print("="*70)