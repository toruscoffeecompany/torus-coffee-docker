#!/usr/bin/env python3
"""
VOID -> Torus Miss Pink Queue Sync (v1)

Reads Miss Pink's Queue on the VOID Ops board, finds cards assigned to
Miss Pink (or tagged miss-pink), and transfers them to the Torus Ops
board — deduplicating by name to prevent the Smart Bridge duplication loop.

Flow:
1. Scan ALL cards on VOID Ops board
2. For each Miss Pink card:
   a. If it's a duplicate (same name already exists on Torus Ops), archive it on VOID
   b. If it's new, move it to Torus Ops P2/P1/P0 based on labels
3. Scan MISSING: cards that exist on Torus Ops but not VOID (already handled)
4. Report results

This replaces the naive sync that was creating 1 card/sec duplicates by
blindly moving every card without checking for existing duplicates.
"""
import sys, requests, time, json
sys.path.insert(0, "scripts")
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds["api_key"], creds["token"]
VOID = "6a595669b8f8f99c93392f4f"
TORUS = "6a70a3157d0db4214ac3f9a3"

HEADERS = {"Content-Type": "application/json"}


def get_lists(board_id):
    r = requests.get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        params={"key": key, "token": token, "fields": "name,id,closed"},
        timeout=30,
    )
    return [l for l in r.json() if not l.get("closed")]


def get_all_cards(board_id):
    """Fetch ALL cards on a board (open only)."""
    r = requests.get(
        f"https://api.trello.com/1/boards/{board_id}/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,idList,labels,closed,dateLastActivity"},
        timeout=120,
    )
    return [c for c in r.json() if not c.get("closed", False)]


def archive_card(card_id):
    """Archive (close) a Trello card by ID."""
    r = requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": key, "token": token, "closed": "true"},
        timeout=10,
    )
    return r.status_code == 200


def move_card(card_id, list_id, board_id=None):
    """Move a Trello card to a different list (optionally on a different board)."""
    params = {"key": key, "token": token, "idList": list_id}
    if board_id:
        params["idBoard"] = board_id
    r = requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params=params,
        timeout=15,
    )
    return r.status_code == 200


def get_card_actions(card_id, limit=5):
    """Get recent actions on a card (to find original creation)."""
    r = requests.get(
        f"https://api.trello.com/1/cards/{card_id}/actions",
        params={"key": key, "token": token, "limit": limit, "fields": "type,date,data"},
        timeout=10,
    )
    return r.json()


def main():
    print("=== VOID Ops -> Torus Ops Miss Pink Queue Sync ===\n")

    # Get board structures
    void_lists = {l["id"]: l["name"] for l in get_lists(VOID)}
    torus_lists = {l["id"]: l["name"] for l in get_lists(TORUS)}
    torus_list_order = get_lists(TORUS)  # ordered by position

    # Target lists on Torus
    targets = {}
    for l in torus_list_order:
        name = l["name"]
        if "Top 10" in name:
            targets["top10"] = l["id"]
        elif name.startswith("P0"):
            targets["p0"] = l["id"]
        elif name.startswith("P1"):
            targets["p1"] = l["id"]
        elif name.startswith("P2"):
            targets["p2"] = l["id"]
        elif name.startswith("P3"):
            targets["p3"] = l["id"]
        elif "Miss Pink" in name:
            targets["inbox"] = l["id"]

    # Get ALL cards on both boards
    void_cards = get_all_cards(VOID)
    torus_cards = get_all_cards(TORUS)

    # Build name index for Torus Ops (what names already exist?)
    torus_existing_names = set(c["name"] for c in torus_cards)
    print(f"Torus Ops: {len(torus_cards)} open cards, {len(torus_existing_names)} unique names")
    print(f"VOID Ops: {len(void_cards)} open cards")

    # Find Miss Pink cards on VOID (by name, desc, or label)
    mp_cards = []
    for c in void_cards:
        name = c.get("name", "")
        desc = c.get("desc", "")
        labels = [x.get("name", "").lower() for x in c.get("labels", [])]
        is_mp = (
            "miss pink" in name.lower()
            or "miss pink" in desc.lower()
            or "miss-pink" in desc.lower()
            or "miss pink" in labels
            or "miss-pink" in labels
        )
        if is_mp:
            mp_cards.append(c)

    print(f"\nFound {len(mp_cards)} Miss Pink cards on VOID Ops board\n")

    transferred = 0
    archived_dups = 0
    kept = 0

    for c in mp_cards:
        card_id = c["id"]
        name = c["name"]
        labels = [x.get("name", "").lower() for x in c.get("labels", [])]
        list_name = void_lists.get(c["idList"], "?")

        # CRITICAL: Check if this is a duplicate (same name already on Torus)
        if name in torus_existing_names:
            # This is a duplicate — archive it on VOID board
            archive_card(card_id)
            archived_dups += 1
            continue

        # Not a duplicate — transfer to Torus Ops
        # Classify priority
        if "p0" in labels or "critical" in name.lower():
            target = targets.get("p0", targets.get("p2"))
        elif "p1" in labels or "high" in name.lower():
            target = targets.get("p1", targets.get("p2"))
        elif "p2" in labels:
            target = targets.get("p2")
        else:
            target = targets.get("inbox") or targets.get("p2")

        if target and move_card(card_id, target, TORUS):
            transferred += 1
            # Add a tracking comment
            requests.post(
                f"https://api.trello.com/1/cards/{card_id}/actions/comments",
                params={"key": key, "token": token,
                       "text": "Transferred from VOID Ops to Torus Ops by Miss Pink sync v1. Deduplication active."},
                timeout=10,
            )
            torus_existing_names.add(name)  # Prevent re-transfer
        else:
            kept += 1

        time.sleep(0.2)  # Rate limit

    # Print summary
    print(f"\n=== SYNC RESULTS ===")
    print(f"  Transferred (new) to Torus Ops: {transferred}")
    print(f"  Archived (duplicates on VOID): {archived_dups}")
    print(f"  Kept (could not transfer):    {kept}")

    # Final board states
    void_final = get_all_cards(VOID)
    torus_final = get_all_cards(TORUS)
    print(f"\n  VOID Ops open: {len(void_final)}")
    print(f"  Torus Ops open: {len(torus_final)}")

    # Count remaining Smart Bridge dupes
    sb_void = [c for c in void_final if "Smart Bridge" in c.get("name", "")]
    sb_torus = [c for c in torus_final if "Smart Bridge" in c.get("name", "")]
    print(f"  Smart Bridge on VOID: {len(sb_void)}")
    print(f"  Smart Bridge on Torus: {len(sb_torus)}")


if __name__ == "__main__":
    main()
