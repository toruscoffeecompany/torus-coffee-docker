"""
FINAL CLEANUP: Archive all verified/complete miss-pink OODA cards + remaining duplicates.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

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

def get_card(card_id):
    try:
        return trello_get(f"cards/{card_id}?fields=name,desc,closed,labels,list")
    except:
        return None

# ─── 1. Archive the 7 OODA cards I created + verified ───────────────────────────
print("=== ARCHIVING VERIFIED OODA CARDS ===")
ooda_card_ids = [
    "6a7a6ab3d37cdf3d67e5064b",  # Profitability gate runner
    "6a7a6ab3504235186b010fe1",  # Dashboard auto-refresh
    "6a7a6ab4d8dd410bcd91dfe6",  # Import 156 yfinance CSVs
    "6a7a6ab5f8fe09edf022eaf4",  # Sync 129 HOF genome exports
    "6a7a6ab586b67f8941df8e5d",  # Fix kill-switch state mismatch
    "6a7a6ab63e0febf3fba5d55f",  # Fix regime detection
    "6a7a6ab7009194fec0e117b9",  # Trigger scan → verify first paper trade
]

archived = 0
for cid in ooda_card_ids:
    card = get_card(cid)
    if card and not card.get("closed"):
        if archive_card(cid):
            archived += 1
            print(f"  ✅ Archived: {card['name'][:55]}")
    elif card and card.get("closed"):
        print(f"  📁 Already archived: {card['name'][:55]}")
    else:
        print(f"  ⚠️ Not found: {cid}")

print(f"\nOODA cards archived: {archived}")

# ─── 2. Archive other verified/duplicate cards ─────────────────────────────────
print(f"\n=== ARCHIVING COMPLETED/DUPLICATE CARDS ===")
completed_cards = [
    "6a726c7cf694311bd8cd5a82",  # Local fleet mesh (marked Done)
    "6a726c7cbe926cbff9bbb55c",  # Container design (marked Done)
]
for cid in completed_cards:
    card = get_card(cid)
    if card and not card.get("closed"):
        if archive_card(cid):
            print(f"  ✅ Archived: {card['name'][:55]}")
    elif card and card.get("closed"):
        print(f"  📁 Already archived: {card['name'][:55]}")

# ─── 3. Final count of remaining active miss-pink cards ─────────────────────────
print(f"\n{'='*60}")
print("FINAL COUNT: Remaining active miss-pink cards")
print(f"{'='*60}")

boards = trello_get("members/me/boards")
total_active = 0
for b in boards:
    try:
        cards = trello_get(f"boards/{b['id']}/cards")
        mp_cards = [c for c in cards if not c.get("closed") and 
                   any(l.get("name", "").lower() in ["miss-pink", "misspink", "miss_pink", "miss pink"] 
                       for l in c.get("labels", []))]
        if mp_cards:
            print(f"\n  {b['name']}: {len(mp_cards)} active")
            for c in mp_cards[:5]:
                labels = [l.get("name", "") for l in c.get("labels", [])]
                p = "P0" if "P0" in labels else "P1" if "P1" in labels else "P2" if "P2" in labels else "OTHER"
                print(f"    • [{p}] {c['name'][:55]}")
            if len(mp_cards) > 5:
                print(f"    ... + {len(mp_cards) - 5} more")
            total_active += len(mp_cards)
    except:
        pass

print(f"\nTotal active miss-pink cards: {total_active}")