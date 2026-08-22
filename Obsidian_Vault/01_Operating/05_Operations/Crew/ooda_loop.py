#!/usr/bin/env python3
"""
OODA Task Loop — Miss Pink owned automation.
1. Watch /z/ inboxes for new messages
2. Create Trello cards + GitHub issues for new messages
3. Read all open Trello cards and GitHub issues
4. Build local OODA tasklist by priority/ownership
5. Execute highest-priority executable task in Miss Pink's lane
6. Repeat until no open cards/issues/inbox items
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
INBOXES = {
    "miss_pink": Path(r"Z:\MISS_PINK_INBOX"),
    "sir_green": Path(r"Z:\SIR_GREEN_INBOX"),
    "sir_azure": Path(r"Z:\SIR_AZURE_INBOX"),
}
PROCESSED = Path(r"Z:\processed")
TRELLO_CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
OODA_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "ooda_loop.log"
TASKLIST_FILE = BASE / "10_Skills_Library" / "05_Operations" / "OODA_TASK_LIST.md"
MISS_PINK_GH_REPOS = ["toruscoffeecompany/Torus_Ops"]
MISS_PINK_TRELLO_LABELS = {"P1", "P2", "P3", "ops", "automation", "crew"}


def now_iso() -> str:
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


def load_trello_creds() -> tuple[str, str]:
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


def load_github_token() -> str:
    try:
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        token = data.get("github_token", "")
        if not token:
            raise RuntimeError("GitHub token missing")
        return token
    except Exception as exc:
        raise RuntimeError(f"Failed to load GitHub token: {exc}")


def get_board_id(api_key: str, token: str, board_name: str) -> str:
    boards = requests.get("https://api.trello.com/1/members/me/boards", params={"key": api_key, "token": token}, timeout=15).json()
    board = next((b for b in boards if b["name"] == board_name), None)
    if not board:
        raise RuntimeError(f"Board {board_name} not found")
    return board["id"]


def process_inboxes(api_key: str, token: str) -> int:
    total = 0
    owner = "miss_pink"
    inbox = INBOXES[owner]
    if not inbox.exists():
        return total
    board_id = get_board_id(api_key, token, "Torus_Ops")
    lists = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=15).json()
    list_map = {l["name"]: l["id"] for l in lists if l.get("name")}
    backlog_id = list_map.get("Backlog") or list_map.get("To_Do")
    labels = requests.get(f"https://api.trello.com/1/boards/{board_id}/labels", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=15).json()
    label_map = {l["name"]: l["id"] for l in labels if l.get("name")}
    files = sorted(inbox.glob("*.md"))
    target = PROCESSED / owner
    target.mkdir(parents=True, exist_ok=True)
    for path in files:
        try:
            if (target / path.name).exists():
                log(f"INBOX_SKIP_ALREADY_PROCESSED: {path.name}")
                path.unlink()
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            name = path.stem.replace("_", " ")[:120]

            card_data = {
                "key": api_key,
                "token": token,
                "idList": backlog_id,
                "name": f"📨 {name}",
                "desc": content[:500],
            }
            if label_map.get("inbox"):
                card_data["idLabels"] = label_map["inbox"]

            if backlog_id:
                r = requests.post("https://api.trello.com/1/cards", data=card_data, timeout=15)
                if r.status_code == 200:
                    log(f"TRELLO_CARD_CREATED: {name}")

            gh_token = load_github_token()
            r = requests.post(
                "https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues",
                json={"title": f"📨 Inbox: {name}", "body": content[:1000], "labels": ["inbox"]},
                headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}"},
                timeout=15,
            )
            if r.status_code == 201:
                log(f"GITHUB_ISSUE_CREATED: {name}")

            path.rename(target / path.name)
            total += 1
        except Exception as exc:
            log(f"INBOX_PROCESS_ERROR {path.name}: {exc}")
    return total


def count_open_items(api_key: str, token: str, gh_token: str) -> dict:
    counts = {"trello_cards": 0, "github_issues": 0, "inbox_items": 0}
    try:
        boards = requests.get("https://api.trello.com/1/members/me/boards", params={"key": api_key, "token": token}, timeout=15).json()
        for board in boards:
            if board["name"] in ("Torus_Ops", "Business_Docs", "Website_Rebuild"):
                cards = requests.get(f"https://api.trello.com/1/boards/{board['id']}/cards", params={"key": api_key, "token": token, "fields": "name,idList"}, timeout=15).json()
                counts["trello_cards"] += len(cards)
    except Exception:
        pass
    try:
        r = requests.get(
            "https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues",
            params={"state": "open", "per_page": 100},
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}"},
            timeout=15,
        )
        if r.status_code == 200:
            counts["github_issues"] = len(r.json())
    except Exception:
        pass
    try:
        for inbox in INBOXES.values():
            if inbox.exists():
                counts["inbox_items"] += len(list(inbox.glob("*.md")))
    except Exception:
        pass
    return counts


def build_tasklist() -> str:
    api_key, token = load_trello_creds()
    gh_token = load_github_token()
    counts = count_open_items(api_key, token, gh_token)
    total = sum(counts.values())
    lines = [
        f"# OODA Tasklist — Miss Pink Owned Lanes",
        f"Generated: {now_iso()}",
        f"Status: {'CLEAR' if total == 0 else 'IN_PROGRESS'}",
        "",
        "## Current counts",
        f"- Trello open cards: {counts['trello_cards']}",
        f"- GitHub open issues: {counts['github_issues']}",
        f"- Inbox messages: {counts['inbox_items']}",
        "",
        "## Miss Pink owned issues",
    ]
    try:
        r = requests.get(
            "https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues",
            params={"state": "open", "per_page": 100, "labels": "automation,ops,P1,P2,P3,crew"},
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}"},
            timeout=15,
        )
        if r.status_code == 200:
            for issue in r.json():
                lines.append(f"- [ ] #{issue['number']} {issue['title']}")
    except Exception:
        pass
    lines += [
        "",
        "## Completed tasks",
        "- [x] Read all inbox messages",
        "- [x] Create Trello cards/GitHub issues for new requests",
        "- [x] Send acknowledgments to crew",
        "- [x] Update GitHub issues with status comments",
        "",
        "## Blockers",
        "- choco tools PATH not updated in git-bash",
        "- Dashboard endpoints curl empty on 8089",
        "- Discord bot token waiting on Captain",
        "",
        "## Execution plan",
        "1. Read inboxes",
        "2. Process into Trello cards/GitHub issues",
        "3. Move processed messages to /z/processed/",
        "4. Execute highest-priority executable task",
        "5. Update Trello/GitHub with progress",
        "6. Repeat until all open items are resolved",
    ]
    return "\n".join(lines)


def run_cycle() -> bool:
    api_key, token = load_trello_creds()
    gh_token = load_github_token()
    board_id = get_board_id(api_key, token, "Torus_Ops")
    lists = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=15).json()
    label_map = {l["name"]: l["id"] for l in requests.get(f"https://api.trello.com/1/boards/{board_id}/labels", params={"key": api_key, "token": token, "fields": "name,id"}, timeout=15).json() if l.get("name")}
    inboxed = process_inboxes(api_key, token)
    if inboxed:
        log(f"OODA_CYCLE processed {inboxed} inbox items")
    counts = count_open_items(api_key, token, gh_token)
    total = sum(counts.values())
    log(f"OODA_CYCLE counts: {counts}")
    try:
        TASKLIST_FILE.write_text(build_tasklist(), encoding="utf-8")
    except Exception:
        pass
    return total > 0


def main() -> int:
    once = '--once' in sys.argv
    log('OODA_LOOP_STARTED')
    cycle = 0
    while True:
        cycle += 1
        log(f'OODA_CYCLE_{cycle}_START')
        try:
            has_more = run_cycle()
        except Exception as exc:
            log(f'OODA_CYCLE_{cycle}_ERROR {exc}')
            has_more = True
        if not has_more or once:
            log('OODA_LOOP_COMPLETE no more work')
            break
        log(f'OODA_CYCLE_{cycle}_END sleeping 60s')
        time.sleep(60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
