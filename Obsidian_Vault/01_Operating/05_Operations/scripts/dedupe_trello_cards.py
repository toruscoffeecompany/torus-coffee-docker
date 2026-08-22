#!/usr/bin/env python3
"""One-time dedupe/cleanup pass for duplicate Trello cards."""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

DONE_LIST = "6a70a32a723c0312a3d5fbb4"

LABEL_MAP = {
    "Top 10": "6a74c9ad1518ad0f9e645fc5",
    "P1": "6a70acc569135c796d8eba5d",
    "P2": "6a70acc56f143597877f576e",
    "P3": "6a70acc6fddcac79f411267f",
    "P0": "6a74cc10430afd9940c72bae",
}


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)


def load_creds() -> tuple[str, str]:
    text = TRELLO_CREDS.read_text(encoding="utf-8")
    lines = text.splitlines()
    api_key = token = None
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Missing Trello API key/token")
    return api_key, token


def api_get(url: str, params: dict):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(url: str, params: dict):
    r = requests.post(url, json=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_put(url: str, params: dict):
    r = requests.put(url, json=params, timeout=30)
    r.raise_for_status()
    return r.json()


def comment_card(card_id: str, text: str, api_key: str, token: str) -> None:
    api_post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        {"key": api_key, "token": token, "text": text},
    )


def move_card(card_id: str, list_id: str, api_key: str, token: str) -> None:
    api_put(
        f"https://api.trello.com/1/cards/{card_id}",
        {"key": api_key, "token": token, "idList": list_id},
    )


def close_card(card_id: str, api_key: str, token: str) -> None:
    api_put(
        f"https://api.trello.com/1/cards/{card_id}",
        {"key": api_key, "token": token, "closed": True},
    )


def main() -> int:
    api_key, token = load_creds()
    cards = api_get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
        {"key": api_key, "token": token, "fields": "name,id,dateLastActivity,closed,shortUrl"},
    )
    open_cards = [c for c in cards if not c.get("closed")]
    by_title = defaultdict(list)
    for c in open_cards:
        by_title[c["name"].strip()].append(c)

    dupes = {title: items for title, items in by_title.items() if len(items) > 1}
    log(f"open={len(open_cards)} duplicate_titles={len(dupes)}")
    archived = 0
    for title, items in dupes.items():
        items.sort(key=lambda c: c.get("dateLastActivity") or "", reverse=True)
        keep = items[0]
        for old in items[1:]:
            try:
                comment_card(
                    old["id"],
                    f"[{datetime.now(timezone.utc).isoformat()}] SMART_TICKET duplicate cleanup: keeping {keep['shortUrl']}.",
                    api_key,
                    token,
                )
                close_card(old["id"], api_key, token)
                move_card(old["id"], DONE_LIST, api_key, token)
                archived += 1
                log(f"ARCHIVED_DUPLICATE {old['id']} {title}")
            except Exception as e:
                log(f"ARCHIVE_FAIL {old['id']} {e}")
        try:
            comment_card(
                keep["id"],
                f"[{datetime.now(timezone.utc).isoformat()}] SMART_TICKET dedupe: archived {len(items)-1} duplicate(s).",
                api_key,
                token,
            )
            log(f"KEPT {keep['id']} {title}")
        except Exception as e:
            log(f"KEEP_COMMENT_FAIL {keep['id']} {e}")

    log(f"DEDUPE_COMPLETE archived={archived}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
