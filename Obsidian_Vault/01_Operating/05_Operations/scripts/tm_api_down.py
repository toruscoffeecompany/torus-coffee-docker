"""File TM API server crash bug."""
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

# Check if /api/status is currently down
import subprocess
r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "5", "http://100.83.247.14:5000/api/status"], capture_output=True, text=True, timeout=10)
code1 = r.stdout

# Check dashboard is up
r2 = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "5", "http://100.83.247.14:8080/"], capture_output=True, text=True, timeout=10)
code2 = r2.stdout

print(f"TM API (5000): HTTP {code1}")
print(f"Dashboard (8080): HTTP {code2}")

if code1 == "000" and code2 == "200":
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    desc = f"""**Bug Hunt v6 — {ts}**

**Issue:** TM API server (port 5000) is DOWN/CRASHED.

**Evidence:**
- curl http://100.83.247.14:5000/api/status → HTTP 000 (connection refused/timeout)
- curl http://100.83.247.14:8080/ → HTTP 200 (dashboard frontend still serving)

The Flask/Express API backend has crashed/stopped while the dashboard server (port 8080) continues running.

This is a REGRESSION — API was responding at 06:24Z, now down at {ts}.

**Impact:**
- ALL API endpoints broken (/api/status, /api/signals, /api/paper_trades, etc.)
- Dashboard panels all show "..." (cannot reach API)
- Signal scanner cannot write (no DB connection via API)
- Paper trading completely broken
- OODA verification cannot check kill_trading/paper_mode

**Root cause investigation needed:**
- Check TM API process status on SQUIDSTATION
- Check if API server OOM-killed or crashed
- Check /api/health endpoint
- Add auto-restart on crash

**Fix:**
1. Restart TM API server (gunicorn/uvicorn/Flask) on SQUIDSTATION
2. Add health check + auto-restart
3. Add crash monitoring to OODA cron

— 🦜"""
    data = json.dumps({"idList": list_id, "name": "TM API SERVER CRASHED — port 5000 down (HTTP 000), dashboard 8080 still serving HTML", "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", "P0", "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                    data=json.dumps({"value": lid}).encode(), method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        print(f"  Filed: TM API crash bug (card {cid[:12]})")
    except Exception as e:
        print(f"  Failed: {e}")
