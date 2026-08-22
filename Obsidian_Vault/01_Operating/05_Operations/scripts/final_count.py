"""Final board count."""
import json, urllib.request
TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=closed,labels,name")
cards = json.loads(resp.read())
active = [c for c in cards if not c.get("closed", True)]
archived = [c for c in cards if c.get("closed", True)]

def is_mp(c):
    for l in c.get("labels", []):
        name = l.get("name", "") if isinstance(l, dict) else str(l)
        if name.lower() == "miss-pink":
            return True
    return False

mp_active = [c for c in active if is_mp(c)]
mp_archived = [c for c in archived if is_mp(c)]

print("=== TORUS_OPS BOARD FINAL STATUS ===")
print(f"Active miss-pink: {len(mp_active)}")
print(f"Archived miss-pink: {len(mp_archived)}")
print(f"Total: {len(mp_active) + len(mp_archived)}")
print()
print("Remaining active:")
for c in sorted(mp_active, key=lambda x: x["name"]):
    print(f"  • {c['name']}")