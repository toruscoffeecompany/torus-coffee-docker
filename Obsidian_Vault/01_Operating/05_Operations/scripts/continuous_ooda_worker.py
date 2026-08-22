#!/usr/bin/env python3
"""
Torus Coffee Continuous OODA Worker
One-card/one-issue-at-a-time priority processor.
Picks highest-priority actionable item from Trello or GitHub, advances it, then stops.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from subprocess import CREATE_NO_WINDOW

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
OODA_LOG = VAULT / "10_Skills_Library/05_Operations/logs/continuous_ooda_worker.log"
STATE_FILE = VAULT / "10_Skills_Library/05_Operations/continuous_ooda_state.json"

REPO = "toruscoffeecompany/Torus_Ops"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"
# List IDs
TOP10_LIST = "6a74cbd3aa052ed2b30c5644"
P0_LIST = "6a74cbd440270147ff04bd5b"
P1_LIST = "6a74cbd5e3d54d2d08be82e7"
P2_LIST = "6a74cbd4148f814483a64589"
P3_LIST = "6a70a32923622d3e00107d70"
P5_LIST = "6a74f124364b0cbd6b9c7117"
P6_LIST = "6a74f1253664a10a9e17bb57"

LIST_PRIORITY = {
    TOP10_LIST: 0, P0_LIST: 1, P1_LIST: 2, P2_LIST: 3, P3_LIST: 4, P5_LIST: 5, P6_LIST: 6
}

LABEL_MAP = {
    "P0": "6a74cc10430afd9940c72bae",
    "P1": "6a70acc569135c796d8eba5d",
    "P2": "6a70acc56f143597877f576e",
    "P3": "6a70acc6fddcac79f411267f",
    "P5": "6a74f124364b0cbd6b9c7117",
    "P6": "6a74f1253664a10a9e17bb57",
    "Top 10": "6a74c9ad1518ad0f9e645fc5",
    "Blocked": "6a74cc14af961cb89bd1d7ec",
    "Waiting": "6a74cc126b64962ee8c0aa27",
    "On-Hold": "6a74cc14a5b2bcf031060256",
    "Doing": "6a74cc10d445ec00d6a33bd5",
    "automation": "6a739cca616c68bad376bcef",
    "ops": "6a739ccb921a250c77d804ea",
    "miss-pink": "6a74dd623356f01be75f7d0c",
}

STUCK_HOURS = 48


def log(msg: str) -> None:
    try:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        with open(OODA_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass


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


def api_get(url: str, params: dict) -> list | dict:
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(url: str, params: dict) -> dict:
    r = requests.post(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_put(url: str, params: dict) -> dict:
    r = requests.put(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def update_card(card_id: str, api_key: str, token: str, **fields) -> dict:
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {"key": api_key, "token": token}
    params.update(fields)
    return api_put(url, params)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            STATE_FILE.replace(STATE_FILE.with_suffix(".bad.json"))
    return {"last_card_id": None, "last_issue_number": None, "last_run": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def parse_iso(dt_str: str) -> datetime | None:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def card_tags(card: dict) -> set[str]:
    return {l.get("name", "") for l in card.get("labels", []) if l.get("name")}


def add_label(card_id: str, label_id: str, api_key: str, token: str) -> None:
    api_post(
        f"https://api.trello.com/1/cards/{card_id}/idLabels",
        {"key": api_key, "token": token, "value": label_id},
    )


def remove_label(card_id: str, label_id: str, api_key: str, token: str) -> None:
    requests.delete(
        f"https://api.trello.com/1/cards/{card_id}/idLabels/{label_id}",
        params={"key": api_key, "token": token},
        timeout=20,
    )


def move_card(card_id: str, list_id: str, api_key: str, token: str) -> None:
    api_post(
        f"https://api.trello.com/1/cards/{card_id}",
        {"key": api_key, "token": token, "idList": list_id},
    )


def set_due(card_id: str, iso_due: str, api_key: str, token: str) -> None:
    api_put(
        f"https://api.trello.com/1/cards/{card_id}",
        {"key": api_key, "token": token, "due": iso_due},
    )


def comment_card(card_id: str, text: str, api_key: str, token: str) -> None:
    api_post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        {"key": api_key, "token": token, "text": text},
    )


def process_trello(api_key: str, token: str) -> tuple[bool, str | None]:
    """Process one Trello card. Returns (work_done, card_id)."""
    lists = {l["id"]: l for l in api_get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/lists",
        {"key": api_key, "token": token, "fields": "name,id,closed"},
    )}
    cards = api_get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
        {"key": api_key, "token": token, "fields": "name,idList,desc,dateLastActivity,due,labels,url,closed"},
    )
    open_cards = [c for c in cards if not c.get("closed")]
    
    # Promotion: Top 10 exact cap — DISABLED here (handled by smart_ticket_cycle.py
    # every 5 min to prevent duplicate promotions between the two scripts)
    top10 = [c for c in open_cards if c.get("idList") == TOP10_LIST]
    # Skip promotion in continuous worker — smart_ticket_cycle handles it
    # This prevents race conditions between the two scripts creating duplicate cards
    p1p2 = []
    
    # Downgrade stuck cards
    now = datetime.now(timezone.utc)
    stuck = []
    for c in open_cards:
        if c.get("idList") not in (TOP10_LIST, P0_LIST, P1_LIST, P2_LIST):
            continue
        tags = card_tags(c)
        if any(t in tags for t in ("Blocked", "Waiting", "On-Hold", "Sir Green's Queue", "Sir Azure's Queue")):
            last = parse_iso(c.get("dateLastActivity", ""))
            if last and (now - last) > timedelta(hours=STUCK_HOURS):
                stuck.append(c)
        elif c.get("idList") in (P1_LIST, P2_LIST, TOP10_LIST):
            last = parse_iso(c.get("dateLastActivity", ""))
            if last and (now - last) > timedelta(hours=STUCK_HOURS * 2):
                stuck.append(c)
    
    for c in stuck:
        tags = card_tags(c)
        if any(t in tags for t in ("Blocked", "Waiting", "Sir Green's Queue", "Sir Azure's Queue")):
            target_list = P6_LIST
            target_label = LABEL_MAP["P6"]
            reason = "External or explicit blocker with no recent progress; cycling back via follow-up."
            follow_days = 7
        else:
            target_list = P5_LIST
            target_label = LABEL_MAP["P5"]
            reason = "Stale high-priority ticket with no recent activity; moved to review."
            follow_days = 14
        
        follow_up = (now + timedelta(days=follow_days)).isoformat()
        move_card(c["id"], target_list, api_key, token)
        for lbl_id in (LABEL_MAP["Top 10"], LABEL_MAP["P0"], LABEL_MAP["P1"], LABEL_MAP["P2"], 
                      LABEL_MAP["P3"], LABEL_MAP["P5"], LABEL_MAP["P6"]):
            remove_label(c["id"], lbl_id, api_key, token)
        add_label(c["id"], target_label, api_key, token)
        set_due(c["id"], follow_up, api_key, token)
        comment_card(
            c["id"],
            f"[{now.isoformat()}] Auto-downgraded. Follow-up: {follow_up}. {reason}",
            api_key, token,
        )
        log(f"DOWNGRADED {c['id']} {c['name']} -> {target_list} due={follow_up}")
        return True, c["id"]
    
    # Work next actionable card
    work_order = [TOP10_LIST, P0_LIST, P1_LIST, P2_LIST, P3_LIST]
    next_card = None
    for lid in work_order:
        candidates = [c for c in open_cards if c.get("idList") == lid 
                      and "Blocked" not in card_tags(c) and "Waiting" not in card_tags(c)]
        if not candidates:
            continue
        candidates.sort(key=lambda c: (
            parse_iso(c.get("due", "")) or datetime(2099, 1, 1, tzinfo=timezone.utc),
            c.get("dateLastActivity", ""),
        ))
        next_card = candidates[0]
        break
    
    if not next_card:
        log("NO_ACTIONABLE_TRELLO_CARDS")
        return False, None
    
    # Skip cards already commented within last 10 minutes to avoid spam-loop on bumped activity
    recent_comments = [
        a for a in api_get(
            f"https://api.trello.com/1/cards/{next_card['id']}/actions",
            {"key": api_key, "token": token, "filter": "commentCard", "limit": 5, "fields": "date"},
        )
        if parse_iso(a.get("date", "")) and (now - parse_iso(a.get("date", ""))) < timedelta(minutes=10)
    ]
    if recent_comments:
        # Try next candidate in same list, or move to next list
        for lid in work_order[work_order.index(next_card.get("idList")):]:
            candidates = [c for c in open_cards if c.get("idList") == lid 
                          and c.get("id") != next_card.get("id")
                          and "Blocked" not in card_tags(c) and "Waiting" not in card_tags(c)]
            candidates = [
                c for c in candidates
                if not any(
                    parse_iso(a.get("date", "")) and (now - parse_iso(a.get("date", ""))) < timedelta(minutes=10)
                    for a in api_get(
                        f"https://api.trello.com/1/cards/{c['id']}/actions",
                        {"key": api_key, "token": token, "filter": "commentCard", "limit": 5, "fields": "date"},
                    )
                )
            ]
            if candidates:
                candidates.sort(key=lambda c: (
                    parse_iso(c.get("due", "")) or datetime(2099, 1, 1, tzinfo=timezone.utc),
                    c.get("dateLastActivity", ""),
                ))
                next_card = candidates[0]
                break
        else:
            log("NO_NEW_ACTIONABLE_CARDS")
            return False, None
    
    next_action = "Review card description/evidence; if executable locally, advance one step."
    if next_card.get("idList") == TOP10_LIST:
        next_action = "Top 10 active: verify blockers, collect evidence, advance toward completion."
    elif next_card.get("idList") == P0_LIST:
        next_action = "P0 active: triage incident and restore service or reroute if blocked."
    elif next_card.get("idList") == P1_LIST:
        next_action = "P1 active: complete next executable subtask or gather missing evidence."
    elif next_card.get("idList") == P2_LIST:
        next_action = "P2 active: advance one concrete step this week."
    elif next_card.get("idList") == P3_LIST:
        next_action = "P3 follow-up: update status or convert to actionable P2 if ready."
    
    comment = (
        f"[{now.isoformat()}] Smart ticket status: {lists.get(next_card.get('idList',''),{}).get('name','Unknown')}.\n"
        f"Next action: {next_action}\n"
        f"Evidence needed: screenshot, curl output, or file path.\n"
        f"Card: {next_card.get('url','')}"
    )
    comment_card(next_card["id"], comment, api_key, token)
    log(f"TRELLO_STATUS_UPDATED {next_card['id']} {next_card['name']}")
    return True, next_card["id"]


def process_github() -> tuple[bool, int | None]:
    """Process one GitHub issue. Returns (work_done, issue_number)."""
    try:
        out = subprocess.check_output(
            ["gh", "issue", "list", "-R", REPO, "--state", "open", "--limit", "100",
             "--json", "number,title,labels,updatedAt"],
            text=True, timeout=30,
            creationflags=CREATE_NO_WINDOW,
        )
        issues = json.loads(out)
    except Exception as e:
        log(f"GITHUB_LIST_ERROR: {e}")
        return False, None
    
    if not issues:
        return False, None
    
    # Sort by priority label then update date
    def issue_priority(issue):
        labels = [l["name"] for l in issue.get("labels", [])]
        if "inbox" in labels:
            return 99
        if "P0" in labels:
            return 0
        if "P1" in labels:
            return 1
        if "P2" in labels:
            return 2
        if "P3" in labels:
            return 3
        return 4
    
    issues.sort(key=lambda i: (issue_priority(i), i.get("updatedAt", "")))
    issue = issues[0]
    
    number = issue["number"]
    title = issue["title"]
    labels = [l["name"] for l in issue.get("labels", [])]
    
    # Add status comment
    next_action = "Review issue description and advance one executable step."
    if "P0" in labels:
        next_action = "P0 critical: triage incident and restore service or reroute if blocked."
    elif "P1" in labels:
        next_action = "P1 active: complete next executable subtask or gather missing evidence."
    elif "P2" in labels:
        next_action = "P2 active: advance one concrete step this week."
    elif "inbox" in labels:
        next_action = "Inbox: categorize and route to appropriate priority lane."
    
    comment = (
        f"[{datetime.now(timezone.utc).isoformat()}] Continuous OODA status.\n"
        f"Next action: {next_action}\n"
        f"Evidence needed: screenshot, curl output, or file path.\n"
        f"Issue: #{number} {title}"
    )
    
    try:
        subprocess.run(
            ["gh", "issue", "comment", str(number), "-R", REPO, "--body", comment],
            text=True, timeout=30, check=True,
            creationflags=CREATE_NO_WINDOW,
        )
        log(f"GITHUB_STATUS_UPDATED #{number} {title}")
        return True, number
    except subprocess.CalledProcessError as e:
        log(f"GITHUB_COMMENT_ERROR #{number}: {e}")
        return False, None


def main() -> int:
    log("CONTINUOUS_OODA_WORKER_START")
    state = load_state()
    now = datetime.now(timezone.utc)
    
    work_done = False
    worked_card_id = None
    worked_issue_number = None
    
    # Try Trello first (higher priority queue)
    try:
        api_key, token = load_creds()
        work_done, worked_card_id = process_trello(api_key, token)
    except Exception as e:
        log(f"TRELLO_ERROR: {e}")
    
    # If no Trello work, try GitHub
    if not work_done:
        work_done, worked_issue_number = process_github()
    
    if worked_card_id:
        state["last_card_id"] = worked_card_id
    if worked_issue_number:
        state["last_issue_number"] = worked_issue_number
    save_state({
        "last_card_id": state.get("last_card_id"),
        "last_issue_number": state.get("last_issue_number"),
        "last_run": now.isoformat(),
        "last_source": "trello" if work_done else ("github" if work_done else "none"),
    })
    
    log("CONTINUOUS_OODA_WORKER_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
