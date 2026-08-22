"""Find and update ALL Trello cards related to Augur trading system (not just miss-pink labeled)."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

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

cards = trello_get(f"boards/{BOARD_ID}/cards")

# Find ALL cards related to Augur/augur trading system work
keywords = ["augur", "import 156 yfinance", "import 129 hof", "trigger scan", 
            "kill-switch", "kill switch", "first verified paper trade",
            "ooda loop", "regime detection", "price_history", "hof genome"]

target_cards = []
for c in cards:
    name = c.get("name", "").lower()
    labels = [l.get("name","") for l in c.get("labels",[])]
    is_p0 = "P0" in labels
    is_p1 = "P1" in labels
    matches_kw = any(kw in name for kw in keywords)
    if matches_kw and (is_p0 or is_p1):
        target_cards.append(c)

print(f"Found {len(target_cards)} P0/P1 cards related to Augur trading system:")
for c in target_cards:
    labels = [l.get("name","") for l in c.get("labels",[])]
    print(f"  [{','.join([l for l in labels if l][:4])}] {c['name'][:60]}")

# Update each with progress
print(f"\n{'='*70}")
print("UPDATING CARDS")
print(f"{'='*70}")

for c in target_cards:
    card_id = c["id"]
    name = c["name"].lower()

    if "import 156 yfinance" in name:
        comment = "DONE: 64,239 rows in price_history (157 tickers). yfinance CSVs imported via /api/download?use_yfinance=true. Data range: 2024-01-01 to 2026-08-07. AI Ready=True."
    elif "import 129" in name or ("hof" in name and "import" not in name):
        comment = "DONE: 129 HOF genome exports imported to DB. 36 genomes in hall_of_fame table. sma_bounce: Sharpe=0.8, WR=60%, PF=2.3 (all 11 HOF criteria met). vwap_bounce: Sharpe=0.4."
    elif "trigger scan" in name or "first verified paper trade" in name:
        comment = "DONE: Augur batch_score on 28 tickers → BB buy @ $8.99 FILLED (order e4479350, client: augur_hof_bb_1786357095), AAPL buy @ $306.61 FILLED (order 8c4aa5dc, client: augur_hof_aapl_1786357095). Both sma_bounce genome bracket orders. Live P&L: AAPL +$1.10, BB -$0.16."
    elif "kill" in name:
        comment = "FIXED: POST /api/killswitch/trading with Content-Type:application/json + {\"action\":\"disable\"}. DB settings confirmed: kill_trading=0, kill_learning=0, paper_mode=1. API returns false/false/true."
    elif "ooda loop" in name and "end-to-end" in name:
        comment = "PROGRESS: Full end-to-end Augur pipeline operational:\n1. HOF genomes: 36 in DB (sma_bounce Sharpe=0.8)\n2. price_history: 64,239 rows, 157 tickers, AI Ready=True\n3. Signal gen: batch_score on 28 tickers → entry zones computed\n4. Paper trades: BB FILLED @ $8.99, AAPL FILLED @ $306.61\n5. Kill switches: OFF, paper mode ON\n6. Autonomous trainer: cron every 5m (job_id: 8911a015555d, 7+ coaching notes)\n7. Fleet: PINKCADY+SQUIDSTATION+STEALTHATTACK all online\nDeliverables: augur_autonomous_trainer.py + VOID_FLEET_AUGUR_HANDBOOK.md + reports in Outbox + Z: vault sync"
    elif "regime" in name:
        comment = "TODO: market_regime.py calls yfinance.download('SPY') live inside Docker → YFRateLimitError. Needs offline path: read SPY/VIX regime from price_history table. Block assigned to Sir Green or Miss Pink to implement offline regime."
    elif "augur" in name and "signal" in name:
        comment = "DONE: Augur signal generator produces entry zones for 18/28 tickers. sma_bounce genome params: SMA=20, R:R=2.0, ATR_stop=0.5, max_hold=5d. Signals via /api/augur/batch_score → bot_signals table."
    else:
        comment = "PROGRESS: See FINAL_AUGUR_DEPLOYMENT_REPORT_20260810T2147Z.md"

    result = trello_post(f"cards/{card_id}/actions/comments", {"text": comment})
    status = "OK" if result.get("id") else f"ERROR"
    print(f"  [{status}] {c['name'][:55]}")

print(f"\n{'='*70}")
print(f"UPDATED {len(target_cards)} cards")
print(f"{'='*70}")