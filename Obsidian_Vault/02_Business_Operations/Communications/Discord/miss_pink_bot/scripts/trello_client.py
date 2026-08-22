#!/usr/bin/env python3
"""Trello client for Miss Pink bot."""
import os
import requests
from typing import Optional

TRELLO_KEY = os.environ.get("TRELLO_KEY") or "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN") or "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = os.environ.get("TRELLO_BOARD_ID") or "6a70a3157d0db4214ac3f9a3"


def _get(path: str, params: Optional[dict] = None):
    params = dict(params or {})
    params.update({"key": TRELLO_KEY, "token": TRELLO_TOKEN})
    r = requests.get(f"https://api.trello.com/1/{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, params: Optional[dict] = None):
    params = dict(params or {})
    params.update({"key": TRELLO_KEY, "token": TRELLO_TOKEN})
    r = requests.post(f"https://api.trello.com/1/{path}", json=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _put(path: str, params: Optional[dict] = None):
    params = dict(params or {})
    params.update({"key": TRELLO_KEY, "token": TRELLO_TOKEN})
    r = requests.put(f"https://api.trello.com/1/{path}", json=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_boards():
    return _get("members/me/boards", {"fields": "name,id"})


def get_board_lists(board_id: str = BOARD_ID):
    return _get(f"boards/{board_id}/lists", {"fields": "name,id"})


def get_list_cards(list_id: str):
    return _get(f"lists/{list_id}/cards", {"fields": "name,id,shortUrl,desc,dateLastActivity"})


def top_cards(limit: int = 5):
    lists = get_board_lists()
    by_priority = []
    for l in lists:
        cards = get_list_cards(l["id"])
        for c in cards:
            c["listName"] = l["name"]
            by_priority.append(c)
    by_priority.sort(key=lambda c: c.get("dateLastActivity") or "", reverse=True)
    return by_priority[:limit]


def find_list_id(list_name: str) -> Optional[str]:
    lists = get_board_lists()
    for l in lists:
        if l["name"].lower() == list_name.lower():
            return l["id"]
    return None


def create_card(name: str, list_name: str = "Inbox", desc: str = ""):
    list_id = find_list_id(list_name)
    if not list_id:
        raise ValueError(f"List not found: {list_name}")
    return _post("cards", {"name": name, "idList": list_id, "desc": desc})


def add_comment(card_id: str, text: str):
    return _post(f"cards/{card_id}/actions/comments", {"text": text})


def move_card(card_id: str, list_id: str):
    return _put(f"cards/{card_id}", {"idList": list_id})


def find_card_by_name(name: str, limit: int = 20):
    """Find cards on the board matching a name (case-insensitive, fuzzy)."""
    cards = _get(f"boards/{BOARD_ID}/cards", {"fields": "name,id,shortUrl,desc,dateLastActivity"})
    matches = [c for c in cards if name.lower() in c.get("name", "").lower()]
    matches.sort(key=lambda c: len(c.get("name", "")), reverse=True)
    return matches[:limit]


def get_label_id_by_name(label_name: str):
    """Find a label by name on the board, return its ID (or None)."""
    labels = _get(f"boards/{BOARD_ID}/labels", {"fields": "name,color,id"})
    for l in labels:
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None


def add_label_to_card(card_id: str, label_name: str):
    """Add a label to a card by label name (creates label if needed)."""
    label_id = get_label_id_by_name(label_name)
    if not label_id:
        label_id = _post(f"boards/{BOARD_ID}/labels", {"name": label_name, "color": "sky"})["id"]
    return _post(f"cards/{card_id}/idLabels", {"value": label_id})


def read_card(card_id: str):
    """Full card details."""
    return _get(f"cards/{card_id}", {"fields": "name,desc,due,dateLastActivity"})


def get_card_comments(card_id: str):
    """All comments on a card."""
    actions = _get(f"cards/{card_id}/actions", {"filter": "commentCard", "fields": "date"})
    return [a for a in actions if a.get("type") == "commentCard"]

