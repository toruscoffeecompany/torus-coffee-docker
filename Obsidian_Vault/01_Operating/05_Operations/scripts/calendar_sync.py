#!/usr/bin/env python3
"""Intelligent scheduling optimizer: converts Trello/GitHub tickets into conflict-aware, workload-balanced calendar events."""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CALENDAR_SYNC_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/CALENDAR_SYNC_LOG.json"
TRELLO_CREDENTIALS = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
GITHUB_REPO = "toruscoffeecompany/Torus_Ops"
CALENDAR_ID = "primary"
LOOKAHEAD_DAYS = 14
WEEKLY_SCHEDULE_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/WEEKLY_SCHEDULE.json"
WORK_START_HOUR = 8
WORK_END_HOUR = 20
BLOCK_MINUTES_DEFAULT = 60
BLOCK_MINUTES_P0_P1 = 120
BLOCK_MINUTES_TOP10 = 150
MAX_DAILY_MINUTES = 8 * 60
PRIORITY_ORDER = {"p0": 0, "p1": 1, "top10": 2, "p2": 3, "p3": 4, "p4": 5, "p5": 6, "p6": 7}

TRELLO_BOARD_ID = "6a70a3157d0db4214ac3f9a3"
TRELLO_SYNC_LISTS = {"top 10 — focus fleet", "p1 - high / doing now"}
TRELLO_SYNC_LABELS = {"p0", "p1", "p2", "top 10"}
TRELLO_SKIP_LIST_FRAGMENTS = ["done", "future ideas", "sir azure's queue", "sir green's queue"]


def _redacted(text: str) -> str:
    return re.sub(r"(key|token|secret|password|webhook|pass)\s*[:=]\s*\S+", r"\1=[REDACTED]", text, flags=re.IGNORECASE)


def get_trello_credentials():
    raw = TRELLO_CREDENTIALS.read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines() if ln.startswith("`")]
    return lines[0].strip("`"), lines[2].strip("`")


def get_google_credentials():
    token_path = Path(r"C:\Users\torus\AppData\Local\hermes\google_token.json")
    client_secret = Path(r"C:\Users\torus\AppData\Local\hermes\google_client_secret.json")
    scopes = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), scopes)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _list_name_safe(list_name: str) -> str:
    return (list_name or "").strip().lower()


def _label_names_safe(labels):
    return [l.get("name", "").strip().lower() for l in labels or []]


def _is_relevant_trello(card: dict[str, Any], lists_by_id: dict[str, Any]) -> bool:
    list_name = _list_name_safe((lists_by_id.get(card.get("idList")) or {}).get("name", ""))
    if any(fragment in list_name for fragment in TRELLO_SKIP_LIST_FRAGMENTS):
        return False
    if list_name in TRELLO_SYNC_LISTS:
        return True
    label_names = _label_names_safe(card.get("labels", []))
    if any(name in label_names for name in TRELLO_SYNC_LABELS):
        return True
    return False


def _is_due_near_term(card: dict[str, Any]) -> bool:
    due = card.get("due")
    if not due:
        return False
    try:
        due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
        return due_dt <= datetime.now(timezone.utc) + timedelta(days=LOOKAHEAD_DAYS)
    except Exception:
        return False


def _fetch_trello_cards():
    key, token = get_trello_credentials()
    lists = requests.get(
        f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=15,
    ).json()
    cards = requests.get(
        f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards",
        params={
            "key": key,
            "token": token,
            "fields": "id,name,due,idList,labels,dateLastActivity",
            "limit": 1000,
            "filter": "all",
        },
        timeout=30,
    ).json()
    return lists, cards


def _fetch_github_issues():
    try:
        out = os.popen(f"gh issue list -R {GITHUB_REPO} --state open --limit 100 --json number,title,labels,assignees").read()
        data = json.loads(out)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[scheduler] GitHub fetch failed: {_redacted(str(e))}")
        return []


def _card_priority(card: dict[str, Any], lists_by_id: dict[str, Any]) -> tuple[int, int]:
    label_names = _label_names_safe(card.get("labels", []))
    list_name = _list_name_safe((lists_by_id.get(card.get("idList")) or {}).get("name", ""))
    if "top 10" in label_names or "top 10" in list_name:
        return PRIORITY_ORDER["top10"], 0
    for p in ("p0", "p1", "p2", "p3", "p4", "p5", "p6"):
        if p in label_names or p in list_name:
            return PRIORITY_ORDER[p], 0
    return PRIORITY_ORDER["p6"], 1


def _estimate_minutes(card: dict[str, Any]) -> int:
    text = f"{card.get('name', '')} {' '.join(l.get('name','') for l in card.get('labels', []))}".lower()
    if any(k in text for k in ["docker", "dashboard 502", "security", "blocked"]):
        return BLOCK_MINUTES_P0_P1
    if any(k in text for k in ["tax", "compliance", "calendar sync"]):
        return BLOCK_MINUTES_P0_P1
    if any(k in text for k in ["website", "inventory", "pos", "alert"]):
        return BLOCK_MINUTES_DEFAULT
    return BLOCK_MINUTES_DEFAULT


def _existing_calendar_event_set(service):
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=LOOKAHEAD_DAYS)).isoformat()
    page_token = None
    existing = set()
    while True:
        resp = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                maxResults=2500,
                pageToken=page_token,
            )
            .execute()
        )
        for e in resp.get("items", []):
            summary = (e.get("summary") or "").strip().lower()
            start = e.get("start", {})
            date = start.get("date") or start.get("dateTime", "").split("T")[0]
            if summary and date:
                existing.add((summary, date))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return existing


