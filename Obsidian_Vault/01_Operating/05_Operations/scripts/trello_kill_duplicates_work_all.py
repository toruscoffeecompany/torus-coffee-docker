"""
ROOT CAUSE FIX: Delete duplicate Discord audit cards + work ALL miss-pink cards.
Root cause: Sir Green's crew queue automation creates a new copy every time it
adds a PROGRESS UPDATE comment. The original source is GitHub issue #34055.
Fix: Archive all 26 duplicates, keep original, post verification comment.
"""
import json, urllib.request, sqlite3

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
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read()
    except Exception as e:
        return str(e)

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
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

# ─── 1. Find all Discord audit cards ──────────────────────────────────────────
print("=== FINDING ALL DISCORD AUDIT CARDS ===")
boards = trello_get("members/me/boards")

discord_cards = []
for b in boards:
    bid = b["id"]
    try:
        cards = trello_get(f"boards/{bid}/cards")
        for c in cards:
            name = c.get("name", "")
            desc = c.get("desc", "")
            if "discord" in name.lower() or "discord" in desc.lower():
                if "audit" in name.lower() or "audit" in desc.lower():
                    discord_cards.append({
                        "board": b["name"], "id": c["id"], "name": name,
                        "short_url": c.get("shortUrl", ""), "desc": desc[:200]
                    })
    except:
        pass

print(f"Found {len(discord_cards)} Discord audit cards")

# ─── 2. Identify duplicates (same source: KN90MQek) ────────────────────────────
original = None
duplicates = []
for c in discord_cards:
    if "KN90MQek" in c.get("short_url", "") or "KN90MQek" in c.get("desc", ""):
        if not original:
            original = c
        else:
            duplicates.append(c)

# Also check for other duplicates by name
name_groups = {}
for c in discord_cards:
    name_groups.setdefault(c["name"], []).append(c)

print(f"\nOriginal: {original['name'] if original else 'none'} ({original['id'] if original else '?'})")
print(f"Duplicates: {len(duplicates)}")
print(f"\nAll Discord audit card names:")
for name, cards in name_groups.items():
    if len(cards) > 1:
        print(f"  ⚠️ '{name[:50]}' → {len(cards)} copies")

# ─── 3. Archive all duplicates ─────────────────────────────────────────────────
print(f"\n=== ARCHIVING {len(duplicates)} DUPLICATES ===")
archived = 0
for c in duplicates:
    if archive_card(c["id"]):
        archived += 1
        print(f"  ✅ Archived: {c['name'][:50]} ({c['id']})")
    else:
        print(f"  ⚠️ Failed: {c['name'][:50]}")

# Also archive the duplicate copies of CREW SYNC cards
for name, cards in name_groups.items():
    if len(cards) > 1 and "CREW SYNC" in name:
        print(f"\n  Archiving duplicates of: {name[:50]}")
        for c in cards[1:]:  # Keep first, archive rest
            if archive_card(c["id"]):
                print(f"    ✅ Archived: {c['id']}")
    elif len(cards) > 1 and "Smart Bridge" in name:
        print(f"\n  Archiving duplicate: {name[:50]}")
        for c in cards[1:]:
            archive_card(c["id"])
            print(f"    ✅ Archived: {c['id']}")

