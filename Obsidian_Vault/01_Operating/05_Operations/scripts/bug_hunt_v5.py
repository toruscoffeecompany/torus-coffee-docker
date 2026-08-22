"""
File final 2 bugs + write comprehensive report.
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
        post_comment(cid, f"🔄 **MISS PINK BUG HUNT v5 ({ts})** — @SirGreen — {name}")
        print(f"  ✅ {name[:60]}")
    except Exception as e:
        print(f"  ❌ — {e}")
    time.sleep(0.4)

print("=== Filing final bugs ===\n")

# Bug: /api/whale returns HTML (same as all other missing endpoints but it's a SECURITY endpoint)
file_bug(
    "🐛 [BUG] /api/whale returns HTML — White Whale classified tools exposed/broken",
    f"""**Issue:** /api/whale returns HTML (not JSON) — the White Whale classified tools endpoint is broken.

**Evidence:**
- curl /api/whale → HTML (index.html SPA)
- curl /api/whale?passphrase=test → HTML (no auth validation visible)
- Dashboard nav has WHITE WHALE link — clicking it shows blank/broken page

**Impact:** White Whale classified tools (vault lockdown, secrets management,
security scanning) are inaccessible via API. Security features broken.

**Fix:**
1. Add POST/GET handler for /api/whale in app.py
2. Implement passphrase validation (backend, not just frontend)
"3. Return JSON with status, tools array, and authentication result"
4. Test with passphrase param

— 🦜""", "P0"
)

# Bug: schwab_api=0 but /api/portfolio returns real Schwab data (inconsistency)
file_bug(
    "🐛 [BUG] schwab_api=0 in phase1_progress BUT /api/portfolio returns real Schwab data — Data inconsistency",
    f"""**Issue:** TM API /api/status reports schwab_api: 0% (phase1_progress) but /api/portfolio
returns 31 REAL positions pulled from Schwab.

**Evidence:**
- /api/status → phase1_progress.schwab_api: 0, phase1_progress.dashboard: 65
- /api/portfolio → {{count: 31, file: "Main Div. Account-Positions-2026-06-04-153554.csv", positions: [...]}}
- Real tickers: AGNC, ARCC, ARR, BEP, BSM, BTG, CPB, DOC, DX, EPD, EPR, GIS, GOLD, GOOD, GWRS, HL, HRZN, KHC, KMB, LAND, LNT, MAIN, MDT, ORC, OXSQ, PFE, PFLT, PSEC, STAG, VZ, ECC

**Impact:** Dashboard progress tracking is WRONG. Schwab integration is actually
working (85%+), but phase1_progress reports 0%. Misleading for Captain.

**Root cause:** phase1_progress is hardcoded/static. The "schwab_api" progress bar
doesn't reflect the actual /api/portfolio endpoint working.

**Fix:**
1. Make phase1_progress dynamic — read actual API endpoint status
2. /api/portfolio working → schwab_api should be 85% not 0%
3. Add progress calculation based on real endpoint availability

— 🦜""", "P1"
)

print(f"\n{'='*70}")
print("BUG HUNT v5 COMPLETE — 2 final bugs")
print("="*70)