def _build_schedule(items):
    scheduled_days: dict[str, int] = {}
    placements: list[dict[str, Any]] = []
    for item in items:
        due = item.get("due_date")
        if not due:
            continue
        try:
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
        except Exception:
            continue
        work_date = due_dt.date()
        placed = False
        for offset in range(0, 7):
            candidate = (due_dt - timedelta(days=offset)).date()
            used = scheduled_days.get(str(candidate), 0)
            if used + item["minutes"] <= MAX_DAILY_MINUTES:
                start = datetime(candidate.year, candidate.month, candidate.day, WORK_START_HOUR, 0, tzinfo=timezone.utc)
                end = start + timedelta(minutes=item["minutes"])
                if end.hour > WORK_END_HOUR:
                    continue
                scheduled_days[str(candidate)] = used + item["minutes"]
                placements.append({
                    "item": item,
                    "start": start,
                    "end": end,
                    "date": candidate,
                    "minutes": item["minutes"],
                })
                placed = True
                break
        if not placed:
            candidate = due_dt.date()
            start = datetime(candidate.year, candidate.month, candidate.day, WORK_START_HOUR, 0, tzinfo=timezone.utc)
            end = start + timedelta(minutes=item["minutes"])
            scheduled_days[str(candidate)] = scheduled_days.get(str(candidate), 0) + item["minutes"]
            placements.append({
                "item": item,
                "start": start,
                "end": end,
                "date": candidate,
                "minutes": item["minutes"],
            })
    return placements


def _detect_conflicts(placements):
    by_day: dict[str, list[dict[str, Any]]] = {}
    for p in placements:
        by_day.setdefault(str(p["date"]), []).append(p)
    conflicts = []
    for day, items in by_day.items():
        items.sort(key=lambda x: x["start"])
        for i in range(len(items) - 1):
            if items[i]["end"] > items[i + 1]["start"]:
                conflicts.append({
                    "date": day,
                    "a": items[i]["item"].get("summary"),
                    "b": items[i + 1]["item"].get("summary"),
                })
                items[i]["end"] = items[i + 1]["start"]
    return conflicts, placements


def run_smart_sync(dry_run: bool = False):
    lists, cards = _fetch_trello_cards()
    lists_by_id = {l["id"]: l for l in lists}
    issues = _fetch_github_issues()

    tickets = []
    for c in cards:
        if not _is_relevant_trello(c, lists_by_id) or not _is_due_near_term(c):
            continue
        tickets.append({
            "source": "trello",
            "id": c["id"],
            "summary": c.get("name") or "Torus Task",
            "due_date": c.get("due"),
            "due": c.get("due"),
            "priority": _card_priority(c, lists_by_id)[0],
            "minutes": _estimate_minutes(c),
        })
    for issue in issues:
        label_names = [l.get("name", "").lower() for l in issue.get("labels", [])]
        if not any(label in TRELLO_SYNC_LABELS for label in label_names):
            continue
        tickets.append({
            "source": "github",
            "id": f"github-{issue['number']}",
            "summary": issue.get("title") or "GitHub Issue",
            "due": None,
            "priority": PRIORITY_ORDER["p3"],
            "minutes": BLOCK_MINUTES_DEFAULT,
        })

    tickets.sort(key=lambda x: (x["priority"], -(x["minutes"] or 0)))
    placements = _build_schedule(tickets)
    conflicts, placements = _detect_conflicts(placements)

    creds = get_google_credentials()
    service = build("calendar", "v3", credentials=creds)
    existing = _existing_calendar_event_set(service)

    created = 0
    skipped = 0
    failed = 0
    dry_run_lines = []
    for p in placements:
        key_ = (p["item"]["summary"].strip().lower(), str(p["date"]))
        if key_ in existing:
            skipped += 1
            continue
        start_iso = p["start"].isoformat()
        end_iso = p["end"].isoformat()
        event = {
            "summary": f"[{p['item']['source'].upper()}] {p['item']['summary']}",
            "description": (
                f"Auto-scheduled from {p['item']['source']} id={p['item']['id']}\n"
                f"Priority rank={p['item']['priority']} | Est={p['minutes']}m\n"
                "Generated by Torus intelligent scheduler"
            ),
            "start": {"dateTime": start_iso, "timeZone": "America/Chicago"},
            "end": {"dateTime": end_iso, "timeZone": "America/Chicago"},
        }
        if dry_run:
            dry_run_lines.append(f"{start_iso} -> {end_iso} | {event['summary']}")
            continue
        try:
            service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
            created += 1
            existing.add(key_)
        except Exception as e:
            failed += 1
            print(f"[scheduler] insert failed: {_redacted(str(e))}")

    log = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "mode": "smart_scheduler",
        "tickets_considered": len(tickets),
        "events_created": created,
        "events_skipped_existing": skipped,
        "events_failed": failed,
        "conflicts_detected": len(conflicts),
        "conflicts": conflicts[:20],
        "errors": [],
    }
    CALENDAR_SYNC_PATH.write_text(json.dumps(log, indent=2), encoding="utf-8")
    if dry_run_lines:
        print("\n".join(dry_run_lines))
    print(json.dumps({
        "tickets_considered": len(tickets),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "conflicts_detected": len(conflicts),
    }, indent=2))
    return log


if __name__ == "__main__":
    run_smart_sync(dry_run="--dry-run" in sys.argv)
