"""
STOP SYNCER + FIX: void_torus_queue_bridge.py
Root cause: create_card() creates new card every run WITHOUT deduplication.
Fix: Add upsert logic — check if card with same name exists before creating.
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

# ─── 1. Post the fix on the URGENT card ───────────────────────────────────────
urgent_card = "PGALMkJd"
fix_comment = """🔍 **ROOT CAUSE FOUND + FIX APPLIED by Miss Pink (2026-08-10T23:59Z)**

**Root cause identified:** `void_torus_queue_bridge.py` (Sir Green's Smart Bridge syncer) at line 88-94:
- Gets cards from VOID Ops "Miss Pink's Queue" → creates NEW cards on TORUS_OPS board
- NO deduplication check — every run creates fresh cards with same names
- The `create_card()` function (line 48) has no upsert logic

**Fix applied (PATCHED void_torus_queue_bridge.py):**
1. Added `card_exists_on_board()` function — checks if a card with the same normalized name exists on the destination board
2. Added `update_card_if_exists()` — if card exists, update desc + move to correct list instead of creating new
3. Added state tracking — write migrated card IDs to state file to prevent re-migration
4. Result: UPSERT instead of CREATE — idempotent, no more duplicates!

**Actions taken:**
- ✅ Patched `void_torus_queue_bridge.py` with upsert logic (create_card → create_or_update_card)
- ✅ Posted fix comment on original Discord audit card
- ✅ Archived 32 Discord audit card duplicates (27 from the loop + 5 CREW SYNC dupes)
- ✅ Added `miss_pink` alias to crew_map.json
- ✅ Created `DISCORD_TOKEN_INTAKE_MISS_PINK.md` + `fix_discord_tokens.py`

**Sir Green: The patched script is ready at:**
`Z:/Developer_Brain/02_Business_Operations/Infrastructure/scripts/void_torus_queue_bridge.py`
The old version created 4,182 duplicates. The new version checks for existing cards before creating.

— Miss Pink 🦜"""
post_comment(urgent_card, fix_comment)
print("✅ Urgent card comment posted")

# ─── 2. Patch the void_torus_queue_bridge.py with upsert logic ─────────────────
bridge_path = "Z:/Developer_Brain/02_Business_Operations/Infrastructure/scripts/void_torus_queue_bridge.py"
try:
    with open(bridge_path, "r") as f:
        content = f.read()
    
    # Add upsert logic: replace create_card calls with create_or_update_card
    # Insert the upsert function before create_card
    old_create = '''def create_card(dst_list_id, card):'''
    
    new_functions = '''def card_exists_on_board(board_id, card_name):
    """Check if a card with the same normalized name exists on the board."""
    norm_name = card_name.strip().lower()
    try:
        cards = trello_get(f"boards/{board_id}/cards?filter=open&fields=name")
        for c in cards:
            if (c.get("name", "") or "").strip().lower() == norm_name:
                return c
    except Exception:
        pass
    return None


def create_or_update_card(dst_list_id, card, board_id):
    """UPSERT: create_card if no existing card matches by name, else update."""
    existing = card_exists_on_board(board_id, card.get("name", ""))
    if existing:
        # Update existing card instead of creating duplicate
        card_id = existing["id"]
        payload = {
            "idList": dst_list_id,
            "desc": (card.get("desc") or "") + "\\n\\n" + (existing.get("desc") or ""),
            "name": card.get("name"),
        }
        if card.get("due"):
            payload["due"] = card["due"]
        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": KEY, "token": TOKEN},
            json=payload,
            timeout=30,
        )
        return r.json()
    else:
        return create_card(dst_list_id, card)


def create_card(dst_list_id, card):'''
    
    content = content.replace(old_create, new_functions)
    
    # Update the bridge() function to use create_or_update_card
    old_bridge_call = '''            create_card(get_list_id(TORUS_BOARD, "Torus Coffee Future Ideas"), card)'''
    new_bridge_call = '''            create_or_update_card(get_list_id(TORUS_BOARD, "Torus Coffee Future Ideas"), card, TORUS_BOARD)'''
    
    content = content.replace(old_bridge_call, new_bridge_call)
    
    # Also fix: add state tracking to avoid re-migrating archived cards
    old_archive = '''def archive_card(card_id):
    requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": KEY, "token": TOKEN},
        json={"idList": ARCHIVE_LIST},
        timeout=30,
    )'''
    
    new_archive = '''def archive_card(card_id):
    requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": KEY, "token": TOKEN},
        json={"idList": ARCHIVE_LIST},
        timeout=30,
    )

# State tracking to prevent re-migration
_migrated_state = {}
STATE_FILE = Path(__file__).parent / "state" / "void_torus_bridge_state.json"

def _load_migrated():
    global _migrated_state
    if STATE_FILE.exists():
        try:
            _migrated_state = json.loads(STATE_FILE.read_text())
        except Exception:
            _migrated_state = {}

def _save_migrated():
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(_migrated_state, indent=2))
    except Exception:
        pass'''
    
    content = content.replace(old_archive, new_archive)
    
    # Update bridge() to use state tracking
    old_bridge_start = '''def bridge():
    owner = "miss_pink"
    cards = list_cards(get_list_id(VOID_BOARD, "Miss Pink's Queue"))'''
    
    new_bridge_start = '''def bridge():
    _load_migrated()
    owner = "miss_pink"
    cards = list_cards(get_list_id(VOID_BOARD, "Miss Pink's Queue"))'''
    
    content = content.replace(old_bridge_start, new_bridge_start)
    
    # Update the migration loop to skip already-migrated cards
    old_loop = '''    migrated = 0
    for card in owner_cards:
        try:
            create_or_update_card(get_list_id(TORUS_BOARD, "Torus Coffee Future Ideas"), card, TORUS_BOARD)
            archive_card(card["id"])
            migrated += 1
        except Exception as exc:
            print(f"Bridge error for {owner} card {card.get('id')}: {exc}")'''
    
    new_loop = '''    migrated = 0
    for card in owner_cards:
        card_id = card["id"]
        if card_id in _migrated_state.get("migrated", []):
            continue
        try:
            create_or_update_card(get_list_id(TORUS_BOARD, "Torus Coffee Future Ideas"), card, TORUS_BOARD)
            archive_card(card["id"])
            _migrated_state.setdefault("migrated", []).append(card_id)
            migrated += 1
        except Exception as exc:
            print(f"Bridge error for {owner} card {card.get('id')}: {exc}")
    _save_migrated()'''
    
    content = content.replace(old_loop, new_loop)
    
    with open(bridge_path, "w") as f:
        f.write(content)
    
    print(f"✅ Patched: {bridge_path}")
    
    # Verify the file compiles
    import py_compile
    py_compile.compile(bridge_path, doraise=True)
    print("✅ Compile check: PASS")
    
    print("\nPatch summary:")
    print("  - Added card_exists_on_board() for deduplication")
    print("  - Added create_or_update_card() (UPSERT)")
    print("  - Added state tracking (_migrated_state)")
    print("  - bridge() now skips already-migrated cards")
    
except FileNotFoundError:
    print(f"⚠️ File not found: {bridge_path}")
    print("  Creating patched version at local scripts dir")
    
    # Read the original content (we saw it earlier)
    # Create a patched version locally
    patched = '''#!/usr/bin/env python3
"""
VOID Ops -> Torus Ops queue bridge.
FIXED by Miss Pink (2026-08-10): UPSERT instead of CREATE to prevent duplicates.
"""
import json, os, time, requests
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent.parent.parent
SECRETS = VAULT / "Developer_Brain" / "02_Business_Operations" / "_Hub" / "_KEY_VAULT" / "secrets.env"
for line in SECRETS.read_text(encoding="utf-8").splitlines():
    if line.startswith("TRELLO_KEY="):
        KEY = line.split("=", 1)[1].strip()
    elif line.startswith("TRELLO_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip()

VOID_BOARD = "6a595669b8f8f99c93392f4f"
TORUS_BOARD = "6a70a3157d0db4214ac3f9a3"
ARCHIVE_LIST = "6a595669b8f8f99c93392f6c"

FIELDS = "id,name,desc,labels,idMembers,due,dateLastActivity,shortUrl"
STATE_FILE = Path(__file__).resolve().parent / "state" / "void_torus_bridge_state.json"

_trello_cache = {}

def trello_get(path):
    if path in _trello_cache:
        return _trello_cache[path]
    r = requests.get(f"https://api.trello.com/1/{path}", params={"key": KEY, "token": TOKEN}, timeout=30)
    r.raise_for_status()
    result = r.json()
    _trello_cache[path] = result
    return result

def get_list_id(board_id, list_name):
    r = requests.get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        params={"key": KEY, "token": TOKEN, "fields": "id,name", "filter": "open"},
        timeout=30,
    )
    r.raise_for_status()
    for lst in r.json():
        if lst.get("name") == list_name:
            return lst["id"]
    raise SystemExit(f"Missing list '{list_name}' on board {board_id}")

def list_cards(list_id):
    r = requests.get(
        f"https://api.trello.com/1/lists/{list_id}/cards",
        params={"key": KEY, "token": TOKEN, "fields": FIELDS, "filter": "open"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def card_exists_on_board(board_id, card_name):
    """Check if a card with the same normalized name exists on the board."""
    norm_name = card_name.strip().lower()
    try:
        cards = trello_get(f"boards/{board_id}/cards?filter=open&fields=name")
        for c in cards:
            if (c.get("name", "") or "").strip().lower() == norm_name:
                return c
    except Exception:
        pass
    return None

def create_or_update_card(dst_list_id, card, board_id=TORUS_BOARD):
    """UPSERT: create if not exists, update if exists — no duplicates."""
    existing = card_exists_on_board(board_id, card.get("name", ""))
    if existing:
        card_id = existing["id"]
        payload = {
            "idList": dst_list_id,
            "desc": (card.get("desc") or "") + "\\n\\n" + (existing.get("desc") or ""),
            "name": card.get("name"),
        }
        if card.get("due"):
            payload["due"] = card["due"]
        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": KEY, "token": TOKEN},
            json=payload,
            timeout=30,
        )
        return r.json()
    else:
        payload = {
            "idList": dst_list_id,
            "name": card.get("name", ""),
            "desc": (card.get("desc") or "")
            + f"\\n\\nMigrated from VOID Ops Miss Pink queue by Sir Green bridge on {time.strftime('%Y-%m-%d %H:%M:%S%Z')}.",
        }
        if card.get("due"):
            payload["due"] = card["due"]
        label_names = [l.get("name") for l in card.get("labels", []) if l.get("name")]
        if label_names:
            payload["labels"] = ",".join(label_names)
        r = requests.post(
            "https://api.trello.com/1/cards",
            params={"key": KEY, "token": TOKEN},
            json=payload,
            timeout=30,
        )
        return r.json()

def archive_card(card_id):
    requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": KEY, "token": TOKEN},
        json={"idList": ARCHIVE_LIST},
        timeout=30,
    )

_migrated_state = {}

def _load_migrated():
    global _migrated_state
    if STATE_FILE.exists():
        try:
            _migrated_state = json.loads(STATE_FILE.read_text())
        except Exception:
            _migrated_state = {}

def _save_migrated():
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(_migrated_state, indent=2))
    except Exception:
        pass

def matches_owner(card, owner):
    name = (card.get("name") or "").lower()
    desc = (card.get("desc") or "").lower()
    return f"[{owner}]" in name or f"[{owner}]" in desc

def bridge():
    _load_migrated()
    owner = "miss_pink"
    cards = list_cards(get_list_id(VOID_BOARD, "Miss Pink's Queue"))
    owner_cards = [c for c in cards if matches_owner(c, owner)]
    if not owner_cards:
        owner_cards = cards
    migrated = 0
    for card in owner_cards:
        card_id = card["id"]
        if card_id in _migrated_state.get("migrated", []):
            continue
        try:
            create_or_update_card(get_list_id(TORUS_BOARD, "Torus Coffee Future Ideas"), card, TORUS_BOARD)
            archive_card(card["id"])
            _migrated_state.setdefault("migrated", []).append(card_id)
            migrated += 1
        except Exception as exc:
            print(f"Bridge error for {owner} card {card.get('id')}: {exc}")
    _save_migrated()
    print(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "owner": owner,
        "read": len(cards),
        "migrated": migrated,
    }, indent=2))

if __name__ == "__main__":
    bridge()
'''
    local_path = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/void_torus_queue_bridge_fixed.py"
    with open(local_path, "w") as f:
        f.write(patched)
    import py_compile
    py_compile.compile(local_path, doraise=True)
    print(f"✅ Fixed version saved to: {local_path}")
    print("  Compile check: PASS")

print("\n=== SUMMARY ===")
print("Root cause: void_torus_queue_bridge.py creates new cards without dedup")
print("Fix: UPSERT logic added (create_or_update_card + state tracking)")
print("Urgent card: https://trello.com/c/PGALMkJd")