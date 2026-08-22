from pathlib import Path
import requests
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import subprocess

REPO_ROOT = Path(".").resolve()
TRELLO_CREDENTIALS = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
creds = TRELLO_CREDENTIALS.read_text(encoding="utf-8")
lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
key = lines[0].strip("`")
token = lines[2].strip("`")
board_id = "6a70a3157d0db4214ac3f9a3"

# Trello summary
lists = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=15,
).json()
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels,dateLastActivity,due", "limit": 1000, "filter": "all"},
    timeout=30,
).json()
list_counts = Counter(c.get("idList") for c in cards)
name_groups = defaultdict(list)
for c in cards:
    name_groups[c["name"].strip().lower()].append(c)
dup_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
active_dups = 0
for name, group in dup_groups.items():
    newest = max(group, key=lambda c: c.get("dateLastActivity") or "")
    active_dups += sum(1 for c in group if c["id"] != newest["id"])

# Local inbox/outbox counts
inbox = list((REPO_ROOT / "02_Business_Operations/Communications/Inbox").glob("*"))
outbox = list((REPO_ROOT / "02_Business_Operations/Communications/Outbox").glob("*"))
comms_bus = REPO_ROOT / "02_Business_Operations/Communications/Outbox/SHARED_COMMS_BUS.json"

# Calendar check
p = Path(r"C:\Users\torus\AppData\Local\hermes\google_token.json")
calendar_ok = False
calendar_count = 0
if p.exists():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds_obj = Credentials.from_authorized_user_file(str(p), ["https://www.googleapis.com/auth/calendar"])
        if creds_obj.valid:
            service = build("calendar", "v3", credentials=creds_obj)
            now = datetime.now(timezone.utc).isoformat()
            events = service.events().list(calendarId="primary", timeMin=now, maxResults=2500, singleEvents=True).execute()
            calendar_count = len(events.get("items", []))
            calendar_ok = True
    except Exception as e:
        calendar_ok = str(e)

# GitHub
github_ok = False
github_issues = 0
try:
    out = subprocess.check_output(
        ["gh", "issue", "list", "-R", "toruscoffeecompany/Torus_Ops", "--state", "open", "--limit", "100", "--json", "number"],
        text=True, timeout=30
    )
    issues = json.loads(out)
    github_issues = len(issues)
    github_ok = True
except Exception as e:
    github_ok = str(e)

report = {
    "timestamp": datetime.now().isoformat(),
    "trello": {
        "total": len(cards),
        "lists": {l["name"]: list_counts.get(l["id"], 0) for l in lists},
        "duplicate_groups": len(dup_groups),
        "active_duplicate_cards": active_dups,
    },
    "inbox": {
        "inbox_count": len(inbox),
        "outbox_count": len(outbox),
        "comms_bus_exists": comms_bus.exists(),
    },
    "calendar": {
        "ok": calendar_ok is True,
        "upcoming_count": calendar_count,
        "error": None if calendar_ok is True else str(calendar_ok),
    },
    "github": {
        "ok": github_ok is True,
        "open_issues": github_issues,
        "error": None if github_ok is True else str(github_ok),
    },
}
print(json.dumps(report, indent=2, default=str))
