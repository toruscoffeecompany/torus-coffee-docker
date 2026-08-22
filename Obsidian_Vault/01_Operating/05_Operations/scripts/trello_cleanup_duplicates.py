"""Delete duplicate Trello cards (keep only the first augmentation card)."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def trello_delete(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    req = urllib.request.Request(url, method='DELETE')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read()
    except Exception as e:
        return str(e)

# Find all augmentation cards
cards = trello_get(f"boards/6a70a3157d0db4214ac3f9a3/cards")
aug_cards = [c for c in cards if "augment" in c.get("name", "").lower() and "signal_generator" in c.get("name", "").lower()]

print(f"Found {len(aug_cards)} augmentation cards:")
for c in aug_cards:
    print(f"  {c['id']}: {c['name'][:60]} (created: {c.get('date','?')})")

# Keep the first (earliest created), delete duplicates
if len(aug_cards) > 1:
    # Sort by creation date
    aug_cards.sort(key=lambda x: x.get('date', ''))
    keep = aug_cards[0]
    for c in aug_cards[1:]:
        result = trello_delete(f"cards/{c['id']}")
        print(f"  🗑️ Deleted duplicate: {c['name'][:50]} — {result}")
    print(f"\n  ✅ Kept: {keep['name']}")
else:
    print(f"  ✅ Only 1 card, no cleanup needed")

print("\n=== DONE ===")