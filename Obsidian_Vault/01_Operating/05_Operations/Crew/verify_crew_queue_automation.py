#!/usr/bin/env python3
"""Verify crew queue automation: transfer log, queue counts, and notification artifacts."""
import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
SCRIPT_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "Crew"
STATE = SCRIPT_DIR / "CREW_QUEUE_STATE.json"
LOG = VAULT / "10_Skills_Library" / "05_Operations" / "CREW_QUEUE_TRANSFER_LOG.json"
OUTBOX = VAULT / "02_Business_Operations" / "Communications" / "Outbox"
TRELLO_CRED = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"

WINDOW = timedelta(hours=4)

def load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def trello_request(url, params=None):
    text = TRELLO_CRED.read_text(errors="ignore")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    p = {"key": api_key, "token": token}
    if params:
        p.update(params)
    return requests.get(url, params=p, timeout=30).json()

def check():
    out = {}
    state = load_json(STATE, {})
    log = load_json(LOG, {"entries": []})
    entries = log.get("entries", [])
    now = datetime.now(timezone.utc)
    recent = [e for e in entries if datetime.fromisoformat(e.get("ts", now.isoformat())) >= now - WINDOW]
    counts = Counter(e.get("crew") for e in recent)
    out["last_run"] = state.get("last_run")
    out["processed_recent"] = len(recent)
    out["counts_recent"] = dict(counts)
    out["total_processed"] = state.get("processed_count")
    out["failed_count"] = state.get("failed_count")

    board = "6a70a3157d0db4214ac3f9a3"
    lists = trello_request(f"https://api.trello.com/1/boards/{board}/lists", {"fields": "name,id"})
    q_ids = {l["id"]: l["name"] for l in lists if "Queue" in l["name"]}
    q_card_counts = {}
    for lid, name in q_ids.items():
        cards = trello_request(f"https://api.trello.com/1/lists/{lid}/cards", {"fields": "name"})
        q_card_counts[name] = len(cards)
    out["queue_counts"] = q_card_counts

    out["latest_failures"] = state.get("failed", [])[:10]
    report = {
        "timestamp": now.isoformat(),
        "ok": bool(out.get("total_processed") and out.get("failed_count") == 0 and "Sir Green's Queue" in q_card_counts and "Sir Azure's Queue" in q_card_counts),
        "details": out,
        "summary": "queue transfer pipeline is active" if out.get("total_processed") else "no queue transfers yet",
    }
    path = SCRIPT_DIR / "CREW_QUEUE_VERIFICATION_REPORT.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check()
