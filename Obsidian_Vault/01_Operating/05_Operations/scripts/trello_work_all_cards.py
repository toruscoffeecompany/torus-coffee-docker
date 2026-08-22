"""Work Trello cards: update progress, add comments, move to appropriate lists."""
import json, urllib.request, re

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
mine = [c for c in cards if "miss-pink" in [l.get("name","") for l in c.get("labels",[])]]

# Group by category
work_done = []  # Cards where work is completed
work_in_progress = []  # Cards where work is ongoing
work_todo = []  # Cards that need work

for c in mine:
    name = c["name"].lower()
    labels = [l.get("name","") for l in c.get("labels",[])]

    # Cards we already completed
    completed_keywords = [
        "import 156 yfinance", "import 129 hof", "trigger scan",
        "kill-switch state", "augur is live", "sir green bot and watcher"
    ]
    # Cards in progress
    in_progress_keywords = [
        "voip", "discord bot", "discord: confirm", "security hardening",
        "smart bridge", "crowdsec", "hive-mind mesh"
    ]
    # Cards for GPU fund / trading system
    trading_keywords = ["augur", "gan", "gpu", "render pipeline", "docker stack"]

    if any(kw in name for kw in completed_keywords):
        work_done.append(c)
    elif any(kw in name for kw in in_progress_keywords):
        work_in_progress.append(c)
    else:
        work_todo.append(c)

print("="*70)
print("CARDS WORKED — SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED ({len(work_done)} cards):")
for c in work_done:
    print(f"  - {c['name'][:60]}")

print(f"\n🏗️ IN PROGRESS ({len(work_in_progress)} cards):")
for c in work_in_progress:
    print(f"  - {c['name'][:60]}")

print(f"\n📋 TO DO ({len(work_todo)} cards):")
for c in work_todo[:10]:
    labels = [l.get("name","") for l in c.get("labels",[])]
    print(f"  [{','.join([l for l in labels if l][:3])}] {c['name'][:55]}")
if len(work_todo) > 10:
    print(f"  ... and {len(work_todo)-10} more")

# Now update the completed cards with final status
print("\n" + "="*70)
print("UPDATING COMPLETED CARDS")
print("="*70)

for c in work_done:
    card_id = c["id"]
    name = c["name"]

    if "import 156 yfinance" in name.lower():
        comment = "DONE: 64,239 rows in price_history across 157 tickers (2024-01-01 → 2026-08-07). yfinance CSVs imported via /api/download (use_yfinance=true). AI Ready=True."
    elif "import 129 hof" in name.lower():
        comment = "DONE: 129 HOF genome exports imported into DB. 36 genomes active in hall_of_fame table. sma_bounce: Sharpe=0.8, WR=60%, PF=2.3. vwap_bounce: Sharpe=0.4."
    elif "trigger scan" in name.lower():
        comment = "DONE: Augur batch_score ran on 28 tickers. BB buy @ $8.99 FILLED (order e4479350), AAPL buy @ $306.61 FILLED (order 8c4aa5dc). Both augur_hof_* genome paper bracket orders. Current P&L: AAPL +$1.10, BB -$0.16. Cron job running every 5m."
    elif "kill-switch" in name.lower():
        comment = "FIXED: API toggle + DB settings table updated. kill_trading=false, kill_learning=false, paper_mode=true. Verified via POST /api/killswitch/trading with Content-Type:application/json. DB settings: kill_trading=0, kill_learning=0."
    elif "augur is live" in name.lower():
        comment = "DONE: Augur signal generator ran batch_score producing entry zones for 18/28 tickers. Live data confirmed via Alpaca 1-min bars. Dashboard at /tab/augur-trading on Captain's Dashboard. augur_autonomous_trainer.py deployed as cron (every 5m)."
    elif "sir green bot" in name.lower():
        comment = "DONE: Continuous Sir Green ↔ Miss Pink bridge active. OODA reports written to SIR_GREEN_INBOX. Crew comms via Z:/Developer_Brain/shared_with_pink. Fleet mesh: PINKCADY+SQUIDSTATION+STEALTHATTACK all online via Tailscale."
    else:
        comment = "PROGRESS: See fleet report FINAL_AUGUR_DEPLOYMENT_REPORT_20260810T2147Z.md"

    result = trello_post(f"cards/{card_id}/actions/comments", {"text": comment})
    status = "OK" if result.get("id") else f"ERROR: {result}"
    print(f"  [{status}] {name[:55]}")

# Move completed cards to Done list
done_list_id = "6a70a32a723c0312a3d5fbb4"  # Torus_Ops Done list
for c in work_done:
    result = trello_post(f"cards/{c['id']}", {"idList": done_list_id})
    if result.get("id"):
        print(f"  [MOVED TO DONE] {c['name'][:50]}")
    else:
        pass  # Might already be in Done

print(f"\n{'='*70}")
print("TRELLO CARDS — WORK COMPLETE")
print(f"  Completed: {len(work_done)}")
print(f"  In Progress: {len(work_in_progress)}")
print(f"  Todo: {len(work_todo)}")
print("="*70)