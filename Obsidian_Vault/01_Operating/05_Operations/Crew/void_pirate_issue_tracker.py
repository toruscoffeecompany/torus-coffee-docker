#!/usr/bin/env python3
"""
VOID Pirate Trading Co — GitHub issue tracker for Torus crew.
Creates Trello cards for open issues in:
- VOIDPirateTradeCo/void-pirate-bots
- VOIDPirateTradeCo/void-pirate-legal
"""
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
TRELLO_CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
OODA_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "ooda_loop.log"


def now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    try:
        OODA_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{now_iso()}] {msg}"
        with open(OODA_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass


def load_trello_creds():
    text = TRELLO_CRED_FILE.read_text(errors="ignore")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello API credentials missing")
    return api_key, token


def load_github_token():
    try:
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        token = data.get("github_token", "")
        if not token:
            raise RuntimeError("GitHub token missing")
        return token
    except Exception as exc:
        raise RuntimeError(f"Failed to load GitHub token: {exc}")


def get_board_id(api_key, token, board_name):
    boards = requests.get("https://api.trello.com/1/members/me/boards", params={"key": api_key, "token": token}, timeout=15).json()
    board = next((b for b in boards if b["name"] == board_name), None)
    if not board:
        raise RuntimeError(f"Board {board_name} not found")
    return board["id"]


def get_or_create_list(api_key, token, board_id, name):
    lists = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=15).json()
    for l in lists:
        if l.get("name") == name:
            return l["id"]
    r = requests.post("https://api.trello.com/1/lists", data={"key": api_key, "token": token, "idBoard": board_id, "name": name}, timeout=15)
    if r.status_code == 200:
        return r.json()["id"]
    raise RuntimeError(f"Failed to create list {name}: {r.status_code}")


def main():
    api_key, token = load_trello_creds()
    gh_token = load_github_token()
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}"}

    # Use existing Torus_Ops board; create list if needed
    board_id = get_board_id(api_key, token, "Torus_Ops")
    list_id = get_or_create_list(api_key, token, board_id, "VOID Ops")

    repos = [
        "VOIDPirateTradeCo/void-pirate-bots",
        "VOIDPirateTradeCo/void-pirate-legal",
    ]
    created = 0
    for repo in repos:
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/issues", params={"state": "open", "per_page": 100}, headers=headers, timeout=15)
            if r.status_code != 200:
                log(f"VOID_ISSUES_FETCH_FAIL {repo} {r.status_code}")
                continue
            for issue in r.json():
                title = issue.get("title", "")
                number = issue.get("number", "")
                body = issue.get("body", "") or ""
                card_name = f"📨 [VOID:{repo}] #{number} {title}"
                card_data = {
                    "key": api_key,
                    "token": token,
                    "idList": list_id,
                    "name": card_name[:120],
                    "desc": body[:500],
                }
                card_r = requests.post("https://api.trello.com/1/cards", data=card_data, timeout=15)
                if card_r.status_code == 200:
                    log(f"VOID_TRELLO_CARD_CREATED: {card_name}")
                    created += 1
        except Exception as exc:
            log(f"VOID_ISSUES_ERROR {repo}: {exc}")
    log(f"VOID_TRELLO_CARDS_CREATED: {created}")


if __name__ == "__main__":
    raise SystemExit(main())
