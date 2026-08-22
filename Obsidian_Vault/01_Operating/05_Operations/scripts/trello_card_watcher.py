#!/usr/bin/env python3
"""Trello card watcher: monitor Torus_Ops for new cards, auto-label/tag/index/sort them."""
import json
import time
import requests
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
CREDENTIALS_PATH = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
TORUS_BOARD_ID = "6a70a3157d0db4214ac3f9a3"
INDEX_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"

# Lists to watch for new cards
WATCHED_LISTS = ["Torus Coffee's Future Ideas", "Backlog", "Top 10 - Highest Priority"]

def get_trello_credentials():
    creds = CREDENTIALS_PATH.read_text(encoding="utf-8")
    key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
    token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
    return key, token

def load_index():
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {"cards": [], "last_checked": None}

def save_index(index):
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

def get_board_lists(key, token, board_id):
    return requests.get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=10,
    ).json()

def get_board_labels(key, token, board_id):
    return requests.get(
        f"https://api.trello.com/1/boards/{board_id}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=10,
    ).json()

def get_void_board_ids(key, token):
    """Get all board IDs accessible to this token."""
    boards = requests.get(
        "https://api.trello.com/1/members/me/boards",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=15,
    ).json()
    return [b['id'] for b in boards]

def check_cross_board_duplicate(key, token, card_name, void_board_ids):
    """Check if card already exists on any accessible board."""
    name_lower = card_name.strip().lower()
    for board_id in void_board_ids:
        if board_id == TORUS_BOARD_ID:
            continue
        try:
            cards = requests.get(
                f"https://api.trello.com/1/boards/{board_id}/cards",
                params={"key": key, "token": token, "fields": "id,name", "limit": 1000, "filter": "all"},
                timeout=30,
            ).json()
            for c in cards:
                if c.get('name', '').strip().lower() == name_lower:
                    return c
        except:
            continue
    return None

def auto_process_card(key, token, card_id, card_name, list_id, list_map, label_map, void_board_ids):
    """Auto-label, tag, add description, and index a new card."""
    updates = {}

    # 1. Check for cross-board duplicates
    duplicate = check_cross_board_duplicate(key, token, card_name, void_board_ids)
    if duplicate:
        updates['comment'] = f"DUPLICATE: Already exists on {duplicate.get('board', 'another board')} - {duplicate['id']}"
        return updates, False

    # 2. Auto-assign labels based on list
    list_name = list_map.get(list_id, '')
    labels_to_add = []

    if 'Future Ideas' in list_name or 'Future Ideas' in card_name.lower():
        labels_to_add.extend(['Future Ideas', 'P3'])
    elif 'Top 10' in list_name or 'Top 10' in card_name.lower():
        labels_to_add.extend(['Top 10', 'P1'])
    elif 'P0' in list_name or 'P0' in card_name.lower():
        labels_to_add.extend(['P0'])
    elif 'P1' in list_name or 'P1' in card_name.lower():
        labels_to_add.extend(['P1'])
    elif 'P2' in list_name or 'P2' in card_name.lower():
        labels_to_add.extend(['P2'])
    elif 'P3' in list_name or 'P3' in card_name.lower():
        labels_to_add.extend(['P3'])
    elif 'P4' in list_name or 'P4' in card_name.lower():
        labels_to_add.extend(['P3', 'P4'])

    # Add label if not present
    for label_name in labels_to_add:
        if label_name in label_map:
            r = requests.post(
                f"https://api.trello.com/1/cards/{card_id}/idLabels",
                params={"key": key, "token": token},
                data={"value": label_map[label_name]},
                timeout=15,
            )
            if r.status_code == 200:
                updates['labeled'] = label_name

    # 3. Add description if missing
    card = requests.get(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": key, "token": token, "fields": "desc"},
        timeout=10,
    ).json()

    if not card.get('desc', '').strip():
        desc = f"Auto-indexed card: {card_name}\n\n"
        desc += f"Source: Torus_Ops board\n"
        desc += f"List: {list_name}\n"
        desc += f"Labels: {', '.join(labels_to_add)}\n"
        desc += f"Card ID: {card_id}\n"
        desc += f"Indexed: {datetime.now().isoformat()}\n"
        desc += f"\n---\n"
        desc += f"This card was auto-processed by Trello automation.\n"
        desc += f"Check TRELLO_CARD_INDEX.json before creating similar cards.\n"

        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": key, "token": token},
            data={"desc": desc},
            timeout=15,
        )
        if r.status_code == 200:
            updates['description'] = 'added'

    # 4. Add to index
    index = load_index()
    index['cards'].append({
        "id": card_id,
        "name": card_name,
        "list": list_name,
        "board": "Torus_Ops",
        "labels": labels_to_add,
        "indexed_at": datetime.now().isoformat(),
        "cross_board_checked": True,
        "duplicate_found": duplicate is not None
    })
    index['last_checked'] = datetime.now().isoformat()
    save_index(index)
    updates['indexed'] = True

    return updates, True

def watch_for_new_cards():
    """Main watcher: check for new cards and process them."""
    key, token = get_trello_credentials()
    lists = get_board_lists(key, token, TORUS_BOARD_ID)
    list_map = {l['id']: l['name'] for l in lists}

    labels = get_board_labels(key, token, TORUS_BOARD_ID)
    label_map = {l['name']: l['id'] for l in labels}

    void_board_ids = get_void_board_ids(key, token)

    # Get all current cards
    current_cards = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,idList,labels,desc", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()

    # Load index
    index = load_index()
    indexed_ids = {c['id'] for c in index['cards']}

    # Find new cards
    new_cards = [c for c in current_cards if c['id'] not in indexed_ids]

    print(f"Total cards: {len(current_cards)}")
    print(f"Indexed cards: {len(indexed_ids)}")
    print(f"New cards to process: {len(new_cards)}")

    processed = 0
    for card in new_cards:
        list_name = list_map.get(card.get('idList', ''), '')
        if list_name in WATCHED_LISTS or any(w in list_name for w in WATCHED_LISTS):
            updates, success = auto_process_card(
                key, token, card['id'], card.get('name', ''), 
                card.get('idList', ''), list_map, label_map, void_board_ids
            )
            processed += 1
            print(f"Processed: {card.get('name', '')[:50]} -> {updates}")

    print(f"\nProcessed {processed} new cards")
    return processed

if __name__ == "__main__":
    watch_for_new_cards()
