"""URGENT: Fix kill-switch state mismatch — kill_trading is True but should be False.
Also investigate Alpaca paper trade connection."""
import json, urllib.request, base64

ALPACA_KEY = "PKGH66PIW467YFQ2WFXSM7Y7I"
ALPACA_SECRET = "6rVGyGxu5PkkhNvozjKSXcNtfHV4qDgtpxjVymmSkDAa"
ALPACA_URL = "https://paper-api.alpaca.markets/v2"
TM_BASE = "http://100.83.247.14:5000"
TM_KEY = "treasuremap_secure_key_2026"

def tm_get(path):
    url = TM_BASE + path
    req = urllib.request.Request(url)
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def tm_post(path, data):
    url = TM_BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode())
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def alpaca_get(path):
    url = ALPACA_URL + path
    creds = base64.b64encode(f"{ALPACA_KEY}:{ALPACA_SECRET}".encode()).decode()
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {creds}")
    req.add_header("Alpaca-Header-Keys-Info", "true")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# ─── 1. Check current kill-switch state ───────────────────────────────────────
print("=== KILL-SWITCH STATE ===")
status = tm_get("/api/status")
print(f"  kill_trading: {status.get('kill_trading', '?')}")
print(f"  kill_learning: {status.get('kill_learning', '?')}")
print(f"  paper_mode: {status.get('paper_mode', '?')}")
print(f"  trading_enabled: {status.get('trading_enabled', '?')}")

# ─── 2. Try to toggle kill_trading OFF ────────────────────────────────────────
if status.get("kill_trading") == True:
    print("\n=== TOGGLING kill_trading OFF ===")
    result = tm_post("/api/toggle/kill_trading", {})
    print(f"  Toggle result: {result}")

# ─── 3. Re-check after toggle ────────────────────────────────────────────────
print("\n=== AFTER TOGGLE ===")
status2 = tm_get("/api/status")
print(f"  kill_trading: {status2.get('kill_trading', '?')}")

# ─── 4. Try Alpaca with different approaches ──────────────────────────────────
print("\n=== ALPACA API CHECK ===")
# Method 1: Direct URL
try:
    resp = urllib.request.urlopen(f"{ALPACA_URL}/account", timeout=15)
    acct = json.loads(resp.read())
    print(f"  Alpaca account: {acct.get('status', '?')}")
    print(f"  Cash: ${acct.get('cash','?')}")
    print(f"  Equity: ${acct.get('portfolio_value','?')}")
except Exception as e:
    print(f"  Direct Alpaca: {e}")

# Method 2: Via TM proxy
print("\n=== TM API PROXY ===")
acct_tm = tm_get("/api/status")
print(f"  TM status: {acct_tm.get('status', '?')}")
print(f"  TM trading_enabled: {acct_tm.get('trading_enabled', '?')}")

# ─── 5. Try direct Alpaca auth ────────────────────────────────────────────────
print("\n=== DIRECT ALPACA AUTH ===")
url = f"{ALPACA_URL}/account"
creds = base64.b64encode(f"{ALPACA_KEY}:{ALPACA_SECRET}".encode()).decode()
req = urllib.request.Request(url)
req.add_header("Authorization", f"Basic {creds}")
req.add_header("Alpaca-Header-Keys-Info", "true")
req.add_header("User-Agent", "AugurSignalBot/1.0")
try:
    resp = urllib.request.urlopen(req, timeout=15)
    acct = json.loads(resp.read())
    print(f"  Status: {acct.get('status','?')}")
    print(f"  Cash: ${acct.get('cash','?')}")
    print(f"  Equity: ${acct.get('portfolio_value','?')}")
    print(f"  Trading: {acct.get('trade_suspended_by_user','?')}")

    positions = urllib.request.urlopen(
        f"{ALPACA_URL}/positions",
        timeout=15
    )
    # Re-request with auth
    req2 = urllib.request.Request(f"{ALPACA_URL}/positions")
    req2.add_header("Authorization", f"Basic {creds}")
    req2.add_header("Alpaca-Header-Keys-Info", "true")
    pos_resp = urllib.request.urlopen(req2, timeout=15)
    positions = json.loads(pos_resp.read())
    print(f"  Positions: {len(positions)}")
    for p in positions:
        pl = float(p.get("unrealized_pl", 0))
        print(f"    {p['symbol']}: {p['qty']} @ {p['avg_entry_price']} | P&L: ${pl:+.2f}")

except Exception as e:
    print(f"  Error: {e}")

print("\n=== DONE ===")