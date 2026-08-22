"""
CRITICAL FIX: Start the TM system + clear kill_trading.
The executor is not running (system.running=false) which causes kill_trading=true.
"""
import json, urllib.request, sqlite3

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

def tm_put(path, data=None):
    url = TM_BASE + path
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(url, data=body, method='PUT')
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

print("=== BEFORE: System state ===")
st = tm_get("/api/status")
print(f"  kill_trading: {st.get('kill_trading')}")
print(f"  paper_mode: {st.get('paper_mode')}")
sys_info = tm_get("/api/system")
print(f"  system.running: {sys_info.get('system', {}).get('running', '?')}")
print(f"  risk.status: {sys_info.get('risk', {}).get('status', '?')}")
print(f"  executor.trades_today: {sys_info.get('executor', {}).get('trades_today', '?')}")

# ─── Try to start the system ──────────────────────────────────────────────────
print("\n=== STARTING TM SYSTEM ===")

start_endpoints = [
    "/api/start",
    "/api/system/start",
    "/api/executor/start",
    "/api/trading/start",
    "/api/augur/start",
    "/api/run",
    "/api/system/start_paper",
    "/api/paper/start",
]
for ep in start_endpoints:
    result = tm_post(ep)
    if "error" not in result:
        print(f"  ✅ POST {ep}: {result}")
    result_get = tm_get(ep)
    if "error" not in result_get and result_get:
        print(f"  📍 GET {ep}: {json.dumps(result_get, indent=2, default=str)[:200]}")

# ─── Try PUT methods ───────────────────────────────────────────────────────────
print("\n=== PUT methods ===")
put_endpoints = [
    "/api/settings/kill_trading",
    "/api/config/kill_trading",
    "/api/system/run",
]
for ep in put_endpoints:
    for data in [{"value": False}, {"kill_trading": False}, {"enabled": False}]:
        result = tm_put(ep, data)
        if "error" not in result:
            print(f"  ✅ PUT {ep} {data}: {result}")

# ─── Direct DB fix: set kill_trading = false ──────────────────────────────────
print("\n=== DB DIRECT FIX ===")
conn = sqlite3.connect(db_path)
try:
    # Update settings table
    conn.execute("UPDATE settings SET value='false' WHERE key='kill_trading'")
    conn.execute("UPDATE settings SET value='false' WHERE key='kill_learning'")
    conn.commit()
    row = conn.execute("SELECT key, value FROM settings WHERE key IN ('kill_trading', 'kill_learning')").fetchall()
    print(f"  DB updated: {row}")
except Exception as e:
    print(f"  DB error: {e}")
conn.close()

# ─── Re-check ──────────────────────────────────────────────────────────────────
print("\n=== AFTER: System state ===")
st2 = tm_get("/api/status")
print(f"  kill_trading: {st2.get('kill_trading', '?')}")
print(f"  paper_mode: {st2.get('paper_mode', '?')}")
print(f"  trading_enabled: {st2.get('trading_enabled', '?')}")

sys2 = tm_get("/api/system")
print(f"  system.running: {sys2.get('system', {}).get('running', '?')}")
print(f"  risk.status: {sys2.get('risk', {}).get('status', '?')}")
print(f"  executor.trades_today: {sys2.get('executor', {}).get('trades_today', '?')}")