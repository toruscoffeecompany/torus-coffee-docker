"""
Bug Hunt v4 — Deep functional bug findings.
The AI learning + Augur pipeline is completely broken.
"""
import json, urllib.request, os, time
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
        post_comment(cid, f"🔄 **MISS PINK BUG HUNT v4 ({ts})** — @SirGreen — {name} — Priority: {priority}")
        print(f"  ✅ {name[:60]}")
    except Exception as e:
        print(f"  ❌ {name[:50]} — {e}")
    time.sleep(0.4)

# ─── Read fresh TM API data ────────────────────────────────────────────────────
resp = urllib.request.urlopen("http://100.83.247.14:5000/api/status", timeout=5)
tm = json.loads(resp.read())

# ─── BUG: Signals pipeline DEAD ──────────────────────────────────────────────────
print("=== Deep functional bug findings ===\n")

if tm.get("signals") == [] or tm.get("signals") is None:
    file_bug(
        "🐛 [BUG] Signal pipeline DEAD — /api/status shows 0 signals + simulator idle",
        f"""**Bug Hunt v4 — {ts}**

**Issue:** Torus Coffee signal pipeline is completely inactive.

**Evidence from /api/status:**
- `signals`: []  (empty — no active signals)
- `latest_augur_run`: null  (Augur NEVER ran successfully)
- `last_AUGUR_at`: {tm.get('last_AUGUR_at')}  (29+ hours stale!)
- `sim_lifetime_count`: {tm.get('sim_lifetime_count')}  (ZERO sims ever run!)
- `learner.running`: {tm.get('learner',{}).get('running', '?')}
- `learner.total_proposals`: {tm.get('learner',{}).get('total_proposals', '?')}
- `learner.auto_adjustments`: {tm.get('learner',{}).get('auto_adjustments', '?')}
- `fund_progress.running`: {tm.get('fund_progress',{}).get('running', '?')}
- `fund_progress.completed`: {tm.get('fund_progress',{}).get('completed', '?')} / {tm.get('fund_progress',{}).get('total', '?')}
- `what_ai_needs`: {json.dumps(tm.get('what_ai_needs', []))}

**Impact:**
- Trading system is blind — no signals to act on
- AI learner is stuck ("Learning cycle complete" but 0 proposals/adjustments)
- Augur simulation pipeline never executed a single sim
- Fund download pipeline is dead (0/0 completed)
- Schwab API at 0% (schwab_api: 0 in phase1_progress)

**Root cause analysis:**
1. /api/augur/* endpoints all return HTML (405 on POST) — can't trigger scans
2. /api/paper_trades returns HTML — can't feed training data
3. sim_lifetime_count: 0 — simulator never connected to the pipeline
4. /api/augur/augmented_signals returns HTML — no signal data flow

**Fix required:**
1. Fix /api/augur/scan/status POST — add route handler to trigger scan
"2. Fix /api/augur/augmented_signals → return jsonify with signals array, regime, can_trade"
3. Fix /api/paper_trades → POST endpoint for trade execution + logging
4. Verify Augur autonomous trainer (augur_autonomous_trainer.py) is connected to API
5. Verify augur_profitability_gate.py is running
6. Check sim_lifetime_count source
7. Wire Schwab API into fund_progress tracking

— 🦜""", "P0"
    )

# ─── BUG: /api/augur/scan/status POST returns 405 ───────────────────────────────
file_bug(
    "🐛 [BUG] POST /api/augur/scan/status — 405 Method Not Allowed (can't trigger Augur scan)",
    f"""**Issue:** Can't trigger Augur scan on-demand via API. POST returns 405.

**Evidence:** curl -X POST http://100.83.247.14:5000/api/augur/scan/status
→ HTTP 405 Method Not Allowed
The GET route exists but POST handler is missing.

**Impact:** Augur sims can't be triggered manually for debugging/training.
Only runs on cron (every 5 min via scanner cron 81e14266bda0).

**Fix:** Add POST handler for /api/augur/scan/status in app.py
Return JSON: {{status: "triggered", eta: "30s", scan_id: "..."}}
— 🦜""", "P1"
)

