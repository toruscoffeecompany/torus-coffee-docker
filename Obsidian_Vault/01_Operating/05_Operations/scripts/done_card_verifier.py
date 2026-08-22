#!/usr/bin/env python3
"""
Done-card verifier for Torus_Ops board.
Rules:
- Read all cards in Done list.
- For each card, verify completion by direct evidence:
  * Has a status comment with verified completion marker
  * Or linked GitHub issue is closed
  * Or card has explicit "Done" verification marker in description
- If verified done: delete card permanently.
- If not verified done: move to "P5 - Low / Review" and refresh tags/labels.
"""
import json
import os
import sys
import time
import requests
from pathlib import Path

VAULT = Path("D:/Work/Torus Coffee Company LLC")
CRED_PATH = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
BASE_URL = "https://api.trello.com/1"
DONE_LIST_ID = "6a70a32a723c0312a3d5fbb4"
P5_LIST_ID = "6a70a3282e405a2460afc170"
DONE_LIST_NAME = "Done"
P5_LIST_NAME = "P5 - Low / Review"
REQUEST_DELAY = 0.35


def load_credentials():
    text = CRED_PATH.read_text()
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Missing Trello API key/token")
    return api_key, token


def get_done_cards(api_key, token):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/lists/{DONE_LIST_ID}/cards",
        params={"key": api_key, "token": token, "fields": "name,id,desc,labels,idList,dateLastActivity"},
    )
    r.raise_for_status()
    return r.json()


def get_card_comments(api_key, token, card_id):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/cards/{card_id}/actions",
        params={"key": api_key, "token": token, "filter": "commentCard", "fields": "data,date"},
    )
    r.raise_for_status()
    return r.json()


def rate_limited_request(method, url, **kwargs):
    for attempt in range(4):
        r = requests.request(method, url, timeout=30, **kwargs)
        if r.status_code != 429:
            return r
        wait = (attempt + 1) * 3.0
        print(f"  rate-limited, waiting {wait}s")
        time.sleep(wait)
    return r


def get_done_cards(api_key, token):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/lists/{DONE_LIST_ID}/cards",
        params={"key": api_key, "token": token, "fields": "name,id,desc,labels,idList,dateLastActivity"},
    )
    r.raise_for_status()
    return r.json()


def get_card_comments(api_key, token, card_id):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/cards/{card_id}/actions",
        params={"key": api_key, "token": token, "filter": "commentCard", "fields": "data,date"},
    )
    r.raise_for_status()
    return r.json()


def get_card_github_issue(api_key, token, card_id):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/cards/{card_id}/attachments",
        params={"key": api_key, "token": token, "fields": "url,name"},
    )
    r.raise_for_status()
    attachments = r.json()
    for att in attachments:
        url = att.get("url", "")
        if "github.com" in url and "/issues/" in url:
            return url
    return None


def is_verified_done(api_key, token, card):
    desc = card.get("desc", "") or ""
    if "VERIFIED_DONE" in desc or "[VERIFIED DONE]" in desc:
        return True, "description_marker"

    comments = get_card_comments(api_key, token, card["id"])
    for action in comments:
        text = action.get("data", {}).get("text", "") or ""
        if "VERIFIED_DONE" in text or "[VERIFIED DONE]" in text:
            return True, "comment_marker"

    gh_url = get_card_github_issue(api_key, token, card["id"])
    if gh_url:
        parts = gh_url.split("github.com/")[1].split("/")
        if len(parts) >= 3:
            owner, repo, number = parts[0], parts[1], parts[3] if "/issues/" in gh_url else parts[2]
            gh_r = rate_limited_request(
                "get",
                f"https://api.github.com/repos/{owner}/{repo}/issues/{number}",
            )
            if gh_r.status_code == 200 and gh_r.json().get("state") == "closed":
                return True, "github_issue_closed"

    return False, "unverified"


def move_card(api_key, token, card_id, list_id):
    r = rate_limited_request(
        "put",
        f"{BASE_URL}/cards/{card_id}",
        params={"key": api_key, "token": token, "idList": list_id},
    )
    return r.status_code == 200


def delete_card(api_key, token, card_id):
    r = rate_limited_request(
        "delete",
        f"{BASE_URL}/cards/{card_id}",
        params={"key": api_key, "token": token},
    )
    return r.status_code == 200


def refresh_labels(api_key, token, card_id):
    r = rate_limited_request(
        "get",
        f"{BASE_URL}/cards/{card_id}",
        params={"key": api_key, "token": token, "fields": "labels,idBoard"},
    )
    r.raise_for_status()
    card = r.json()
    existing = {lab["name"] for lab in card.get("labels", [])}
    needed = {"ops", "P5"}
    missing = needed - existing
    if not missing:
        return
    labels_r = rate_limited_request(
        "get",
        f"{BASE_URL}/boards/{card.get('idBoard')}/labels",
        params={"key": api_key, "token": token, "fields": "name,id"},
    )
    labels_r.raise_for_status()
    label_map = {lab["name"]: lab["id"] for lab in labels_r.json()}
    for name in missing:
        label_id = label_map.get(name)
        if not label_id:
            continue
        time.sleep(REQUEST_DELAY)
        rate_limited_request(
            "post",
            f"{BASE_URL}/cards/{card_id}/idLabels",
            params={"key": api_key, "token": token, "value": label_id},
        )


def post_comment(api_key, token, card_id, text):
    time.sleep(REQUEST_DELAY)
    rate_limited_request(
        "post",
        f"{BASE_URL}/cards/{card_id}/actions/comments",
        params={"key": api_key, "token": token, "text": text},
    )


def main():
    api_key, token = load_credentials()
    cards = get_done_cards(api_key, token)
    print(f"Done cards: {len(cards)}")
    verified = 0
    moved = 0
    deleted = 0
    failed = 0
    for card in cards:
        cid = card["id"]
        name = card["name"]
        done, reason = is_verified_done(api_key, token, card)
        if done:
            print(f"  DELETE {cid} | {name} | {reason}")
            ok = delete_card(api_key, token, cid)
            if ok:
                deleted += 1
            else:
                failed += 1
        else:
            print(f"  MOVE->P5 {cid} | {name} | {reason}")
            ok = move_card(api_key, token, cid, P5_LIST_ID)
            if ok:
                moved += 1
                refresh_labels(api_key, token, cid)
                post_comment(
                    api_key,
                    token,
                    cid,
                    f"[AUTO] Moved to P5 - Low / Review because completion not verified. Reason: {reason}. Re-queue when done.",
                )
            else:
                failed += 1
    print(f"verified={verified} deleted={deleted} moved={moved} failed={failed}")


if __name__ == "__main__":
    main()
