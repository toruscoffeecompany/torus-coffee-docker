#!/usr/bin/env python3
"""Test auto-sort watcher for Miss Pink's inbox."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
STATE_FILE = VAULT / "10_Skills_Library/05_Operations/test_auto_sort_state.json"
OODA_LOG = VAULT / "10_Skills_Library/05_Operations/logs/continuous_ooda_worker.log"
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"

API_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"
INBOX_LIST = "6a75869a95f875e18db6c081"
GREEN_QUEUE = "6a7586d65efb13d4c8a6c1f9"
AZURE_QUEUE = "6a7586d8f9b0a5b7c8d9e0f1"

QUEUE_MAP = {
    "Sir Green": GREEN_QUEUE,
    "Sir Azure": AZURE_QUEUE,
}


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    try:
        with open(OODA_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            STATE_FILE.replace(STATE_FILE.with_suffix(".bad.json"))
    return {"processed": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fetch_inbox() -> list:
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    r = requests.get(
        url,
        params={
            "key": API_KEY,
            "token": TOKEN,
            "fields": "name,id,desc,idList,labels,url",
        },
        timeout=30,
    )
    r.raise_for_status()
    return [c for c in r.json() if c.get("idList") == INBOX_LIST and not c.get("closed")]


def move_card(card_id: str, list_id: str) -> None:
    url = f"https://api.trello.com/1/cards/{card_id}"
    r = requests.put(
        url,
        json={"key": API_KEY, "token": TOKEN, "idList": list_id},
        timeout=30,
    )
    r.raise_for_status()


def comment_card(card_id: str, text: str) -> None:
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    r = requests.post(
        url,
        json={"key": API_KEY, "token": TOKEN, "text": text},
        timeout=30,
    )
    r.raise_for_status()


def add_label(card_id: str, label_name: str) -> None:
    # Best-effort: add label if known
    label_map = {
        "Sir Green Queue": "6a7586e0f1b2c3d4e5f6a7b8",
        "Sir Azure Queue": "6a7586e1f2b3c4d5e6f7a8b9",
        "TEST": "6a7586e2f3b4c5d6e7f8a9b0",
    }
    label_id = label_map.get(label_name)
    if not label_id:
        return
    url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
    r = requests.post(
        url,
        json={"key": API_KEY, "token": TOKEN, "value": label_id},
        timeout=30,
    )
    if r.status_code >= 400:
        log(f"LABEL_ADD_FAIL {card_id} {label_name} {r.status_code}")


def detect_recipient(card: dict) -> str | None:
    text = (card.get("name", "") + " " + card.get("desc", "")).lower()
    if "sir green" in text or "sirgreen" in text:
        return "Sir Green"
    if "sir azure" in text or "sirazure" in text:
        return "Sir Azure"
    return None


def is_test_card(card: dict) -> bool:
    name = card.get("name", "").lower()
    return "test-auto-sort" in name or "[test]" in name


def main() -> int:
    log("TEST_AUTO_SORT_START")
    state = load_state()
    processed = set(state.get("processed", []))

    cards = fetch_inbox()
    log(f"INBOX_SCAN cards={len(cards)}")

    worked = False
    for card in cards:
        cid = card["id"]
        if cid in processed:
            continue

        recipient = detect_recipient(card)
        if not recipient:
            log(f"NO_RECIPIENT {cid} {card['name']}")
            processed.add(cid)
            state["processed"] = list(processed)
            save_state(state)
            continue

        target_list = QUEUE_MAP[recipient]
        move_card(cid, target_list)
        add_label(cid, f"{recipient.replace(' ', '')}Queue")
        comment = (
            f"[{datetime.now(timezone.utc).isoformat()}] Auto-sorted to {recipient} Queue.\\n"
            f"Reply TEST_RECV to confirm routing.\\n"
            f"Card: {card.get('url', '')}"
        )
        comment_card(cid, comment)
        log(f"AUTO_SORTED {cid} -> {recipient}")
        processed.add(cid)
        state["processed"] = list(processed)
        save_state(state)
        worked = True
        break

    if not worked:
        log("NO_WORK")

    log("TEST_AUTO_SORT_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
