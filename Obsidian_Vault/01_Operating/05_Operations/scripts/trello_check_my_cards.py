"""Fetch Trello Torus Ops board cards assigned to Miss Pink."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"  # Torus_Ops

def trello_get(path, extra_params=""):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}{extra_params}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

# Get my member info
me = trello_get("members/me")
my_id = me.get("id", "")
my_name = me.get("fullName", "?")
print(f"Me: {my_name} | ID: {my_id[:8]}...")
print()

# Get all cards with members + detailed fields
cards = trello_get("boards/" + BOARD_ID + "/cards", "&members=true&memberFields=fullName,username&fields=name,due,labels,idList,status,url")

# Get list names
lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
lists_resp = urllib.request.urlopen(lists_url, timeout=30)
lists_data = json.loads(lists_resp.read())
list_map = {l["id"]: l["name"] for l in lists_data}

# Filter cards assigned to me
my_cards = []
for c in cards:
    members = c.get("members", [])
    for m in members:
        if m.get("id") == my_id:
            my_cards.append(c)
            break

print(f"=== Cards assigned to ME ({my_name}): {len(my_cards)} ===")
for c in my_cards:
    labels = [l.get("name", "") for l in c.get("labels", [])]
    list_name = list_map.get(c.get("idList", ""), "?")
    due = c.get("due", "No due date")
    label_str = ", ".join([l for l in labels if l][:4])
    url = c.get("url", "")

    print(f"\n  [{label_str}] {c['name'][:70]}")
    print(f"    List: {list_name} | Due: {due[:10] if due else 'None'}")
    if url:
        print(f"    URL: {url}")

# Also show P0/P1 cards (priority focus)
print("\n" + "="*60)
print("=== ALL P0/P1 CARDS (priority focus) ===")
print("="*60)
p01_cards = [c for c in cards if any(l.get("name") in ("P0", "P1") for l in c.get("labels", []))]
for c in p01_cards[:20]:
    labels = [l.get("name", "") for l in c.get("labels", [])]
    list_name = list_map.get(c.get("idList", ""), "?")
    is_mine = any(m.get("id") == my_id for m in c.get("members", []))
    marker = " [MINE]" if is_mine else ""
    print(f"  [{','.join([l for l in labels if l][:3])}]{marker} {c['name'][:65]}")
    print(f"    List: {list_name} | Labels: {labels}")