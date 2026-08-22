"""Find the right TM API endpoints for learning + signal generation."""
import json, urllib.request

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

def tm_post(path, data=None):
    url = TM_BASE + path
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", TM_KEY)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# ─── Find all API endpoints ┘
endpoints_to_try = [
    "/api/", "/api/status", "/api/scan", "/api/scan/signals",
    "/api/augur/scan", "/api/augur/scan_signals", "/api/augur/learn",
    "/api/learning", "/api/learning/run", "/api/learning/cycle",
    "/api/ai/learn", "/api/ai/run", "/api/augur/run", "/api/augur/step",
    "/api/scanner/signals", "/api/scanner/scan", "/api/scanner/run",
    "/api/augur/last_signal", "/api/augur/generate_signal",
    "/api/augur/evaluate", "/api/augur/evaluate_entry",
    "/api/paper/scan", "/api/paper/trade",
    "/api/trade/execute", "/api/trade/scan", "/api/trade/signals",
    "/api/executor", "/api/executor/state", "/api/executor/run",
    "/api/scan/paper", "/api/paper_mode/scan",
]

print("=== API ENDPOINT SCAN ===")
for ep in endpoints_to_try:
    # Try GET
    r = tm_get(ep)
    if "error" not in r and r:
        if isinstance(r, dict):
            keys = list(r.keys())[:5]
            print(f"  GET {ep}: keys={keys}")
        elif isinstance(r, list):
            print(f"  GET {ep}: list({len(r)} items)")
    # Try POST with empty body
    r2 = tm_post(ep)
    if "error" not in r2 and r2:
        if isinstance(r2, dict):
            keys2 = list(r2.keys())[:5]
            print(f"  POST {ep}: keys={keys2}")

# ─── Try signal generation with specific parameters ───────────────────────────
print("\n=== Signal Generation Attempts ===")
signals_tried = [
    ("/api/scan", {"mode": "paper", "generate_signals": True}),
    ("/api/scan", {"tickers": ["AAPL"], "mode": "signal"}),
    ("/api/scan", {"mode": "live", "tickers": ["AAPL", "NVDA"]}),
    ("/api/augur/scan", {"mode": "paper"}),
    ("/api/scanner/run", {"mode": "paper"}),
    ("/api/trade/capture", {"ticker": "AAPL", "mode": "paper"}),
]
for ep, data in signals_tried:
    r = tm_post(ep, data)
    if "error" not in r and r:
        if isinstance(r, dict):
            print(f"  POST {ep} {data}: {json.dumps(r, indent=2, default=str)[:300]}")
        elif isinstance(r, list):
            print(f"  POST {ep} {data}: {len(r)} items")
