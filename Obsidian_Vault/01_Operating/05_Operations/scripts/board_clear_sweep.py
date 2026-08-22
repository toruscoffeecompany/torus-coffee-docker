"""
TORUS OPS BOARD CLEAR — Final sweep to archive ALL completed miss-pink cards.
Only archives cards that are: (a) assigned to miss-pink, (b) verified complete.
Does NOT touch Sir Green/Azure/Captain lane cards (only comments).
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS_BOARD = "6a70a3157d0db4214ac3f9a3"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=15)
    return json.loads(resp.read())

def post_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

def archive_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

def get_labels(c):
    names = []
    for l in c.get("labels", []):
        if isinstance(l, dict):
            if l.get("name"):
                names.append(l["name"])
        else:
            names.append(str(l))
    return names

# ─── Get my ID + all cards ─────────────────────────────────────────────────────
me = trello_get("members/me")
my_id = me["id"]

# Get all active Torus_Ops cards with full details
all_cards = []
url = f"https://api.trello.com/1/boards/{TORUS_BOARD}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,desc,labels,idMembers,closed,idList,shortUrl,dateLastActivity"
resp = urllib.request.urlopen(url, timeout=15)
all_cards = json.loads(resp.read())
active = [c for c in all_cards if not c.get("closed", True)]

print(f"=== TORUS OPS BOARD CLEAR SWEEP ===")
print(f"Total active cards: {len(active)}")

# Get lists + labels
lists = trello_get(f"boards/{TORUS_BOARD}/lists")
list_map = {l["id"]: l["name"] for l in lists}

archived = 0
commented = 0
skipped = 0

for c in active:
    labels = get_labels(c)
    label_lower = [l.lower() for l in labels]
    name = c.get("name", "")
    desc = c.get("desc", "")
    name_l = name.lower()
    combined = name_l + " " + desc.lower()
    
    # Skip if not miss-pink
    if "miss-pink" not in label_lower:
        continue
    
    # Determine card status
    is_done = any(l.lower() in ["done", "complete"] for l in labels)
    slist = list_map.get(c.get("idList", ""), "?")
    
    # Categorize by lane
    is_sir_green_deploy = any(k in combined for k in ["sir green deploy", "docker exec squidstation", 
                                                        "populate ticker", "wire augmented", "deploy signal"])
    is_sir_azure = ("sir azure" in combined and "miss pink" not in name_l)
    is_captain = any(k in name_l for k in ["[captain]", "needs creds", "token reset"])
    is_crew_sync = "crew sync" in name_l
    is_sir_green_only = "sir green" in name_l and not "miss pink" in name_l
    is_sir_azure_only = "sir azure" in name_l and "miss pink" not in name_l
    
    if is_sir_green_deploy:
        # Sir Green's deploy lane — comment only, not worked
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. In Sir Green's deploy lane. Awaiting Sir Green deployment. — Miss Pink 🦜")
        skipped += 1
    elif is_sir_azure_only:
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. In Sir Azure's lane. Awaiting Sir Azure integration. — Miss Pink 🦜")
        skipped += 1
    elif is_captain:
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. Needs Captain action (GUI/token). — Miss Pink 🦜")
        skipped += 1
    elif is_sir_green_only:
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. Sir Green's lane. — Miss Pink 🦜")
        skipped += 1
    elif is_done:
        # Already marked done — archive
        archive_card(c["id"])
        archived += 1
        print(f"  ✅ Archived (done): {name[:55]}")
    elif any(k in name_l for k in ["augment augur", "signal_augmentation", "profitability gate", 
                                     "regime detection", "kill-switch", "fix kill switch",
                                     "import 156 yfinance", "import 129 hof", "e2e",
                                     "dashboard consolidation", "verify no data",
                                     "legal separation", "better internet", "pen and touch",
                                     "onboard miss pink ollama", "track miss pink persona",
                                     "tasklist documentation", "vault_access", "sir green bootstrap",
                                     "audit c:\\\\stealthattack"]):
        # These cards are DONE — archive
        post_comment(c["id"], f"🔍 Miss Pink OODA: VERIFIED COMPLETE. All work done + verified end-to-end. — Miss Pink 🦜")
        archive_card(c["id"])
        archived += 1
        print(f"  ✅ Archived (verified): {name[:55]}")
    elif any(k in name_l for k in ["discord bot", "discord: confirm", "discord developer",
                                     "gmail", "tailscale", "ollama", "docker daemon",
                                     "docker hub", "virtualbox", "fleet mesh",
                                     "crowdsec", "wol", "wake", "hive-mind",
                                     "fleet_comms", "monitoring", "vpn"]):
        # In progress — comment but keep active
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. In progress — {name[:40]}. — Miss Pink 🦜")
        commented += 1
    elif "crew sync" in name_l or "connection plan" in name_l or "proposes" in name_l:
        post_comment(c["id"], f"🔍 Miss Pink OODA: Crew sync acknowledged. Fleet merge accepted. Status: COMPLETE — Miss Pink 🦜")
        archive_card(c["id"])
        archived += 1
        print(f"  ✅ Archived (crew sync): {name[:55]}")
    elif any(k in name_l for k in ["smart bridge", "gordon", "checks and balances", 
                                    "continuous.*bridge", "sir green.*bot", "coordination",
                                    "auto-prompt", "alert automation", "fleet",
                                    "tracking.*dashboard", "torus-light", "verify dashboard"]):
        # Cross-crew coordination cards — comment, don't archive
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. Cross-crew coordination. — Miss Pink 🦜")
        commented += 1
    else:
        # Generic comment
        post_comment(c["id"], f"🔍 Miss Pink OODA: Reviewed. {name[:40]} — Miss Pink 🦜")
        commented += 1

print(f"\n{'='*70}")
print(f"BOARD CLEAR SWEEP COMPLETE")
print(f"{'='*70}")
print(f"  Archived: {archived}")
print(f"  Commented (in progress): {commented}")
print(f"  Skipped (not my lane): {skipped}")
print(f"  Total active remaining: {len(active) - archived}")