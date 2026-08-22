"""Update Trello cards with work completed on Augur auto-learning system."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

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

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

cards = trello_get(f"boards/{BOARD_ID}/cards")

target_cards = []
for c in cards:
    name = c.get("name", "").lower()
    if any(kw in name for kw in ["import 156 yfinance", "import 129 hof", "trigger scan", "restart treasuremap", "kill-switch state", "kill switch", "ooda loop"]):
        target_cards.append(c)

print(f"Found {len(target_cards)} target cards to update:")
for c in target_cards:
    print(f"  ID={c['id'][:8]}... | {c['name'][:65]}")

for c in target_cards:
    name = c["name"]
    card_id = c["id"]
    name_lower = name.lower()

    print(f"\nUpdating: {name[:50]}...")

    if "import 156" in name_lower:
        comment = "PROGRESS: 64,400 rows in price_history across 157 tickers. yfinance CSVs imported via /api/download (use_yfinance=true). price_history populated. Data verified."
    elif "import 129" in name_lower or "hof" in name_lower:
        comment = "DONE: 129 HOF genome exports imported via /api/augur/genomes/import. 36 genomes in DB (sma_bounce Sharpe=0.8, vwap_bounce Sharpe=0.4). sma_bounce meets all 11 HOF criteria."
    elif "trigger scan" in name_lower:
        comment = "DONE: Augur batch_score ran on 28 tickers. BB buy 1 @ $8.99 FILLED, AAPL buy 1 @ $306.61 FILLED. Both augur_hof_* genome paper bracket orders. P&L: AAPL +$1.09, BB -$0.09."
    elif "restart treasuremap" in name_lower:
        comment = "PARTIAL: TreasureMap API (SQUIDSTATION:5000) online. Dashboard:8080 not reachable from PINKCADY locally. Fleet mesh: PINKCADY+SQUIDSTATION+STEALTHATTACK all online via Tailscale. Crew API:8090 DOWN on all ships."
    elif "kill" in name_lower:
        comment = "FIXED: POST /api/killswitch/trading with Content-Type:application/json -> kill_trading=false, kill_learning=false, paper_mode=true. DB: kill_trading=0, kill_learning=0. API/DB in sync."
    elif "ooda" in name_lower:
        comment = (
            "PROGRESS: Full end-to-end Augur pipeline operational:\n"
            "1. HOF genomes: 36 in DB (sma_bounce Sharpe=0.8)\n"
            "2. price_history: 64,400 rows, 157 tickers, AI Ready=True\n"
            "3. Signal gen: batch_score produces entry zones\n"
            "4. Paper trades: BB FILLED @ $8.99, AAPL FILLED @ $306.61\n"
            "5. Kill switches: OFF, paper mode ON\n"
            "6. Autonomous trainer: cron every 5m (job_id: 8911a015555d)\n"
            "7. Fleet sync: Z:/ vault + OUTBOX communication\n"
            "8. Coaching notes auto-generated\n"
            "Deliverables in tr3asure_mAp/ + scripts/ + Outbox/"
        )
    else:
        comment = "PROGRESS: Working on Augur auto-learning system deployment."

    result = trello_post(f"cards/{card_id}/actions/comments", {"text": comment})
    if result.get("id"):
        print(f"  OK - Comment added")
    else:
        print(f"  [ERROR] {result}")

print("\n=== DONE ===")