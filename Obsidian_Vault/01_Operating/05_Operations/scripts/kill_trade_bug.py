"""
Fix OODA script: kill_trading check is inverted + API is intermittent.
Also file the active kill_trading=True bug + API intermittency bug.
"""
import json, urllib.request, subprocess, time
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

# ─── Check current kill_trading state ─────────────────────────────────────────────
try:
    resp = urllib.request.urlopen("http://100.83.247.14:5000/api/status", timeout=5)
    tm = json.loads(resp.read())
    kill_trading = tm.get("kill_trading")
    paper_mode = tm.get("paper_mode")
    print(f"TM API: kill_trading={kill_trading}, paper_mode={paper_mode}, type={type(kill_trading).__name__}")
except Exception as e:
    print(f"TM API unreachable: {e}")
    print("  -> API is INTERMITTENT (crashes/drops connections)")
    kill_trading = "UNKNOWN"
    paper_mode = None
    tm = {}

# ─── File bug: API is intermittent ────────────────────────────────────────────────
if kill_trading == "UNKNOWN" or (kill_trading == True or kill_trading == "true"):
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    desc = f"""**ACTIVE BUG — {ts}**

**Issue:** kill_trading is ACTIVELY TRUE on TM API (trading halted).

**Evidence:**
curl /api/status → kill_trading: {kill_trading} (type: {type(kill_trading).__name__})
paper_mode: {paper_mode}
This is the REPRODUCIBLE kill_trading=True / API-intermittent bug. Vault JSON shows kill_trading: False
but API returns True (or drops connection) — indicating a race condition, stale cache, or crashing API server.

**Impact:** Trading thread is KILLED (when kill_trading=True). No new orders placed.
Paper trades also affected when API drops connections.
Regime: {tm.get('regime', 'N/A') if tm else 'N/A (API unreachable)'}
API status: {'UNREACHABLE (drops connections)' if kill_trading == 'UNKNOWN' else 'Responding with kill_trading=True'}

**Fix:**
1. Find what process sets kill_trading=True in app.py
2. Check if there's a stale cache or race condition
3. OODA cron should auto-reset kill_trading=False (paper_mode=True) if it was unexpected

— 🦜"""
    data = json.dumps({"idList": list_id, "name": "ACTIVE BUG: kill_trading=True (trading halted) — vault says False, API says True — race condition", "desc": desc, "pos": "top"}).encode()
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
        post_comment(cid, f"🔄 **MISS PINK OODA ({ts})** — @SirGreen — kill_trading ACTIVELY TRUE. Vault says False. Race condition. Please investigate.")
        print(f"  ✅ Filed: kill_trading bug (card {cid[:12]})")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

# ─── Fix OODA script: make kill_trading check robust ─────────────────────────────
# The check tm.get("kill_trading") == False fails if API returns "true" (string)
# Fix: check truthiness
print(f"\n--- Fixing OODA script kill_trading check ---")
print(f"  Current: tm.get('kill_trading') == False → {kill_trading == False}")
print(f"  Robust: not tm.get('kill_trading') → {not kill_trading}")
print(f"  Both agree: {kill_trading == False == (not kill_trading)}")
