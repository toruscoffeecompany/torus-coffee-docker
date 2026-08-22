#!/usr/bin/env python3
"""Dashboard bridge: publish smart-ticket/OODA state for Captain's dashboard."""
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from master_ooda_loop import trello_cards, github_issues
except Exception:
    trello_cards = lambda: []
    github_issues = lambda: []

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TASKLIST = VAULT / "10_Skills_Library/05_Operations/MASTER_OODA_TASKLIST.json"
OUT = VAULT / "10_Skills_Library/05_Operations/logs/dashboard_smart_ticket_state.json"


def counts_from_trello():
    cards = []
    try:
        cards = trello_cards()
    except Exception:
        pass
    counts = {}
    for c in cards:
        key = (c.get("list") or "Unknown").strip()
        counts[key] = counts.get(key, 0) + 1
    return counts


def counts_from_github():
    issues = []
    try:
        issues = github_issues()
    except Exception:
        pass
    return {"GitHub Open": len(issues)}


def tasklist_summary():
    if TASKLIST.exists():
        try:
            data = json.loads(TASKLIST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"updated": datetime.now(timezone.utc).isoformat(), "tasks": []}
    else:
        data = {"updated": datetime.now(timezone.utc).isoformat(), "tasks": []}
    tasks = data.get("tasks", [])[:20]
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    return {
        "updated": data.get("updated"),
        "count": len(tasks),
        "pending": pending,
        "completed": completed,
        "tasks": tasks,
    }


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "timestamp": now,
        "trello_counts": counts_from_trello(),
        "github_counts": counts_from_github(),
        "tasklist": tasklist_summary(),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"DASHBOARD_BRIDGE_WRITE {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
