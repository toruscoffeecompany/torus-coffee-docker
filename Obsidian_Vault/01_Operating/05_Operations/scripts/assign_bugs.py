"""Find Sir Green's Trello member ID + assign the 5 bug cards."""
import json, urllib.request, time

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

# ─── Find Sir Green's member ID ───────────────────────────────────────────────
print("=== Finding Sir Green's Trello member ID ===")
# Method 1: Search for member
url = f"https://api.trello.com/1/members/sirgreen?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
try:
    resp = urllib.request.urlopen(url, timeout=10)
    member = json.loads(resp.read())
    sg_id = member["id"]
    print(f"  ✅ Found: sirgreen → ID: {sg_id}")
    print(f"  Full name: {member.get('fullName','?')}")
    print(f"  Username: {member.get('username','?')}")
except Exception as e:
    print(f"  Try sirgreen: {e}")
    # Try other variations
    for search in ["sir_green", "SirGreen", "sirgreen", "greensquid", "squidstation"]:
        try:
            url2 = f"https://api.trello.com/1/members/{search}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
            resp2 = urllib.request.urlopen(url2, timeout=10)
            member2 = json.loads(resp2.read())
            print(f"  ✅ Found: {search} → ID: {member2['id']}")
            print(f"    Full name: {member2.get('fullName','?')}")
            print(f"    Username: {member2.get('username','?')}")
            sg_id = member2["id"]
            break
        except:
            pass

# ─── Get board members to find Sir Green ──────────────────────────────────────
print("\n=== Board members on VOID_Ops ===")
board_url = f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/members?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
resp3 = urllib.request.urlopen(board_url, timeout=10)
members = json.loads(resp3.read())
for m in members:
    print(f"  • {m.get('fullName','?')} ({m.get('username','?')}) → ID: {m['id']}")
    if "green" in m.get("username","").lower() or "green" in m.get("fullName","").lower():
        sg_id = m["id"]
        print(f"    ← Sir Green found!")

# ─── Assign bug cards ─────────────────────────────────────────────────────────
bug_card_ids = [
    "6a7b1d62265713de7748a706",
    "6a7b1d67117f4078bfcc5856",
    "6a7b1d6b998f86cd76ba751f",
    "6a7b1d6f103a306bdbe852a0",
    "6a7b1d73a49d1f282613bc71",
]

print(f"\n=== Assigning {len(bug_card_ids)} bug cards to Sir Green (ID: {sg_id}) ===")
for cid in bug_card_ids:
    url = f"https://api.trello.com/1/cards/{cid}/idMembers?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"value": sg_id}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ {cid} → assigned to Sir Green")
    except Exception as e:
        print(f"  ⚠️ {cid} → {e}")
    time.sleep(0.35)