#!/usr/bin/env python3
"""Automate Trello board setup to mirror VOID Ops structure for Torus_Ops."""
import json
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
CREDENTIALS_PATH = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
TORUS_BOARD_ID = "6a70a3157d0db4214ac3f9a3"

def get_trello_credentials():
    creds = CREDENTIALS_PATH.read_text(encoding="utf-8")
    key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
    token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
    return key, token

def get_board_lists(key, token, board_id):
    return requests.get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        params={"key": key, "token": token, "fields": "id,name,pos", "filter": "all"},
        timeout=15,
    ).json()

def get_board_labels(key, token, board_id):
    return requests.get(
        f"https://api.trello.com/1/boards/{board_id}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=10,
    ).json()

def get_board_cards(key, token, board_id):
    return requests.get(
        f"https://api.trello.com/1/boards/{board_id}/cards",
        params={"key": key, "token": token, "fields": "id,name,idList,labels", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()

def ensure_list(key, token, board_id, name, pos="bottom"):
    lists = get_board_lists(key, token, board_id)
    for l in lists:
        if l['name'] == name:
            return l['id']
    r = requests.post(
        f"https://api.trello.com/1/lists",
        params={"key": key, "token": token, "idBoard": board_id},
        data={"name": name, "pos": pos},
        timeout=15,
    )
    return r.json()['id'] if r.status_code == 200 else None

def ensure_label(key, token, board_id, name, color):
    labels = get_board_labels(key, token, board_id)
    for l in labels:
        if l['name'] == name:
            return l['id']
    r = requests.post(
        f"https://api.trello.com/1/labels",
        params={"key": key, "token": token, "idBoard": board_id},
        data={"name": name, "color": color},
        timeout=15,
    )
    return r.json()['id'] if r.status_code == 200 else None

def move_card(key, token, card_id, target_list_id):
    return requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        params={"key": key, "token": token},
        data={"idList": target_list_id},
        timeout=15,
    ).status_code == 200

def label_card(key, token, card_id, label_id):
    return requests.post(
        f"https://api.trello.com/1/cards/{card_id}/idLabels",
        params={"key": key, "token": token},
        data={"value": label_id},
        timeout=15,
    ).status_code == 200

def setup_void_ops_structure():
    key, token = get_trello_credentials()
    board_id = TORUS_BOARD_ID

    # 1. Create lists (VOID Ops structure)
    lists_to_create = [
        ("Top 10 — Focus Fleet", "top"),
        ("To Do", "top"),
        ("P0 - Critical / Do Now", "top"),
        ("P1 - High / This Week", "top"),
        ("Doing", "top"),
        ("P2 - Medium / Backlog", "bottom"),
        ("Backlog", "bottom"),
        ("Blocked", "bottom"),
        ("Sir Azure's Queue", "bottom"),
        ("P3 - Low / Someday", "bottom"),
        ("Miss Pink's Queue", "bottom"),
        ("Follow-up", "bottom"),
        ("Done", "bottom"),
    ]

    list_map = {}
    for name, pos in lists_to_create:
        list_id = ensure_list(key, token, board_id, name, pos)
        if list_id:
            list_map[name] = list_id
            print(f"List ready: {name}")
        else:
            print(f"Failed to create list: {name}")

    # 2. Create labels (VOID Ops labels)
    labels_to_create = [
        ("P0", "red"),
        ("P1", "orange"),
        ("P2", "yellow"),
        ("P3", "red"),
        ("Top 10", "yellow"),
        ("Future Ideas", "yellow"),
        ("Doing", "green"),
        ("Done", "red"),
        ("Blocked", "purple"),
        ("Waiting", "yellow"),
        ("On-Hold", "orange"),
        ("Next Week", "orange"),
        ("This Week", "yellow"),
        ("This Month", "red"),
        ("Backlog", "black"),
        ("Todo", "black"),
        ("followup", "black"),
        ("project", "pink"),
        ("docs", "sky"),
        ("lore", "purple"),
        ("ops", "green"),
        ("finance", "green"),
        ("calendar", "lime"),
        ("linear-sync", "blue"),
    ]

    label_map = {}
    for name, color in labels_to_create:
        label_id = ensure_label(key, token, board_id, name, color)
        if label_id:
            label_map[name] = label_id
            print(f"Label ready: {name}")

    # 3. Sort cards by priority
    cards = get_board_cards(key, token, board_id)
    priority_map = {
        'Top 10': 'Top 10 — Focus Fleet',
        'P0': 'P0 - Critical / Do Now',
        'P1': 'P1 - High / This Week',
        'P2': 'P2 - Medium / Backlog',
        'P3': 'P3 - Low / Someday',
        'Future Ideas': "Torus Coffee's Future Ideas",
        'Blocked': 'Blocked',
        'Doing': 'Doing',
        'Done': 'Done',
    }

    moved = 0
    for c in cards:
        current_list = c.get('idList', '')
        labels = [l['name'] for l in c.get('labels', [])]
        
        target_list = None
        for label, list_name in priority_map.items():
            if label in labels:
                target_list = list_map.get(list_name)
                break
        
        if target_list and target_list != current_list:
            if move_card(key, token, c['id'], target_list):
                moved += 1

    print(f"\nMoved {moved} cards to correct lists")

    # 4. Add Backlog label to Backlog list cards
    backlog_list_id = list_map.get('Backlog')
    backlog_label_id = label_map.get('Backlog')
    if backlog_list_id and backlog_label_id:
        backlog_cards = [c for c in cards if c.get('idList') == backlog_list_id]
        labeled = 0
        for c in backlog_cards:
            labels = [l['name'] for l in c.get('labels', [])]
            if 'Backlog' not in labels:
                if label_card(key, token, c['id'], backlog_label_id):
                    labeled += 1
        print(f"Labeled {labeled} Backlog cards")

    print("\nVOID Ops structure automation complete!")

if __name__ == "__main__":
    setup_void_ops_structure()
