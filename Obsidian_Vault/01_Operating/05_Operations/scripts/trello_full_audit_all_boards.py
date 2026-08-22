"""
FULL TRELLO AUDIT — Scan ALL boards for cards labeled miss-pink + investigate
why 'Audit Discord bots' card keeps appearing in inbox.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

# ─── 1. Get ALL boards the user has access to ────────────────────────────────
print("=== ALL TRELLO BOARDS ===")
boards = trello_get("members/me/boards")
for b in boards:
    print(f"  {b['name']} ({b['id']}) — {b.get('opts', {}).get('permission', '?')}")

# ─── 2. For each board, find miss-pink labels + cards ─────────────────────────
print("\n=== SCANNING ALL BOARDS FOR miss-pink CARDS ===")
all_my_cards = []
for b in boards:
    bid = b["id"]
    bname = b["name"]
    try:
        cards = trello_get(f"boards/{bid}/cards")
        labels = trello_get(f"boards/{bid}/labels")
        mp_label = None
        for l in labels:
            if l["name"].lower() in ["miss-pink", "misspink", "miss_pink", "miss pink"]:
                mp_label = l["id"]
        
        for c in cards:
            card_labels = [l.get("id") for l in c.get("labels", [])]
            if mp_label and mp_label in card_labels:
                label_names = [l.get("name", "") for l in c.get("labels", [])]
                all_my_cards.append({
                    "board": bname,
                    "board_id": bid,
                    "id": c["id"],
                    "name": c["name"],
                    "labels": label_names,
                    "list": c.get("idList", ""),
                    "desc": c.get("desc", "")[:200],
                    "short_url": c.get("shortUrl", ""),
                })
                print(f"\n  [{bname}] {c['name']}")
                print(f"    Labels: {label_names}")
                print(f"    URL: {c.get('shortUrl', '?')}")
                print(f"    ID: {c['id']}")
                print(f"    List: {c.get('idList', '?')}")
                if c.get("desc"):
                    print(f"    Desc: {c['desc'][:200]}")
    except Exception as e:
        print(f"  {bname}: ERROR - {e}")

print(f"\n{'='*60}")
print(f"TOTAL miss-pink cards across ALL boards: {len(all_my_cards)}")
print(f"{'='*60}")

# ─── 3. Investigate the Discord audit card ─────────────────────────────────────
print("\n=== INVESTIGATING: Discord audit card repetition ===")
discord_cards = [c for c in all_my_cards if "discord" in c["name"].lower() or "discord" in c.get("desc", "").lower()]
if discord_cards:
    print(f"Found {len(discord_cards)} Discord-related cards:")
    for c in discord_cards:
        print(f"\n  Board: {c['board']}")
        print(f"  Name: {c['name']}")
        print(f"  URL: {c['short_url']}")
        print(f"  Card ID: {c['id']}")
        print(f"  Desc: {c['desc'][:300]}")
else:
    print("No Discord cards found with miss-pink label!")

# ─── 4. Check for duplicate cards ──────────────────────────────────────────────
print("\n=== DUPLICATE DETECTION ===")
card_names = [c["name"] for c in all_my_cards]
from collections import Counter
name_counts = Counter(card_names)
for name, count in name_counts.items():
    if count > 1:
        print(f"  ⚠️ DUPLICATE: '{name}' appears {count} times")
        for c in all_my_cards:
            if c["name"] == name:
                print(f"    - {c['board']}: {c['short_url']}")

print(f"\n=== DONE ===")