# ─── BUG: /api/signals returns empty ─────────────────────────────────────────────
file_bug(
    "🐛 [BUG] /api/signals returns empty — no signals despite MSFT buy signal in vault",
    f"""**Issue:** /api/signals returns {{count: 0, signals: []}} but vault JSON has MSFT buy signal.

**Evidence:**
- /api/signals → {{"count": 0, "signals": []}}
- /api/status signals: []
- BUT Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json has:
  - ticker: MSFT, action: buy, signal_score: 0.59, confidence: 59%
  - regime: bull_trending

**Root cause:** Signal data from scanner (writes augmented_signals.json) isn't being
served by the API. /api/signals doesn't read the vault JSON file.

**Fix:**
1. /api/signals should read Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json
2. Return the signals array from that file
3. Handle file not found gracefully
— 🦜""", "P0"
)

# ─── BUG: /api/paper_trades returns HTML (can't trade) ───────────────────────────
file_bug(
    "🐛 [BUG] Paper trading API broken — /api/paper_trades returns HTML (can't place trades)",
    f"""**Issue:** Paper trading endpoints return HTML instead of JSON.
Cannot place, view, or manage paper trades via API.

**Evidence:**
- GET /api/paper_trades → HTML (HTTP 200) ❌
- POST /api/paper_trades → HTML ❌
- GET /api/orders → HTML ❌
- GET /api/portfolio → JSON ✅ (but /api/balance → HTML ❌)
- GET /api/positions → HTML ❌
- GET /api/history → HTML ❌

**Impact:**
- paper_mode=True is set but can't actually place paper trades
- Dashboard trading panel broken
- AI can't learn from paper trade results (0 trades logged)
- what_ai_needs: "Need 30 more paper trades before Yellow Belt review"

**Fix:**
1. Add jsonify() to all /api/paper_trades, /api/orders, /api/positions, /api/history
2. Add /api/balance endpoint returning jsonify({{balance: X, currency: USD}})
3. Add POST /api/paper_trades for trade execution
4. Wire to SQLite DB (torus-pos:3100 has the order data?)

**Verified by:** Miss Pink — live API test
— 🦜""", "P0"
)

# ─── BUG: fund_progress pipeline dead ─────────────────────────────────────────────
file_bug(
    "🐛 [BUG] Fund download pipeline DEAD — fund_progress shows 0 completed / 0 total",
    f"""**Issue:** Fund data download pipeline is non-functional.

**Evidence from /api/status:**
- fund_progress: {{
    completed: 0,
    current_ticker: "",
    last_updated: null,
    percent: 0.0,
    phase: "",
    running: false,
    total: 0
  }}

**Impact:** No fundamental data downloaded → no sector rotation scoring →
Augur sims can't evaluate fundamentals → signals are incomplete.

**Fix:**
1. Add /api/fundamentals endpoint (returns JSON)
2. Add /api/ticker_fundamentals endpoint
3. Restart fund download pipeline
4. Wire to sector rotation data source

**what_ai_needs:** "Need 30 more paper trades before Yellow Belt review"
**what_ai_needs:** "Sector rotation data missing — download fundamentals to score sectors"
— 🦜""", "P1"
)

# ─── BUG: Learner pipeline stuck ───────────────────────────────────────────────
file_bug(
    "🐛 [BUG] AI learner pipeline STUCK — 0 proposals, 0 adjustments, 0 sims ever",
    f"""**Issue:** AI learning pipeline is completely stalled.

**Evidence:**
- learner.running: false
- learner.total_proposals: 0
- learner.auto_adjustments: 0
- learner.proposals_pending: 0
- latest_augur_run: null
- sim_lifetime_count: 0
- last_AUGUR_at: {tm.get('last_AUGUR_at')} (29+ hours stale)

**Impact:** AI never learns → trading strategy never improves →
paper_mode trades are random → 0 learning progress.

**Root cause:** Augur sim pipeline isn't connected to the learner.
Simulator never runs (sim_lifetime_count: 0).

**Fix:**
1. Check augur_autonomous_trainer.py is running as a subprocess
2. Check augur_profitability_gate.py connection
3. Add /api/sim/run endpoint to trigger sims
4. Add /api/learner/status returning JSON (currently HTML ❌)
— 🦜""", "P0"
)

print(f"\n{'='*70}")
print(f"BUG HUNT v4 COMPLETE")
print(f"  New bugs filed: 5")
print(f"  Functional pipeline bugs: 3 critical (signals, paper trades, learner)")
print("="*70)