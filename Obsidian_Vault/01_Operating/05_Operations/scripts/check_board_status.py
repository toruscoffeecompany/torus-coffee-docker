"""
FINAL BOARD STATUS CHECK — count remaining cards on all crew boards.
Then OODA loop to clear them.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

# Known board IDs
BOARDS = {
    "Business_Docs": "5f1e7a7a4e4b442dd4b93756",
    "My_Trello_Board": "5f1e7a7a4e4b442dd4b93757",
    "Torus_Ops": "6a70a3157d0db4214ac3f9a3",
    "VOID_Ops": "6a595669b8f8f99c93392f4f",
    "Website_Rebuild": "5f1e7a7a4e4b442dd4b93758",
}

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=15)
    return json.loads(resp.read())

print("=" * 70)
print("BOARD STATUS CHECK — ALL CREW BOARDS")
print("=" * 70)

for board_name, board_id in BOARDS.items():
    try:
        cards = trello_get(f"boards/{board_id}/cards")
        active = [c for c in cards if not c.get("closed", True)]
        archived = [c for c in cards if c.get("closed", False)]
        print(f"\n  {board_name}:")
        print(f"    Active cards: {len(active)}")
        print(f"    Archived cards: {len(archived)}")
        
        # Show active card titles
        if active:
            print(f"    Active cards:")
            for c in active[:10]:
                print(f"      • {c['name'][:60]}")
            if len(active) > 10:
                print(f"      ... and {len(active) - 10} more")
    except Exception as e:
        print(f"\n  {board_name}: ❌ {e}")

# Check who we are
me = trello_get("members/me")
print(f"\n{'='*70}")
print(f"Miss Pink: {me['fullName']} (ID: {me['id']})")
print(f"{'='*70}")