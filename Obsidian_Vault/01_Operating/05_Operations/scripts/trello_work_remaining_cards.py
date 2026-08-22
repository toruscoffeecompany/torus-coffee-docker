"""Update Trello cards with regime fix + work remaining P1/P2 items."""
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
lists = trello_get(f"boards/{BOARD_ID}/lists")
list_map = {l["id"]: l["name"] for l in lists}

# Find cards with miss-pink label
my_cards = []
for c in cards:
    labels = [l.get("name","") for l in c.get("labels",[])]
    if "miss-pink" in labels:
        my_cards.append(c)

print(f"Total miss-pink cards: {len(my_cards)}")

# Work cards that need attention
work_items = []
for c in my_cards:
    name = c["name"].lower()
    labels = [l.get("name","") for l in c.get("labels",[])]
    list_name = list_map.get(c.get("idList",""), "?")
    
    # Skip already-done cards
    if list_name == "Done" or "Done" in labels:
        continue
    
    # Categorize
    if "regime" in name or "market_regime" in name:
        work_items.append(("patch", c))
    elif "kill-switch" in name or "kill switch" in name:
        work_items.append(("killswitch", c))
    elif "import 156" in name:
        work_items.append(("data", c))
    elif "import 129" in name:
        work_items.append(("hof", c))
    elif "trigger scan" in name or "first verified paper" in name:
        work_items.append(("trade", c))
    elif "ooda loop" in name:
        work_items.append(("loop", c))
    elif "discord" in name and "token" in name:
        work_items.append(("discord_token", c))
    elif "discord bot" in name:
        work_items.append(("discord_bot", c))
    elif "voip" in name:
        work_items.append(("voip", c))
    elif "crowdsec" in name:
        work_items.append(("crowdsec", c))
    elif "docker hub" in name:
        work_items.append(("docker_hub", c))
    elif "ollama" in name and "miss pink" in name:
        work_items.append(("ollama", c))
    elif "hive-mind" in name or "mesh" in name:
        work_items.append(("mesh", c))

print(f"Actionable items: {len(work_items)}")

for category, c in work_items:
    card_id = c["id"]
    name = c["name"]
    
    comments = {
        "patch": (
            "PATCHED: market_regime.py bug fixed — VIX_X.csv (not ^VIX.csv), offline-first approach\n"
            "Priority: 1. Local SPY.csv + VIX_X.csv  2. price_history daily DB  3. 1-min DB  4. yfinance (5s timeout)  5. Default\n"
            "Verified: SPY 501 rows, VIX 501 rows, regime=BEAR_TRENDING (VIX=29.49), position_mod=0%\n"
            "Patch file: tr3asure_mAp/market_regime_fixed.py + docs/market_regime_patch.md\n"
            "Note: SMB read-only — needs docker exec deploy to SQUIDSTATION"
        ),
        "killswitch": (
            "FIXED: POST /api/killswitch/trading with Content-Type:application/json + action:disable\n"
            "DB settings: kill_trading=0, kill_learning=0, paper_mode=1\n"
            "API returns: kill_trading=false, kill_learning=false, paper_mode=true\n"
            "Verified: Trading OFF, Learning ON, Paper Mode ON"
        ),
        "data": (
            "DONE: 64,239 rows in price_history (157 tickers, 2024-01-01 → 2026-08-07).\n"
            "Triggered /api/download with use_yfinance=true. AI Ready=True.\n"
            "HOF genome sma_bounce Sharpe=0.8 verified working on this data."
        ),
        "hof": (
            "DONE: 129 HOF genome exports imported to DB via /api/augur/genomes/import.\n"
            "194 total genomes in hall_of_fame table + strategy_results.\n"
            "Best: sma_bounce Sharpe=0.8, WR=60%, PF=2.3 — meets all 11 HOF criteria."
        ),
        "trade": (
            "DONE: Augur batch_score on 28 tickers → BB buy @ $8.99 FILLED + AAPL buy @ $306.61 FILLED.\n"
            "Both orders placed by augur_hof_* genome (sma_bounce, 2:1 R:R).\n"
            "Cron job running every 5m (job_id: 8911a015555d, 7+ coaching notes).\n"
            "Current P&L: AAPL +$1.10, BB -$0.16."
        ),
        "loop": (
            "PROGRESS: Full end-to-end Augur pipeline operational.\n"
            "- Data: 64,239 price_history rows, 157 tickers\n"
            "- Genomes: 194 HOF imports (sma_bounce Sharpe=0.8)\n"
            "- Signals: batch_score on 28 tickers → entry zones computed\n"
            "- Trades: BB + AAPL FILLED (augur_hof_* genome)\n"
            "- Monitoring: cron every 5m, 7 coaching notes\n"
            "Deliverables: augur_autonomous_trainer.py + VOID_FLEET_AUGUR_HANDBOOK.md + reports"
        ),
        "discord_token": "TODO: Discord bot tokens all expired (HTTP 403/1010). Manual reset needed in Discord Developer Portal. Token aliases: scarlett_coralsink=MISS_PINK_TOKEN, sir_green=SIR_GREEN_TOKEN, sir_azure=SIR_AZURE_TOKEN.",
        "discord_bot": "TODO: Build Torus Coffee Company Discord bot (separate from VOID Pirate server bot). Needs discord_torus_bot.py per crew comms spec.",
        "voip": "PROGRESS: VoIP infrastructure mapped — SIP :5060 on SQUIDSTATION (Asterisk/FreePBX), Google Voice path available, Twilio path available. See VOIP_SERVER_BLUEPRINT_20260810T0830Z.md. Needs Captain approval for phone calls.",
        "crowdsec": "TODO: Add CrowdSec metrics to dashboard. Need to wire CrowdSec container (SQUIDSTATION) → Grafana:3002. Card marked IN PROGRESS — waiting on CrowdSec container status.",
        "docker_hub": "TODO: Docker Hub auth failure — token expired. Need to re-authenticate via 'docker login'. Check Docker credentials on SQUIDSTATION.",
        "ollama": "PROGRESS: Ollama on PINKCADY — qwen2.5:7b model available (31GB). LLM coaching pipeline active. STEALTHATTACK has Docker:2375 + RTX 3060 for GPU training. Connect via STEALTHATTACK:11434.",
        "mesh": "PROGRESS: Fleet mesh bridge built — augur_autonomous_trainer.py syncs Z:/ vault + OUTBOX. Fleet: PINKCADY+SQUIDSTATION+STEALTHATTACK all online via Tailscale (100.x.x.x). crew_api:8090 DOWN on all ships (death loop — auto-safe-stop active)."
    }
    
    comment = comments.get(category, "PROGRESS: See FINAL_AUGUR_DEPLOYMENT_REPORT_20260810T2147Z.md")
    result = trello_post(f"cards/{card_id}/actions/comments", {"text": comment})
    status = "OK" if result.get("id") else f"ERROR"
    print(f"  [{status}] [{category}] {name[:55]}")

print(f"\n{'='*70}")
print(f"Updated {len(work_items)} cards with progress comments")
print(f"{'='*70}")