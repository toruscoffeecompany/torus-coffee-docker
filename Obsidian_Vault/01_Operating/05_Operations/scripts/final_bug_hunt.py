"""
Final bug filing: augur_signals empty + /api/crew_heartbeat missing.
+ Write the final completion report.
"""
import json, urllib.request, time, os
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

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def file_bug(name, desc, priority="P0"):
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                    data=json.dumps({"value": lid}).encode(), method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        post_comment(cid, f"🔄 **MISS PINK BUG HUNT FINAL ({ts})** — @SirGreen")
        print(f"  FILED: {name[:60]}")
    except Exception as e:
        print(f"  FAIL: {e}")
    time.sleep(0.3)

# ─── Bug: /api/augur/augmented_signals returns empty signals ─────────────────────
file_bug(
    "[BUG] /api/augur/augmented_signals returns empty signals (count:0) — Augur Trading tab broken",
    f"""**Bug Hunt Final — {ts}**

**Issue:** /api/augur/augmented_signals returns **0 signals** despite MSFT buy signal 
existing in vault data. The Augur Trading dashboard tab has no data to display.

**Evidence:**
curl /api/augur/augmented_signals → {{"count":0, "note":"Augmented signals placeholder", "signals":[]}}

But vault vault.json has regime=bull_trending with MSFT buy signal score 0.59.

**Impact:** No trading signals generated → no paper trades → Augur sims=0 → entire pipeline dead.
Augur Trading tab shows empty placeholder text.

**Root cause:** Signal generation pipeline is disconnected from API serving layer.
The scanner writes to augmented_signals.json but /api/augur/augmented_signals reads from DB.

**Fix:**
1. Connect /api/augur/augmented_signals to read from augmented_signals.json
2. OR have scanner write to DB signals table
3. Parse vault.json signals into the API response

— 🦜""", "P0")

# ─── Bug: /api/crew_heartbeat returns HTML ─────────────────────────────────────
file_bug(
    "[BUG] /api/crew_heartbeat returns HTML 404 — crew agent monitoring broken",
    f"""**Bug Hunt Final — {ts}**

**Issue:** /api/crew_heartbeat endpoint — which dashboard_server.py documents as the 
crew agent heartbeat monitor — returns HTML (404 catch-all) instead of JSON.

**Evidence:**
curl /api/crew_heartbeat → HTML (index.html served via catch-all)
dashboard_server.py docstring says: "Crew agent heartbeat: /api/crew_heartbeat 
(for cross-ship agent monitoring)"

**Impact:** Crews cannot report heartbeats to the dashboard. Fleet monitoring 
cross-ship agent status is broken.

**Fix:** Add /api/crew_heartbeat route to dashboard_server.py.
Return JSON with crew status (agent_id, ship, last_seen, status).

— 🦜""", "P1")

# ─── Bug: /api/sandbox returns HTML 404 ──────────────────────────────────────────
file_bug(
    "[BUG] /api/sandbox returns HTML — Sandbox API endpoint missing (dashboard has tab)",
    f"""**Bug Hunt Final — {ts}**

**Issue:** Dashboard "🧪 Sandbox" tab exists but /api/sandbox endpoint 
returns HTML catch-all (route not registered).

**Evidence:** curl /api/sandbox → HTML (index.html)

**Fix:** Add /api/sandbox route returning JSON sandbox operations.

— 🦜""", "P2")

print(f"\n{'='*70}")
print("FINAL BUG HUNT COMPLETE")
print("="*70)
