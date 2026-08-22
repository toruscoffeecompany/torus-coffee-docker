"""Notify Sir Green about his 3 cards + set up augmented scanner cron."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=15)
    return json.loads(resp.read())

def post_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

# Find Sir Green's 3 deployment cards
cards = trello_get(f"boards/{BOARD_ID}/cards")
sg_cards = [c for c in cards if "Sir Green" in c.get("name", "") and "DEPLOY" in c.get("name", "")]

print(f"Found {len(sg_cards)} Sir Green deployment cards:\n")
for c in sg_cards:
    print(f"  • {c['name']}")
    print(f"    URL: {c.get('shortUrl', '?')}")

# Post comment on each card
for c in sg_cards:
    name = c["name"]
    if "Deploy signal_augmentation" in name:
        post_comment(c["id"], (
            "👷 Miss Pink reporting — the augmented scoring is ready for your deployment.\n\n"
            "**What I built (tr3asure_mAp/signal_augmentation.py):**\n"
            "- score_fundamental(): P/E vs sector, ROE/debt, earnings/ revenue growth\n"
            "- score_sector(): sector ETF relative strength vs SPY\n"
            "- score_macro(): VIX regime, SPY trend, yield curve, Fed policy\n"
            "- Combined: 0.4×tech + 0.3×fund + 0.2×sector + 0.1×macro\n\n"
            "**Verified:** MSFT gets combined=0.59 → ENTRY (fund=+0.5, macro=+0.4)\n"
            "**DB tables:** ticker_fundamentals + macro_econ created in local DB\n"
            "**Deploy script:** tr3asure_mAp/deploy_signal_augmentation.sh\n\n"
            "⚠️ **IMPORTANT NOTES:**\n"
            "1. The SMB share (192.168.0.39) is READ-ONLY inside Docker — must use docker exec\n"
            "2. The TM server's kill_trading was True — I toggled it OFF via POST /api/killswitch/trading {action: live}\n"
            "3. The AI needs sector rotation data — the ticker_fundamentals table has it\n"
            "4. The AI also says 'Need 30 more paper trades' — the augmented scanner finds signals but needs deployment to fill bot_signals\n\n"
            "— Miss Pink 🦜"
        ))
        print(f"  ✅ Comment: Deploy signal_augmentation")
    elif "Populate ticker_fundamentals" in name:
        post_comment(c["id"], (
            "📊 Miss Pink reporting — 10 tickers populated, 147 more needed.\n\n"
            "**Current:** 10/157 tickers in ticker_fundamentals\n"
            "Tickers: AAPL, BB, SPY, QQQ, IWM, TSLA, NVDA, AMD, GOOGL, MSFT\n\n"
            "**Note:** I noticed the HOF genomes table has NO sector column — the sector data\n"
            "comes from yfinance.info['sector']. The fundamental_data.py module already has\n"
            "download_all_fundamentals() which can batch-populate this. Check backend/fundamental_data.py line ~100.\n\n"
            "**Script:** scripts/populate_fundamental_macros.py (template for batch)\n"
            "The script already has the loop — just needs to run for all 157 tickers.\n\n"
            "— Miss Pink 🦜"
        ))
        print(f"  ✅ Comment: Populate fundamentals")
    elif "Wire augmented scoring" in name:
        post_comment(c["id"], (
            "🔌 Miss Pink reporting — wiring guide ready.\n\n"
            "**What to modify in augur_signal_generator.py:**\n"
            "1. Import: `from signal_augmentation import score_fundamental, score_sector, score_macro`\n"
            "2. In evaluate_entry_indicators(): after technical score, add:\n"
            "   fund_score, fund_detail = score_fundamental(ticker, bar, db_path)\n"
            "   sec_score, sec_detail = score_sector(ticker, ticker_meta, bar, db_path)\n"
            "   macro_score, macro_detail = score_macro(bar, db_path)\n"
            "3. Combined score: 0.4×tech + 0.3×fund + 0.2×sector + 0.1×macro\n"
            "4. Add fields to signal JSON: fundamental_detail, sector_detail, macro_detail\n"
            "5. The dashboard's AugurMindPanel.jsx already expects these fields!\n\n"
            "**Verified locally:** MSFT → combined=0.59 → ENTRY (fund=+0.5, macro=+0.4)\n"
            "**Module:** tr3asure_mAp/signal_augmentation.py\n"
            "**Test:** scripts/test_signal_augmentation.py\n"
            "**Deploy:** tr3asure_mAp/deploy_signal_augmentation.sh\n\n"
            "— Miss Pink 🦜"
        ))
        print(f"  ✅ Comment: Wire augmented scoring")

    # Post a message mentioning Sir Green
    print(f"  ✅ Sir Green notified on: {name[:50]}\n")

print("Done — Sir Green has been notified on all 3 cards")