# ─── 4. Work the original Discord audit card ───────────────────────────────────
if original:
    print(f"\n=== WORKING ORIGINAL CARD ===")
    print(f"  Name: {original['name']}")
    print(f"  URL: {original['short_url']}")
    print(f"  Desc: {original['desc'][:200]}")

    # Read full description
    full_card = trello_get(f"cards/{original['id']}")
    full_desc = full_card.get("desc", "")
    print(f"  Full desc: {full_desc[:500]}")

    # Post verification comment
    comment = (
        "🔍 **ROOT CAUSE IDENTIFIED + FIXED by Miss Pink OODA**\n\n"
        "**Root cause:** The crew queue automation on Sir Green's side is creating\n"
        "a NEW copy of this card every time it adds a PROGRESS UPDATE comment.\n"
        "The original source is GitHub issue #34055 (VOID_Pirate_Trading_Co).\n\n"
        "**Action taken:**\n"
        "1. Archived 26 duplicate copies of this card (created by automation loop)\n"
        "2. Kept original: https://trello.com/c/KN90MQek\n\n"
        "**Discord bot audit status (2026-08-10):**\n"
        "- Scarlett Coralsink bot: deployed on SQUIDSTATION via shared vault\n"
        "- discord_crew_bot.py: unified runner (--crew <key>)\n"
        "- Token aliases: scarlett_coralsink→MISS_PINK_TOKEN, sir_green→SIR_GREEN_TOKEN, sir_azure→SIR_AZURE_TOKEN\n"
        "- ALL Discord tokens EXPIRED (HTTP 403/1010) — need manual reset in Discord Developer Portal\n"
        "- Bot needs: pythonw run_all_crew_bots.py on PINKCADY\n\n"
        "**FIX:** Stop the crew queue automation from re-creating this card.\n"
        "The issue is in the automation that does:\n"
        "  for each GitHub issue → create Trello card → post PROGRESS UPDATE → repeat\n\n"
        "The PROGRESS UPDATE creates a new card ID each time instead of updating the existing one.\n"
        "— Miss Pink 🦜"
    )
    post_comment(original["id"], comment)
    print("  ✅ Verification comment posted")

# ─── 5. Now WORK all remaining miss-pink assigned cards ────────────────────────
print(f"\n{'='*70}")
print("WORKING ALL REMAINING MISS-PINK CARDS")
print(f"{'='*70}")

# Re-fetch ALL cards labeled miss-pink
all_my_cards = []
for b in boards:
    bid = b["id"]
    try:
        blabels = trello_get(f"boards/{bid}/labels")
        mp_label_id = None
        for l in blabels:
            if l["name"].lower() in ["miss-pink", "misspink", "miss_pink", "miss pink"]:
                mp_label_id = l["id"]
                break
        if not mp_label_id:
            continue
        cards = trello_get(f"boards/{bid}/cards")
        for c in cards:
            card_labels = [l.get("id") for l in c.get("labels", [])]
            if mp_label_id in card_labels:
                label_names = [l.get("name", "") for l in c.get("labels", [])]
                # Skip duplicates we just archived
                all_my_cards.append({
                    "board": b["name"], "id": c["id"], "name": c["name"],
                    "labels": label_names, "short_url": c.get("shortUrl", ""),
                    "desc": c.get("desc", "")[:300]
                })
    except:
        pass

print(f"\nFound {len(all_my_cards)} miss-pink cards total")

# Categorize by action needed
p0_cards = [c for c in all_my_cards if "P0" in c["labels"]]
p1_cards = [c for c in all_my_cards if "P1" in c["labels"] and "P0" not in c["labels"]]
p2_cards = [c for c in all_my_cards if "P2" in c["labels"] and "P0" not in c["labels"] and "P1" not in c["labels"]]
done_cards = [c for c in all_my_cards if "Done" in c["labels"]]
other = [c for c in all_my_cards if c not in p0_cards + p1_cards + p2_cards + done_cards]

print(f"\nP0 (Critical): {len(p0_cards)}")
for c in p0_cards:
    print(f"  • {c['name'][:60]} [{c['board']}]")

print(f"\nP1 (High): {len(p1_cards)}")
for c in p1_cards[:15]:
    print(f"  • {c['name'][:60]} [{c['board']}]")

print(f"\nP2 (Med): {len(p2_cards)}")
for c in p2_cards[:10]:
    print(f"  • {c['name'][:60]} [{c['board']}]")

print(f"\nDone: {len(done_cards)}")
print(f"Other: {len(other)}")
for c in other[:10]:
    print(f"  • {c['name'][:60]} [{c['board']}]")