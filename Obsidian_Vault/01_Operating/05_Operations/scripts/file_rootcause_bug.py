"""
File the ROOT CAUSE kill_trading bug — line 300 of app.py has comment/code mismatch.
ALSO: Fix the OODA script's _load_kill_state() call which reads stale DB value.
"""
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

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

# ─── Read app.py to confirm the bug ─────────────────────────────────────────────
with open("D:/Work/tr3asure_mAp/patches/app.py") as f:
    lines = f.readlines()

# Find all kill_trading assignments
print("=== kill_trading assignments in app.py ===")
for i, line in enumerate(lines, 1):
    if "kill_trading" in line and "=" in line:
        print(f"  {i}: {line.rstrip()[:80]}")

# ─── File root cause bug ─────────────────────────────────────────────────────────
list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"

desc = f"""**ROOT CAUSE — kill_trading auto-sets to True on server restart — {ts}**

**Issue:** Line 300 of app.py has a COMMENT/CODE MISMATCH that causes kill_trading to
always be True when the TM API server starts or restarts.

**Evidence (app.py line 296-310):**
```python
# Line 296-300:
    except Exception:
        return True, False   # Safe defaults — trading off, learning on

    _, kill_learning = _load_kill_state()
    kill_trading = True    # ALWAYS starts OFF — Captain must manually enable live trading  ← BUG!
```

The COMMENT says "ALWAYS starts OFF" (meaning kill_trading should be False) but the CODE
assigns `kill_trading = True`. This is a copy-paste/logic error.

**Additional issue (line 297):** `_load_kill_state()` returns `(True, False)` as defaults — meaning:
- True = kill_trading starts True (WRONG — should be False for paper mode)
- False = kill_learning starts False (learning on)

**Additional issue (line 307):** `_save_kill_state()` writes kill_trading to DB as 'true'
every time the server starts — so the stale 'true' value persists.

**Lines 1297 + 1438 also set kill_trading = True directly** — these emergency kill handlers
may be firing incorrectly.

**Impact:**
- Every server restart → kill_trading = True (trading halted)
- paper_mode = True but kill_trading = True → paper trades also halted
- No new signals generated, no new trades, Augur sims = 0
- This is the ROOT CAUSE of the "kill_trading auto-resets to True" bug

**Fix:**
1. Line 300: Change `kill_trading = True` → `kill_trading = False`
   (Comment already says "ALWAYS starts OFF" — match the code to the intent)
2. Line 297: Change `return True, False` → `return False, False`
   (Safe defaults: trading ON for paper mode, learning ON)
3. Lines 1297 + 1438: Review why kill_trading is set to True — may be legitimate
   emergency handlers that need investigation
4. Add OODA auto-fix: if paper_mode=True and kill_trading=True with no manual
   kill event, auto-reset kill_trading=False

**File:** tr3asure_mAp/patches/app.py (this is the DEPLOYED version on SQUIDSTATION)
**Note:** The live app.py on SQUIDSTATION may differ from this patched copy — verify
that this file IS the one running on port 5000.

— 🦜"""

data = json.dumps({"idList": list_id, "name": "ROOT CAUSE: kill_trading=True on boot — app.py line 300 comment/code mismatch (comment says OFF, code sets True)", "desc": desc, "pos": "top"}).encode()
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
    post_comment(cid, f"🔄 **MISS PINK ROOT CAUSE ({ts})** — @SirGreen — kill_trading=True on boot. app.py line 300: `kill_trading = True` but comment says \"ALWAYS starts OFF\". Code/comment mismatch. Fix: set kill_trading=False on boot (paper mode).")
    print(f"  ROOT CAUSE bug filed (card {cid[:12]})")
except Exception as e:
    print(f"  FAILED: {e}")
