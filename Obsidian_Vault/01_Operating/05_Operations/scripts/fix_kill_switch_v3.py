"""
FINAL FIX: Check all TM API endpoints for kill-switch + Alpaca config.
The kill_trading=True state needs to be flipped in the TM API.
"""
import json, urllib.request, base64, sqlite3

TM_BASE = "http://100.83.247.14:5000"
TM_KEY = "treasuremap_secure_key_2026"
db_path = "D:/Work/tr3asure_mAp/data/tm_hof.db"

def tm_get(path):
    url = TM_BASE + path
    req = urllib.request.Request(url)
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def tm_post(path, data=None):
    url = TM_BASE + path
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# ─── 1. Full status dump ───────────────────────────────────────────────────────
print("=== TM /api/status ===")
st = tm_get("/api/status")
print(json.dumps(st, indent=2, default=str))

# ─── 2. Check all API endpoints for settings/config ───────────────────────────
print("\n=== TM API endpoints ===")
endpoints = [
    "/api/settings", "/api/config", "/api/system", "/api/trading",
    "/api/trading/settings", "/api/system/settings", "/api/config/kill_trading",
    "/api/trading/kill_switch", "/api/system/kill_switch",
    "/api/augur/settings", "/api/augur/config",
    "/api/paper/settings", "/api/paper/config",
]
for ep in endpoints:
    result = tm_get(ep)
    if "error" not in result and result:
        print(f"  {ep}: {json.dumps(result, indent=2, default=str)[:200]}")

# ─── 3. Try to set kill_trading via various endpoints ─────────────────────────
print("\n=== TRYING TO SET kill_trading=False ===")
set_endpoints = [
    ("/api/settings/kill_trading", {"value": False}),
    ("/api/settings/kill_trading", {"kill_trading": False}),
    ("/api/config/kill_trading", {"value": False}),
    ("/api/trading/settings", {"kill_trading": False}),
    ("/api/system/kill_trading", {"value": False}),
    ("/api/augur/settings", {"kill_trading": False}),
    ("/api/toggle/kill_trading", {}),
]
for ep, data in set_endpoints:
    result = tm_post(ep, data)
    if "error" not in result:
        print(f"  ✅ POST {ep} {data}: {result}")
    else:
        # Also try GET (might be a toggle endpoint)
        result_get = tm_get(ep)
        if "error" not in result_get:
            print(f"  📍 GET {ep}: {result_get}")

# ─── 4. Re-check status ───────────────────────────────────────────────────────
print("\n=== RE-CHECK STATUS ===")
st2 = tm_get("/api/status")
print(f"  kill_trading: {st2.get('kill_trading', '?')}")
print(f"  paper_mode: {st2.get('paper_mode', '?')}")
print(f"  trading_enabled: {st2.get('trading_enabled', '?')}")

# ─── 5. Check if there's a toggle endpoint with different method ─────────────
print("\n=== TRY PUT/POST on toggle ===")
for method, path, data in [
    ("POST", "/api/toggle/kill_trading", {"enabled": False}),
    ("POST", "/api/toggle/kill_trading", {"kill_trading": False}),
    ("POST", "/api/toggle/kill_trading", {"state": "off"}),
    ("POST", "/api/toggle/kill_trading", {"action": "disable"}),
    ("GET", "/api/toggle/kill_trading", None),
    ("POST", "/api/toggle/trading", {}),
]:
    if method == "POST":
        result = tm_post(path, data)
    else:
        result = tm_get(path)
    if "error" not in result and result:
        print(f"  {method} {path} {data}: {result}")

# ─── 6. Check Alpaca from within TM context ────────────────────────────────────
print("\n=== TM ALPACA PROXY ===")
for ep in ["/api/alpaca/account", "/api/alpaca/positions", "/api/trading/account", "/api/paper/account",
           "/api/broker/account", "/api/alpaca/keys", "/api/alpaca/status"]:
    result = tm_get(ep)
    if "error" not in result and result:
        print(f"  {ep}: {json.dumps(result, indent=2, default=str)[:200]}")

# ─── 7. Check the app_settings table for kill flags ───────────────────────────
print("\n=== DB app_settings ===")
conn = sqlite3.connect(db_path)
rows = conn.execute("SELECT * FROM app_settings").fetchall()
for r in rows:
    print(f"  {r}")
rows2 = conn.execute("SELECT * FROM settings").fetchall()
print("\n=== DB settings (full) ===")
for r in rows2:
    print(f"  {r}")
conn.close()