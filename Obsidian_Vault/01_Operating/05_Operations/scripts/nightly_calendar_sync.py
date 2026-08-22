#!/usr/bin/env python3
"""
nightly_calendar_sync.py — Batch Google Calendar sync from Torus_Ops Trello cards.

Behavior:
  - Runs daily at 02:00 via Windows schtasks
  - Syncs near-term P1 + Top 10 Trello cards to Google Calendar
  - Batch writes: 10 cards per batch, 5s delay between batches (avoids rate limits)
  - Uses redacted Google API key from vault
  - NEVER passes 'timeout' into googleapiclient discovery.build() (known crash point)
  - Dry-run mode: python nightly_calendar_sync.py --dry-run

Usage:
  python nightly_calendar_sync.py            # full sync
  python nightly_calendar_sync.py --dry-run  # preview only, no writes

Scope:
  - Top 10 — Focus Fleet (max 10 cards)
  - P1 - High / Doing Now (first 30 cards)
  - Only cards with due dates
  - Deduplicates by (summary, date) — skips existing events
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── CONFIG ──────────────────────────────────────────────────────────────────
VAULT = Path("D:/Work/Torus Coffee Company LLC")
CREDS_FILE = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"

# Trello
TORUS_OPS_BOARD = "6a70a3157d0db4214ac3f9a3"
TOP10_LIST = "6a74cbd3aa052ed2b30c5644"
P1_LIST = "6a74cbd5e3d54d2d08be82e7"
DONE_LIST = "6a70a32a723c0312a3d5fbb4"

# Limits (per user: "we dont need a live update all the time")
TOP10_LIMIT = 10
P1_LIMIT = 30
BATCH_SIZE = 10
BATCH_DELAY_SEC = 5

# Google Calendar
GOOGLE_API_KEY = "[REDACTED]"  # populated from vault at read time
GOOGLE_CALENDAR_ID = "primary"
SYNC_LOG = VAULT / "10_Skills_Library/05_Operations/last_calendar_sync.json"


def load_credentials():
    """Read Trello key + token from vault creds file."""
    text = CREDS_FILE.read_text()
    lines = text.splitlines()
    api_key = token = None
    for i, l in enumerate(lines):
        if "API Key" in l and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in l and "OAuth" not in l and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise ValueError("Trello credentials not found in vault")
    return api_key, token


def get_cards_with_due_dates(api_key, token, list_id, max_cards=10):
    """Fetch cards from a list, return those with valid due dates."""
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {
        "key": api_key,
        "token": token,
        "fields": "name,desc,due,id,labels",
    }
    resp = requests.get(url, params=params, timeout=15)
    if not resp.ok:
        print(f"  ERROR fetching list {list_id[:12]}: {resp.status_code}")
        return []
    cards = resp.json()
    # Filter: has due date, not in Done state, not already closed
    result = []
    for c in cards:
        due = c.get("due")
        if due and due.strip():
            # Check if already done (label or list)
            labels = [l.get("name", "") for l in c.get("labels", [])]
            if not any("Done" in la for la in labels):
                result.append(c)
        if len(result) >= max_cards:
            break
    return result


def parse_due_date(due_str):
    """Parse Trello ISO date → Google Calendar RFC3339 date string."""
    try:
        dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except (ValueError, AttributeError):
        return None


def load_existing_events():
    """Load previously-synced events to prevent duplicates."""
    if SYNC_LOG.exists():
        data = json.loads(SYNC_LOG.read_text())
        return {e.get("unique_key"): e for e in data.get("synced", [])}
    return {}


def save_sync_log(synced):
    """Persist sync state for deduplication."""
    SYNC_LOG.write_text(json.dumps({"synced": synced, "last_run": datetime.now(timezone.utc).isoformat()}, indent=2))


def build_google_service():
    """Create Google Calendar service — NO timeout param (known crash)."""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    # Try service account key first
    sa_key_path = VAULT / "01_Operating/Operating Paperwork/google_service_account.json"
    if sa_key_path.exists():
        creds = Credentials.from_service_account_file(
            str(sa_key_path),
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        # NOTE: explicitly omitting timeout — it crashes googleapiclient
        service = build("calendar", "v3", credentials=creds)
        return service

    # Fallback: check for alert mechanism
    print("  SKIP: No Google Calendar write credentials available")
    print("  ALERT: Nightly Calendar Sync scheduled @02:00 but NO CREDENTIALS FOUND.")
    print("  Fix: place service account JSON at D:/Work/Torus Coffee Company LLC/Obsidian_Vault/01_Operating/Operating Paperwork/google_service_account.json")
    print("  AND share target calendar with that service account email.")
    return None


def main():
    parser = argparse.ArgumentParser(description="Nightly Google Calendar sync from Trello")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no calendar writes")
    args = parser.parse_args()

    print(f"[{datetime.now(timezone.utc).isoformat()}] Nightly Calendar Sync starting")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")

    # Step 1: Load Trello credentials
    api_key, token = load_credentials()
    print(f"  Trello auth: loaded (key={api_key[:8]}...)")

    # Step 2: Fetch cards from Top 10 + P1
    print("  Fetching Top 10 cards...")
    top10_cards = get_cards_with_due_dates(api_key, token, TOP10_LIST, TOP10_LIMIT)
    print(f"  Top 10 cards with due dates: {len(top10_cards)}")

    print("  Fetching P1 cards...")
    p1_cards = get_cards_with_due_dates(api_key, token, P1_LIST, P1_LIMIT)
    print(f"  P1 cards with due dates: {len(p1_cards)}")

    all_cards = top10_cards + p1_cards
    print(f"  Total cards to sync: {len(all_cards)}")

    if args.dry_run:
        print("\n  DRY RUN — cards that would be synced:")
        for i, c in enumerate(all_cards[:10]):
            print(f"    {i+1}. {c['name'][:60]} | due={c.get('due','')[:10]}")
        print(f"  ... ({len(all_cards)} total)")
        return

    # Step 3: Connect to Google Calendar
    service = build_google_service()
    if service is None:
        print("  SKIP: No Google Calendar write credentials available")
        print("  To enable: place service_account.json in vault + share calendar with service account email")
        return

    # Step 4: Process in batches of 10, 5s delay
    existing = load_existing_events()
    synced = []

    for batch_start in range(0, len(all_cards), BATCH_SIZE):
        batch = all_cards[batch_start:batch_start + BATCH_SIZE]
        print(f"\n  Batch {batch_start // BATCH_SIZE + 1}: {len(batch)} cards")

        for card in batch:
            # Build event
            summary = card["name"][:250]
            due_str = card.get("due", "")
            start_date = parse_due_date(due_str)
            if not start_date:
                continue

            # Deduplicate key: (summary, date)
            unique_key = f"{summary}|{start_date[:10]}"
            if unique_key in existing:
                print(f"    SKIP (dup): {summary[:45]}")
                continue

            event = {
                "summary": summary,
                "description": card.get("desc", "")[:500] or "Torus Coffee task from Trello",
                "start": {
                    "dateTime": start_date,
                    "timeZone": "America/Chicago",
                },
                "end": {
                    "dateTime": start_date,
                    "timeZone": "America/Chicago",
                },
            }

            try:
                created = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
                print(f"    SYNCED: {summary[:45]} → event {created.get('id','?')[:8]}")
                synced.append({"unique_key": unique_key, "event_id": created.get("id"), "card_id": card["id"]})
            except Exception as e:
                print(f"    FAIL: {summary[:45]} → {e}")

        # Save progress after each batch
        all_synced = list(load_existing_events().values()) + synced
        save_sync_log(all_synced)

        if batch_start + BATCH_SIZE < len(all_cards):
            print(f"    Sleeping {BATCH_DELAY_SEC}s (batch delay)...")
            time.sleep(BATCH_DELAY_SEC)

    print(f"\n[{datetime.now(timezone.utc).isoformat()}] Sync complete: {len(synced)} events created")


if __name__ == "__main__":
    main()
