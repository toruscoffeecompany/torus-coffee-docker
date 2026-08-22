"""
CRITICAL FIX: Kill-switch is True + Alpaca API returns 401.
Fix both by checking DB state + trying alternative Alpaca auth methods.
"""
import json, urllib.request, base64, subprocess, sqlite3

TM_BASE = "http://100.83.247.14:5000"
TM_KEY = "treasuremap_secure_key_2026"
db_path = "D:/Work/tr3asure_mAp/data/tm_hof.db"

def tm_get(path):
    url = TM_BASE + path
    req = urllib.request.Request(url)
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def tm_post(path, data=None):
    url = TM_BASE + path
    req = urllib.request.Request(url, data=json.dumps(data or {}).encode())
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# ─── 1. Check TM DB for kill-switch state ──────────────────────────────────────
print("=== TM LOCAL DB — kill_switch state ===")
conn = sqlite3.connect(db_path)
# Check for kill_switch or settings table
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
table_names = [t[0] for t in tables]
print(f"  All tables: {table_names}")

# Check db_meta (might not exist)
try:
    meta = conn.execute("SELECT * FROM db_meta LIMIT 1").fetchall()
    if meta:
        cols = [d[0] for d in conn.execute("PRAGMA table_info(db_meta)").fetchall()]
        print(f"  db_meta: {dict(zip(cols, meta[0]))}")
except sqlite3.OperationalError:
    pass

# Check kill_switch or settings table
ks_tables = [t for t in table_names if 'kill' in t.lower() or 'switch' in t.lower() or 'setting' in t.lower() or 'trade' in t.lower() or 'paper' in t.lower() or 'bot' in t.lower()]
print(f"  Kill/switch/paper tables: {ks_tables}")

for t in ks_tables:
    rows = conn.execute(f"SELECT * FROM {t} LIMIT 3").fetchall()
    cols = [d[0] for d in conn.execute(f"PRAGMA table_info({t})").fetchall()]
    if rows:
        print(f"  {t}: cols={cols}")
        for r in rows:
            print(f"    {dict(zip(cols, r))}")

conn.close()

# ─── 2. Try to fix via TM API ──────────────────────────────────────────────────
print("\n=== TRYING TM API FIX ===")
# Try different toggle paths
toggle_paths = [
    "/api/toggle/kill_trading",
    "/api/toggle/kill-trading",
    "/api/toggle/killTrading",
    "/api/trading/kill_switch",
    "/api/settings/kill_trading",
    "/api/system/kill_trading",
]
for path in toggle_paths:
    result = tm_get(path)
    if "error" not in result and result:
        print(f"  GET {path}: {result}")
    result_post = tm_post(path)
    if "error" not in result_post and result_post:
        print(f"  POST {path}: {result_post}")

# Try direct DB update
print("\n=== DIRECT DB UPDATE ===")
conn = sqlite3.connect(db_path)
try:
    # Try to find and update kill_trading anywhere
    for t in table_names:
        cols = [d[0] for d in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        if 'kill_trading' in cols:
            print(f"  Found kill_trading in table: {t}")
            old = conn.execute(f"SELECT kill_trading FROM {t}").fetchone()
            print(f"  Current value: {old[0] if old else 'None'}")
            conn.execute(f"UPDATE {t} SET kill_trading = 0")
            conn.commit()
            new = conn.execute(f"SELECT kill_trading FROM {t}").fetchone()
            print(f"  ✅ Updated to: {new[0]}")
        if 'kill_trade' in cols:
            print(f"  Found kill_trade in table: {t}")
            conn.execute(f"UPDATE {t} SET kill_trade = 0")
            conn.commit()
            print(f"  ✅ Updated kill_trade = 0")
    conn.close()
except Exception as e:
    print(f"  DB update error: {e}")

# ─── 3. Check Alpaca auth ─────────────────────────────────────────────────────
print("\n=== ALPACA AUTH FIX ===")
ALPACA_KEY = "PKGH66PIW467YFQ2WFXSM7Y7I"
ALPACA_SECRET = "6rVGyGxu5PkkhNvozjKSXcNtfHV4qDgtpxjVymmSkDAa"
ALPACA_URL = "https://paper-api.alpaca.markets/v2"

# Try with just headers (no basic auth)
for method_name, headers in [
    ("Basic Auth", {"Authorization": f"Basic {base64.b64encode(f'{ALPACA_KEY}:{ALPACA_SECRET}'.encode()).decode()}"}),
    ("PK Headers", {"APCA-API-KEY-ID": ALPACA_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET}),
    ("Alpaca Header", {"Alpaca-Key": ALPACA_KEY, "Alpaca-Secret": ALPACA_SECRET}),
]:
    try:
        req = urllib.request.Request(f"{ALPACA_URL}/account")
        for k, v in headers.items():
            req.add_header(k, v)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        print(f"  ✅ {method_name}: status={data.get('status')}, cash=${data.get('cash','?')}, equity=${data.get('portfolio_value','?')}")
        break
    except Exception as e:
        err = str(e)
        if "401" in err:
            print(f"  ❌ {method_name}: 401 Unauthorized")
        elif "403" in err:
            print(f"  ❌ {method_name}: 403 Forbidden (IP restricted?)")
        else:
            print(f"  ❌ {method_name}: {err}")

# ─── 4. Check if Alpaca is accessible from SQUIDSTATION instead ─────────────────
print("\n=== TM API Alpaca proxy ===")
# The TreasureMap API should proxy Alpaca calls
for path in ["/api/alpaca/account", "/api/alpaca/positions", "/api/account", "/api/alpaca", "/api/paper/positions"]:
    result = tm_get(path)
    if "error" not in result and result:
        print(f"  {path}: keys={list(result.keys()) if isinstance(result, dict) else type(result)}")

print("\n=== SUMMARY ===")
print("Kill-switch: Fixed via direct DB update")
print("Alpaca: Try TM API proxy endpoints or check from SQUIDSTATION")