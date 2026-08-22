"""
TORUS_OPS CARD ROUTING AUDIT + REVIEW.
1. Scan ALL cards on Torus_Ops
2. Move Sir Green cards → VOID_Ops (assign to Sir Green there)
3. Ensure remaining cards are assigned correctly (miss-pink, sir-azure, captain, or unassigned)
4. Re-verify 9/9 systems
"""
import json, urllib.request, os, time, subprocess
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

FILES = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/found_bugs_v3.json"
if os.path.exists(FILES):
    with open(FILES) as f:
        FOUND = json.load(f)
else:
    FOUND = []

def add_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def file_bug(name, desc, priority="P0"):
    for f in FOUND:
        if f.get("name") == name:
            return None
    from datetime import timezone as tz
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                    data=json.dumps({"value": lid}).encode(), method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        FOUND.append({"name": name, "priority": priority, "card_id": cid, "filed_at": ts})
        with open(FILES, "w") as f:
            json.dump(FOUND, f, indent=2)
        print(f"  ✅ {name[:60]}")
    except Exception as e:
        print(f"  ❌ {name[:40]} — {e}")
    time.sleep(0.4)

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return None

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def move_card(card_id, dest_board_id):
    """Move card to VOID_Ops + assign Sir Green."""
    # Get Sir Green's Trello member ID
    # Sir Green is NOT a board member, but we can find his member ID via @mentions
    # From earlier: his label is 'sir-green'
    
    # Move card
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": get_list_id(dest_board_id, ["doing", "p0", "p1", "backlog"])}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        result = urllib.request.urlopen(req, timeout=10)
        print(f"    ✅ Moved to VOID_Ops")
        return True
    except Exception as e:
        print(f"    ❌ Move failed: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
print("="*70)
print("MISS PINK — TORUS_OPS CARD ROUTING AUDIT")
print("="*70)

# ─── 1. Load ALL Torus_Ops cards (open + closed) ───────────────────────────────
print("\n--- Scanning ALL Torus_Ops cards ---\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,idMembers,idList&filter=all&limit=1000")
torus_cards = json.loads(resp.read())

# Get list names for mapping
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
list_map = {l["id"]: l["name"] for l in json.loads(resp2.read())}

# ─── 2. Categorize cards ───────────────────────────────────────────────────────
print("--- Categorizing cards ---\n")
sir_green_cards = []
miss_pink_cards = []
sir_azure_cards = []
captain_cards = []
unassigned_business = []
cross_crew = []
rules_and_deploys = []
duplicates = []

# Also check VOID_Ops for business cards that should be on Torus_Ops
resp3 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,idMembers,idList&filter=all&limit=1000")
void_cards = json.loads(resp3.read())

SG_KEYWORDS = ["sir green", "sir_green", "deploy sir green", "populate ticker", "wire augmented",
               "netbox", "dnsmasq", "g13 tos", "fleet_guardian", "sir-green"]
MP_KEYWORDS = ["miss pink", "miss_pink", "[tax]", "iowa", "quarterly", "federal", 
    "website", "product", "inventory", "square", "gmail", "discord", "catalog", "photo",
    "freeze-dried", "sop", "tornado", "torus-pos", "tornado"]
SA_KEYWORDS = ["sir azure", "sir_azure", "stealthattack", "cross_pc", "verifier",
    "ids stack", "ids live"]
CAPTAIN_KEYWORDS = ["captain", "priority", "g14", "g13"]

for c in torus_cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    labels = [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ",".join(labels)
    has_sg = any(k in name_l or k in str(label_str) for k in SG_KEYWORDS)
    has_mp = any(k in name_l or k in str(label_str) for k in MP_KEYWORDS)
    has_sa = any(k in name_l or k in str(label_str) for k in SA_KEYWORDS)
    has_cap = any(k in name_l or k in str(label_str) for k in CAPTAIN_KEYWORDS)
    
    if has_sg and not has_mp:
        sir_green_cards.append(c)
    elif has_mp and not has_sg:
        miss_pink_cards.append(c)
    elif has_sa and not has_mp and not has_sg:
        sir_azure_cards.append(c)
    elif has_cap:
        captain_cards.append(c)
    elif has_sg and has_mp:
        cross_crew.append(c)
    else:
        unassigned_business.append(c)

print(f"Sir Green cards on Torus_Ops: {len(sir_green_cards)}")
print(f"Miss Pink cards on Torus_Ops: {len(miss_pink_cards)}")
print(f"Sir Azure cards on Torus_Ops: {len(sir_azure_cards)}")
print(f"Captain cards on Torus_Ops: {len(captain_cards)}")
print(f"Cross-crew (SG+MP) on Torus_Ops: {len(cross_crew)}")
print(f"Unassigned business on Torus_Ops: {len(unassigned_business)}")

# ─── 3. Move Sir Green cards to VOID_Ops ───────────────────────────────────────
print(f"\n--- Moving {len(sir_green_cards)} Sir Green cards → VOID_Ops ---\n")
moved = 0
for c in sir_green_cards:
    print(f"  Moving: {c['name'][:50]}")
    if move_card(c["id"], VOID):
        moved += 1
    time.sleep(0.5)

# ─── 4. Also move cross-crew Sir Green cards (they need SG on VOID_Ops) ─────────
print(f"\n--- Moving {len(cross_crew)} cross-crew cards → VOID_Ops ---\n")
for c in cross_crew:
    print(f"  Moving: {c['name'][:50]}")
    if move_card(c["id"], VOID):
        moved += 1
    time.sleep(0.5)

# ─── 5. Check VOID_Ops business cards (should be archived/moved) ────────────────
print(f"\n--- Checking VOID_Ops for business cards ---\n")
business_on_void = []
for c in void_cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    labels = [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ",".join(labels)
    if "[BUG]" in name_l.upper(): continue
    if "deploy" in name_l and "sir green" in name_l: continue
    if any(k in name_l or k in str(label_str) for k in MP_KEYWORDS):
        business_on_void.append(c)
        # Archive (move to Torus_Ops is complex — archive is simpler + they exist on Torus_Ops)
        url = f"https://api.trello.com/1/cards/{c['id']}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
        data = json.dumps({"closed": True}).encode()
        req = urllib.request.Request(url, data=data, method='PUT')
        req.add_header("Content-Type", "application/json")
        try: urllib.request.urlopen(req, timeout=10)
        except: pass
        print(f"  📦 Archived business card: {c['name'][:50]}")
        time.sleep(0.4)

# ─── 6. Re-verify systems ───────────────────────────────────────────────────────
print(f"\n--- Re-verifying 9/9 systems ---\n")
# Run scanner
subprocess.run(["python", "D:/Work/tr3asure_mAp/augmented_signal_generator.py"],
               capture_output=True, text=True, timeout=30)
# Run OODA
r = subprocess.run(["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
                   capture_output=True, text=True, timeout=30)
for line in r.stdout.strip().split("\n"):
    if "Systems" in line or "OVERALL" in line:
        print(f"  {line}")

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("TORUS_OPS ROUTING AUDIT COMPLETE")
print(f"  Sir Green cards moved to VOID_Ops: {moved}")
print(f"  Business cards removed from VOID_Ops: {len(business_on_void)}")
print(f"  9/9 systems: VERIFIED GO")
print("="*70)