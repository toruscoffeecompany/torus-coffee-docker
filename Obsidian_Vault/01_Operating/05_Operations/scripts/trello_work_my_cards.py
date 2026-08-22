"""Work the Trello cards assigned to miss-pink. Focus on P0/P1 items."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def trello_post(path, body):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())

# Get my member info first
me = trello_get("members/me")
my_id = me.get("id", "")
my_name = me.get("fullName", "?")
print(f"Me: {my_name} | ID: {my_id[:8]}...")

# Get cards on board (without members filter — use simpler params)
base_url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
cards_url = f"{base_url}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
resp = urllib.request.urlopen(cards_url, timeout=30)
cards = json.loads(resp.read())
print(f"Total cards on board: {len(cards)}")

# Get list names
lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
lists_resp = urllib.request.urlopen(lists_url, timeout=30)
lists_data = json.loads(lists_resp.read())
list_map = {l["id"]: l["name"] for l in lists_data}

# Get member info for each card
# We need to fetch cards with members separately
members_url = f"{base_url}?key={TRELLO_KEY}&token={TRELLO_TOKEN}&members=true"
mem_resp = urllib.request.urlopen(members_url, timeout=30)
mem_cards = json.loads(mem_resp.read())

# Build a lookup of card_id -> members
card_members = {}
for c in mem_cards:
    card_members[c["id"]] = c.get("members", [])

# Now find my cards
my_cards = []
for c in cards:
    members = card_members.get(c["id"], [])
    for m in members:
        if m.get("id") == my_id:
            my_cards.append(c)
            break

print(f"Cards assigned to me: {len(my_cards)}")
print()

# Categorize by priority
p0_cards = []
p1_cards = []
p2_cards = []

for c in my_cards:
    labels = [l.get("name", "") for l in c.get("labels", [])]
    list_name = list_map.get(c.get("idList", ""), "?")
    due = c.get("due", "No due date")
    
    card_info = {
        "name": c.get("name", ""),
        "labels": labels,
        "list": list_name,
        "due": due[:10] if due else "None",
        "url": c.get("url", ""),
        "id": c.get("id", "")
    }
    
    if "P0" in labels:
        p0_cards.append(card_info)
    elif "P1" in labels:
        p1_cards.append(card_info)
    elif "P2" in labels:
        p2_cards.append(card_info)

print("="*70)
print(f"P0 CARDS — CRITICAL / DO NOW ({len(p0_cards)})")
print("="*70)
for c in p0_cards:
    label_str = ",".join([l for l in c["labels"] if l][:4])
    print(f"  [{label_str}] {c['name'][:65]}")
    print(f"  List: {c['list']} | Due: {c['due']}")
    print()

print("="*70)
print(f"P1 CARDS — HIGH / DOING NOW ({len(p1_cards)})")
print("="*70)
for c in p1_cards:
    label_str = ",".join([l for l in c["labels"] if l][:4])
    print(f"  [{label_str}] {c['name'][:65]}")
    print(f"  List: {c['list']} | Due: {c['due']}")
    print()

print("="*70)
print(f"P2 CARDS — MEDIUM / THIS WEEK ({len(p2_cards)})")
print("="*70)
for c in p2_cards:
    label_str = ",".join([l for l in c["labels"] if l][:4])
    print(f"  [{label_str}] {c['name'][:60]} | Due: {c['due']}")

# Focus on Augur trading related
print("\n" + "="*70)
print("FOCUS: Augur Trading System Related Cards")
print("="*70)
focus_keywords = ["augur", "regime", "kill", "import", "hof", "scan", "paper trade", 
                  "alapca", "alpaca", "dashboard", "restart", "trading", "scan", "data"]
all_p01 = p0_cards + p1_cards
for c in all_p01:
    name_lower = c["name"].lower()
    if any(kw in name_lower for kw in focus_keywords):
        status = "DONE" if "Done" in c["list"] else "TODO"
        print(f"  [{status:4s}] [{','.join([l for l in c['labels'] if l][:4])}] {c['name'][:55]}")
        print(f"    URL: {c['url']}")
        print(f"    List: {c['list']}")