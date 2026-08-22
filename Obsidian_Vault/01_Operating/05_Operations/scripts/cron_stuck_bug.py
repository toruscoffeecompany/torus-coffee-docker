"""File CRON SCHEDULER STUCK bug + verify restarts."""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return None

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

# ─── File bug: Cron scheduler stuck ───────────────────────────────────────────────
list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
desc = f"""**Bug Hunt v6 — {ts}**

**Issue:** Cron scheduler STUCK — missed 5+ hours of scheduled runs.

**Evidence:**
- Scanner cron (81e14266bda0): last_run_at=01:55:58Z, last_status=ERROR, next_run_at=02:00:58Z
  (Current time: {ts} — next_run is 5+ hours in the PAST!)
- OODA cron (4692924e5258): last_run_at=01:55:58Z, last_status=ERROR, next_run_at=02:00:58Z
  (Same 5+ hour gap!)
- scanner_health.json last_run: 06:39:42Z — that was a MANUAL run, not cron

**Impact:**
- Signal scanner NOT running (12 tickers not scanned)
- OODA loop NOT running (no card verification, no system checks)
- Bug cards pile up unchecked
- Business cards at risk (though protection now active)

**Root cause:** The cron scheduler appears to have a bug where it stops rescheduling
after the last_run_at time. The next_run_at is set in the past, meaning the scheduler
does not fire.

**Fix:**
1. Investigate cron scheduler — why next_run_at went stale
2. Add cron health check to OODA (verify next_run is within 5 min of now)
3. Resume + manually fire both jobs

**Status:** Manually resumed both jobs at {ts}. Monitoring.

— 🦜"""
data = json.dumps({"idList": list_id, "name": "CRON SCHEDULER STUCK — scanner + OODA crons missed 5+ hours (last_run 01:55Z, status=error, next_run in PAST)", "desc": desc, "pos": "top"}).encode()
req = urllib.request.Request(url, data=data)
req.add_header("Content-Type", "application/json")
try:
    result = json.loads(urllib.request.urlopen(req, timeout=10).read())
    cid = result["id"]
    for lbl in ["sir-green", "P1", "Bug"]:
        lid = get_label_id(VOID, lbl)
        if lid:
            lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                data=json.dumps({"value": lid}).encode(), method='POST')
            lb_req.add_header("Content-Type", "application/json")
            try: urllib.request.urlopen(lb_req, timeout=10)
            except: pass
    print(f"  ✅ Filed: Cron stuck bug (card {cid[:12]})")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# ─── Verify manual cron runs ─────────────────────────────────────────────────────
print("\n--- Verifying cron runs ---\n")
import subprocess
time.sleep(30)  # Wait for runs to complete

# Check scanner health
try:
    with open("Z:/Developer_Brain/Shared_With_Pink/scanner_health.json") as f:
        health = json.load(f)
    print(f"Scanner health last_run: {health.get('last_run')}")
    print(f"Scanner alive: {health.get('alive')}")
except Exception as e:
    print(f"  Scanner health file error: {e}")

# Check OODA log
import glob
logs = sorted(glob.glob("Z:/Developer_Brain/Shared_With_Pink/ooda_log_*.json"), reverse=True)
if logs:
    with open(logs[0]) as f:
        log = json.load(f)
    print(f"OODA log timestamp: {log.get('timestamp')}")
    print(f"OODA overall: {log.get('overall')}")
    print(f"OODA systems: {log.get('systems', {}).get('kill_trading OFF', 'N/A')}/9")
