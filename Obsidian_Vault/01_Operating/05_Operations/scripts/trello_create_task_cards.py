"""Create Trello cards for task tracking + assign Sir Green / Miss Pink."""
import json, urllib.request, os

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

# Try GitHub issues too
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def trello_post(path, body):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# Get lists and labels
lists = trello_get(f"boards/{BOARD_ID}/lists")
list_map = {l["name"]: l["id"] for l in lists}
labels = trello_get(f"boards/{BOARD_ID}/labels")
label_map = {l["name"]: l["id"] for l in labels}

# Find the right list
todo_list_id = list_map.get("P1 - High / Doing Now") or list_map.get("To Do") or lists[0]["id"]
p1_id = label_map.get("P1")
p0_id = label_map.get("P0")
p2_id = label_map.get("P2")
sir_green_label = label_map.get("sir-green")
miss_pink_label = label_map.get("miss-pink")
done_label = label_map.get("Done")

print(f"Using list: {list_map.get(todo_list_id, '?')}")
print(f"Labels: P1={p1_id}, P0={p0_id}")

# ─── SIR GREEN'S CARDS: Deploy signal augmentation ─────────────────────────══
print("\n=== CREATING SIR GREEN CARDS ===")

sir_green_cards = [
    {
        "name": "[DEPLOY] Sir Green: Deploy signal_augmentation.py to SQUIDSTATION Docker",
        "desc": (
            "Miss Pink has built signal_augmentation.py with fundamentals/sector/macro "
            "scoring. Deploy to SQUIDSTATION Docker container.\n\n"
            "**Steps:**\n"
            "1. Copy signal_augmentation.py to backend/augur/ in Docker container\n"
            "2. Create DB tables: ticker_fundamentals, macro_econ (SQL in deploy script)\n"
            "3. Import augmentation functions into engine.py's evaluate_entry_indicators()\n"
            "4. Replace pure technical scoring with combined 4-layer scoring\n"
            "5. Test: AAPL should get combined_score=0.39 → ENTRY (fundamentals +0.5)\n\n"
            "**Files:** tr3asure_mAp/signal_augmentation.py, tr3asure_mAp/deploy_signal_augmentation.sh\n"
            "**Verified by:** Miss Pink (test_signal_augmentation.py)"
        ),
        "labels": [p1_id, sir_green_label],
    },
    {
        "name": "[DEPLOY] Sir Green: Populate ticker_fundamentals for all 157 tickers",
        "desc": (
            "Fundamentals table has 10/157 tickers. Batch-populate the remaining 147.\n\n"
            "**Steps:**\n"
            "1. Get all tickers from price_history table (157 tickers)\n"
            "2. Fetch yfinance.Ticker(ticker).info for each (pe_ratio, roe, debt_to_equity, etc.)\n"
            "3. Map ticker → GICS sector (yfinance sector field)\n"
            "4. Insert into ticker_fundamentals table\n"
            "5. Verify all 157 tickers have fundamental data\n\n"
            "**Script:** scripts/populate_fundamental_macros.py (template for batch)\n"
            "**Current:** 10/157 tickers populated\n"
            "**Target:** 157/157 tickers"
        ),
        "labels": [p1_id, sir_green_label],
    },
    {
        "name": "[DEPLOY] Sir Green: Wire augmented scoring into augur_signal_generator.py",
        "desc": (
            "Integrate signal_augmentation.py into the live signal generator.\n\n"
            "**Steps:**\n"
            "1. Import score_fundamental, score_sector, score_macro from signal_augmentation\n"
            "2. In evaluate_entry_indicators(): add fundamental/sector/macro as additional conditions\n"
            "3. Modify combined score = 0.4*tech + 0.3*fund + 0.2*sector + 0.1*macro\n"
            "4. Update signal output format to include fundamental_detail, sector_detail, macro_detail\n"
            "5. API endpoint /api/augur/last_signal should return augmented scores\n"
            "6. Dashboard AugurMindPanel shows the 4-layer breakdown\n\n"
            "**File:** backend/augur/augur_signal_generator.py (inside Docker)\n"
            "**Reference:** AugurMindPanel.jsx already expects these fields!"
        ),
        "labels": [p0_id, sir_green_label],
    },
]

sg_card_ids = []
for c in sir_green_cards:
    result = trello_post("cards", {
        "name": c["name"],
        "desc": c["desc"],
        "idList": todo_list_id,
        "idLabels": [l for l in c["labels"] if l],
    })
    if result.get("id"):
        sg_card_ids.append(result["id"])
        print(f"  ✅ Created: {c['name'][:60]}")
        print(f"     URL: {result.get('shortUrl', '?')}")
    else:
        print(f"  ⚠️  {result}")

# ─── MISS PINK'S CARDS: My OODA tasklist ──────────────────────────────────────
print(f"\n=== CREATING MY CARDS (miss-pink) ===")

