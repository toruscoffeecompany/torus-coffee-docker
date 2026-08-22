#!/usr/bin/env python3
"""Close completed historical P0/P1 cards and enforce Top 10 exactly."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
DONE_LABEL = "Done"

CREATED_PATTERNS = [
    r"^(Created|Stopped|Updated|Wrote|Built|Fixed|Added|Implemented|Confirmed|Verified|Deployed)\s",
    r"^(✅ )?Confirm ",
    r"^(✅ )?Setup ",
    r"Gmail alert spam fix report$",
    r"alert_router\.py$",
    r"inventory_alert\.py$",
]

def load_trello_creds():
    text = CRED_FILE.read_text(errors="ignore")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello credentials missing")
    return api_key, token

def get_board(api_key, token, board_name="Torus_Ops"):
    boards = requests.get("https://api.trello.com/1/members/me/boards", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=30).json()
    bid = next((b["id"] for b in boards if b["name"] == board_name), None)
    if not bid:
        raise RuntimeError(f"Board not found: {board_name}")
    return bid

def get_list_id(api_key, token, board_id, list_name):
    lists = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=30).json()
    lid = next((l["id"] for l in lists if l["name"] == list_name), None)
    if not lid:
        raise RuntimeError(f"List not found: {list_name}")
    return lid

def get_label_id(api_key, token, board_id, label_name):
    labels = requests.get(f"https://api.trello.com/1/boards/{board_id}/labels", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=30).json()
    return next((l["id"] for l in labels if l["name"] == label_name), None)

def move_card(api_key, token, card_id, list_id):
    r = requests.put(f"https://api.trello.com/1/cards/{card_id}", data={"key": api_key, "token": token, "idList": list_id}, timeout=30)
    r.raise_for_status()
    return r.json()

def add_label(api_key, token, card_id, label_id):
    r = requests.post(f"https://api.trello.com/1/cards/{card_id}/idLabels", data={"key": api_key, "token": token, "value": label_id}, timeout=30)
    r.raise_for_status()
    return r.json()

def is_completed(name):
    n = name.strip()
    if n.startswith("Stopped "):
        return True
    if n.startswith("Created "):
        return True
    if n.startswith("Updated "):
        return True
    if n.startswith("Built "):
        return True
    if n.startswith("Fixed "):
        return True
    if n.startswith("Added "):
        return True
    if n.startswith("Wrote "):
        return True
    if n.startswith("Implemented "):
        return True
    if n.startswith("✅ "):
        return True
    if n.endswith("alert_router.py"):
        return True
    if n.endswith("inventory_alert.py"):
        return True
    if n.endswith("Gmail alert spam fix report"):
        return True
    if "Gmail send scope for alerts" in n:
        return True
    return False

def run():
    api_key, token = load_trello_creds()
    board_id = get_board(api_key, token)
    done_id = get_list_id(api_key, token, board_id, "Done")
    done_label_id = get_label_id(api_key, token, board_id, DONE_LABEL)
    top10_id = get_list_id(api_key, token, board_id, "Top 10 — Focus Fleet")

    # Move completed P0/P1 cards to Done
    for list_name in ["P0 - Alert / Critical / Do Now", "P1 - High / Doing Now"]:
        lid = get_list_id(api_key, token, board_id, list_name)
        cards = requests.get(f"https://api.trello.com/1/lists/{lid}/cards", params={"key": api_key, "token": token, "fields": "name,id,labels"}, timeout=30).json()
        moved = 0
        for c in cards:
            if is_completed(c.get("name", "")):
                move_card(api_key, token, c["id"], done_id)
                if done_label_id:
                    add_label(api_key, token, c["id"], done_label_id)
                moved += 1
        print(f"[{list_name}] moved {moved} completed cards to Done")

    # Enforce Top 10 exactly 10
    top10_cards = requests.get(f"https://api.trello.com/1/lists/{top10_id}/cards", params={"key": api_key, "token": token, "fields": "name,id,dateLastActivity"}, timeout=30).json()
    top10_cards_sorted = sorted(top10_cards, key=lambda c: c.get("dateLastActivity", ""), reverse=True)
    target = 10
    if len(top10_cards_sorted) > target:
        for c in top10_cards_sorted[target:]:
            # Move excess to P1
            p1_id = get_list_id(api_key, token, board_id, "P1 - High / Doing Now")
            move_card(api_key, token, c["id"], p1_id)
            print(f"[Top 10] moved excess: {c['name'][:60]}")
    elif len(top10_cards_sorted) < target:
        # Promote highest P1 cards
        p1_id = get_list_id(api_key, token, board_id, "P1 - High / Doing Now")
        p1_cards = requests.get(f"https://api.trello.com/1/lists/{p1_id}/cards", params={"key": api_key, "token": token, "fields": "name,id,dateLastActivity,labels"}, timeout=30).json()
        top10_label_id = get_label_id(api_key, token, board_id, "Top 10")
        p1_sorted = sorted(p1_cards, key=lambda c: c.get("dateLastActivity", ""), reverse=True)
        needed = target - len(top10_cards_sorted)
        for c in p1_sorted[:needed]:
            move_card(api_key, token, c["id"], top10_id)
            if top10_label_id:
                add_label(api_key, token, c["id"], top10_label_id)
            print(f"[Top 10] promoted: {c['name'][:60]}")
    print(f"[Top 10] current count: {len(top10_cards_sorted)}")

if __name__ == "__main__":
    run()
