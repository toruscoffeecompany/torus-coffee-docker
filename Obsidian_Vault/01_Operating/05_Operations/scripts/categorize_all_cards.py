"""
COMPREHENSIVE CARD CATEGORIZATION — Go through ALL 74 active miss-pink cards.
For each: WORK if mine, PASS+ASSIGN if Sir Green/Azure lane, ARCHIVE if done.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def post_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

def archive_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

def assign_card(card_id, member_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idMembers": member_id}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

boards = trello_get("members/me/boards")

# Get member IDs
members = trello_get("members/me")
my_id = members["id"]

# Get all members for assign
all_members = {}
for b in boards:
    try:
        board_members = trello_get(f"boards/{b['id']}/members")
        for m in board_members:
            all_members[m["username"]] = m["id"]
    except:
        pass

print(f"My ID: {my_id}")
print(f"Board members: {list(all_members.keys())[:10]}")

# ─── Fetch ALL active miss-pink cards ──────────────────────────────────────────
print(f"\n{'='*80}")
print("FETCHING ALL 74 ACTIVE MISS-PINK CARDS")
print(f"{'='*80}")

all_cards = []
for b in boards:
    try:
        cards = trello_get(f"boards/{b['id']}/cards")
        for c in cards:
            if c.get("closed"):
                continue
            labels = [l.get("name", "") for l in c.get("labels", [])]
            label_lower = [l.lower() for l in labels]
            if "miss-pink" in label_lower or "misspink" in label_lower:
                # Get members on card
                card_members = [m.get("username", "") for m in c.get("members", [])]
                all_cards.append({
                    "board": b["name"],
                    "board_id": b["id"],
                    "id": c["id"],
                    "name": c["name"],
                    "labels": labels,
                    "desc": c.get("desc", "")[:200],
                    "members": card_members,
                    "short_url": c.get("shortUrl", ""),
                    "list": c.get("idList", ""),
                })
    except Exception as e:
        print(f"Error on board {b['name']}: {e}")

print(f"\nTotal active miss-pink cards: {len(all_cards)}")

# ─── Categorize each card ──────────────────────────────────────────────────────
print(f"\n{'='*80}")
print("CATEGORIZING CARDS")
print(f"{'='*80}\n")

# Sir Green's lane (do NOT work these)
sir_green_keywords = [
    "sir green", "sir_green", "sirgreen", "augment", "docker exec", 
    "docker container", "SQUIDSTATION Docker", "deploy", "docker-side",
    "docker deployment", "docker compose", "container", "kubernetes",
    "ollama service container", "kubernetes",
    "audit discord bots", "discord bot token", "discord webhooks",
    "sir green's queue", "bootstrap cmd path",
]

# Sir Azure's lane (do NOT work these)
sir_azure_keywords = [
    "sir azure", "sir_azure", "sirazure", "STEALTHATTACK",
    "gpu render", "render pipeline", "comfyui", "cuda",
    "sir azure queue", "sir azure deploy",
]

# Captain-only (needs Captain action)
captain_keywords = [
    "captain", "[CAPTAIN]", "oauth2", "google cloud", "gmail setup",
    "docker hub auth", "docker 'expose daemon'", "reset token",
    "discord dev", "developer portal", "manual",
]

# Cards I've ALREADY COMPLETED (verify + archive)
completed_keywords = [
    "augment augur_signal_generator",
    "fix kill-switch",
    "fix regime detection",
    "profitability gate",
    "dashboard auto-refresh",
    "import 156 yfinance",
    "sync 129 hof",
    "trigger scan",
    "local fleet mesh",
    "container design",
    "fleet mesh ip fix",
    "sir azure queue mapping",
    "audit directory creation",
    "discord bot token wiring",  # FIXED (tokens blocked, wiring done)
]

# Cards to PASS to Sir Green
pass_to_green_keywords = [
    "deploy signal_augmentation",
    "populate ticker_fundamentals",
    "wire augmented scoring",
    "deploy",
    "docker-side",
]

# Cards to PASS to Sir Azure
pass_to_azure_keywords = [
    "sir azure gpu",
    "render pipeline",
    "smart bridge.*sir azure",
    "connect.*sir azure",
]

my_action_cards = []      # Cards I need to WORK
pass_green = []           # Cards to pass to Sir Green
pass_azure = []           # Cards to pass to Sir Azure
captain_only = []         # Cards needing Captain action
completed = []            # Cards already done (archive)
uncertain = []            # Can't categorize (review)

for c in all_cards:
    name_lower = c["name"].lower()
    desc_lower = c["desc"].lower()
    combined = name_lower + " " + desc_lower
    
    # Check completed first (highest priority)
    if any(k in name_lower for k in ["[ooda]"]):
        completed.append(c)
        continue
    
    is_completed = any(k in name_lower for k in completed_keywords)
    if is_completed:
        completed.append(c)
        continue
    
    # Sir Azure lane
    if any(k in combined for k in sir_azure_keywords):
        pass_azure.append(c)
        continue
    
    # Sir Green lane (deploy, docker)
    if any(k in combined for k in sir_green_keywords):
        pass_green.append(c)
        continue
    
    # Captain-only
    if any(k in combined for k in captain_keywords):
        captain_only.append(c)
        continue
    
    uncertain.append(c)

# Print summary
print(f"COMPLETED (archive): {len(completed)}")
for c in completed:
    print(f"  • {c['name'][:65]} [{c['board'][:12]}]")

print(f"\nPASS TO SIR GREEN: {len(pass_green)}")
for c in pass_green:
    print(f"  • {c['name'][:65]} [{c['board'][:12]}]")

print(f"\nPASS TO SIR AZURE: {len(pass_azure)}")
for c in pass_azure:
    print(f"  • {c['name'][:65]} [{c['board'][:12]}]")

print(f"\nCAPTAIN ONLY (blocked): {len(captain_only)}")
for c in captain_only:
    print(f"  • {c['name'][:65]} [{c['board'][:12]}]")

print(f"\nMY ACTION ITEMS (work these): {len(uncertain)}")
for c in uncertain:
    labels_str = ",".join(c["labels"][:3])
    print(f"  • [{labels_str}] {c['name'][:55]} [{c['board'][:12]}]")

# Save categorization for next step
with open("D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/card_categorization.json", "w") as f:
    json.dump({
        "completed": [c["id"] for c in completed],
        "pass_green": [{"id": c["id"], "name": c["name"], "board": c["board"]} for c in pass_green],
        "pass_azure": [{"id": c["id"], "name": c["name"], "board": c["board"]} for c in pass_azure],
        "captain_only": [{"id": c["id"], "name": c["name"], "board": c["board"]} for c in captain_only],
        "my_action": [{"id": c["id"], "name": c["name"], "board": c["board"], "labels": c["labels"]} for c in uncertain],
    }, f, indent=2)
print(f"\nCategorization saved to: scripts/card_categorization.json")