miss_pink_cards = [
    {
        "name": "[OODA] Miss Pink: Create 100-trade profitability gate runner",
        "desc": (
            "Deploy augur_profitability_gate.py as an automated evaluator.\n\n"
            "**Steps:**\n"
            "1. Add profitability gate as a step in augur_autonomous_trainer.py Phase 6\n"
            "2. Read from Alpaca paper orders + local trades table\n"
            "3. Evaluate all 6 gate criteria (WR, PF, Sharpe, drawdown, max losses, profit)\n"
            "4. Write result to Outbox/AUGUR_PROFITABILITY_GATE_RESULT.md\n"
            "5. Post gate result as comment on Trello card 'Augur: 100-paper-trade profitability gate'\n"
            "6. If gate PASSES: send Captain approval request\n\n"
            "**Current:** 2/100 trades (AAPL winner, BB loser), PF=6.93, need 98 more\n"
            "**File:** tr3asure_mAp/augur_profitability_gate.py (done)"
        ),
        "labels": [p1_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Verify Augur dashboard tab auto-refresh + alerts",
        "desc": (
            "Captain's Dashboard Augur tab at /tab/augur-trading needs live data verification.\n\n"
            "**Steps:**\n"
            "1. Fetch dashboard HTML from SQUIDSTATION:8080\n"
            "2. Verify AugurTab.jsx polls /api/augur/last_signal every 5s\n"
            "3. Verify AugurMindPanel.jsx renders indicator snapshot + genome conditions\n"
            "4. Verify error reporting sends to /api/client_error → SOS tab\n"
            "5. Check if /api/augur/last_signal returns data or no_data\n"
            "6. Report missing endpoints if any\n\n"
            "**File:** //192.168.0.39/.../frontend/src/tabs/AugurTab.jsx (8,369 lines)\n"
            "**File:** //192.168.0.39/.../frontend/src/components/AugurMindPanel.jsx"
        ),
        "labels": [p1_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Import 156 yfinance CSVs — verify completion",
        "desc": (
            "Previously marked complete. Re-verify all CSVs imported into price_history.\n\n"
            "**Steps:**\n"
            "1. Count yfinance CSV files in data/yfinance/\n"
            "2. Count distinct tickers in price_history table\n"
            "3. Verify row count (target: >60K rows)\n"
            "4. Check AI Ready flag in TreasureMap status API\n\n"
            "**Expected:** 156 CSVs → 157 tickers → 64,239 rows → AI Ready=True"
        ),
        "labels": [p2_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Sync 129 HOF genome exports — verify completion",
        "desc": (
            "Previously imported 129 HOF genome JSON exports. Re-verify DB state.\n\n"
            "**Steps:**\n"
            "1. Count JSON files in hall_of_fame_exports/\n"
            "2. Count rows in hall_of_fame table\n"
            "3. Count rows in strategy_results table\n"
            "4. Verify best genome: sma_bounce (Sharpe=0.8, WR=60%, PF=2.3)\n"
            "5. Check AI Ready flag\n\n"
            "**Expected:** 129 JSON → 194 hall_of_fame + 194 strategy_results → AI Ready=True\n"
            "(More rows than JSONs because batch sims also write to DB)"
        ),
        "labels": [p2_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Fix kill-switch state mismatch — re-verify",
        "desc": (
            "Previously fixed kill-switch state mismatch. Re-verify.\n\n"
            "**Steps:**\n"
            "1. Call TreasureMap /api/status\n"
            "2. Verify kill_trading=False, kill_learning=False, paper_mode=True\n"
            "3. Call /api/toggle endpoint to confirm toggle works\n"
            "4. Verify state persists across cron runs\n\n"
            "**Expected:** kill_trading=False, paper_mode=True"
        ),
        "labels": [p0_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Fix regime detection — verify offline fallback works",
        "desc": (
            "Patched market_regime.py for offline-first SPY/VIX access.\n\n"
            "**Steps:**\n"
            "1. Verify market_regime_fixed.py is deployed to SQUIDSTATION\n"
            "2. Check if the fix was applied (file is inside Docker — can't write via SMB)\n"
            "3. Test offline fallback: SPY.csv + VIX_X.csv in yfinance/ dir\n"
            "4. Document workaround if Docker write is blocked\n\n"
            "**Fix:** VIX file is VIX_X.csv (not ^VIX.csv) — patched in market_regime_fixed.py\n"
            "**Issue:** Docker container writes not possible via SMB share (read-only mount)"
        ),
        "labels": [p0_id, miss_pink_label],
    },
    {
        "name": "[OODA] Miss Pink: Trigger scan → verify first paper trade",
        "desc": (
            "Previously executed BB + AAPL paper trades. Re-verify they're still live.\n\n"
            "**Steps:**\n"
            "1. Call Alpaca /positions API\n"
            "2. Verify BB and AAPL positions still active\n"
            "3. Check order history (/orders) for FILL status\n"
            "4. Verify P&L: AAPL should be green (~+$1), BB should be slightly red (~-$0.15)\n\n"
            "**Current:** AAPL 1@$306.61 P/L: +$0.84, BB 1@$8.99 P/L: -$0.16"
        ),
        "labels": [p1_id, miss_pink_label],
    },
]

mp_card_ids = []
for c in miss_pink_cards:
    # Fix: use correct label variable
    labels_to_use = c["labels"]
    result = trello_post("cards", {
        "name": c["name"],
        "desc": c["desc"],
        "idList": todo_list_id,
        "idLabels": [l for l in labels_to_use if l],
    })
    if result.get("id"):
        mp_card_ids.append(result["id"])
        print(f"  ✅ Created: {c['name'][:60]}")
        print(f"     URL: {result.get('shortUrl', '?')}")
    else:
        print(f"  ⚠️  {result}")

print(f"\n=== SUMMARY ===")
print(f"Sir Green cards: {len(sg_card_ids)}")
print(f"Miss Pink cards: {len(mp_card_ids)}")
print(f"\nTotal new cards created: {len(sg_card_ids) + len(mp_card_ids)}")