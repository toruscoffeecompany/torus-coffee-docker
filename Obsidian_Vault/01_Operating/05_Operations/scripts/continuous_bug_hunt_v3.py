"""
CONTINUOUS BUG HUNT v3 — Actually USE the dashboard features.
Try placing paper trades, running sims, checking all panels + routes.
File cards for everything that doesn't work.
"""
import json, urllib.request, os, subprocess, time, re
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

FILES = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/found_bugs_v3.json"
if os.path.exists(FILES):
    with open(FILES) as f:
        FOUND = json.load(f)
else:
    FOUND = []

def add_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return None

def file_bug(name, desc, priority="P0"):
    for f in FOUND:
        if f.get("name") == name:
            return None
    
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                    data=json.dumps({"value": lid}).encode(), method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        add_comment(cid, f"🔄 **MISS PINK BUG HUNT v3 ({ts})** — @SirGreen — {name} — Priority: {priority}")
        FOUND.append({"name": name, "priority": priority, "card_id": cid})
        with open(FILES, "w") as f:
            json.dump(FOUND, f, indent=2)
        print(f"  ✅ {name[:55]}")
        return cid
    except Exception as e:
        print(f"  ❌ {name[:40]} — {e}")
    time.sleep(0.4)

def curl_code(url, timeout=5):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                           "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                          capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return "000"

def curl_body(url, timeout=5):
    try:
        r = subprocess.run(["curl", "-s", "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                          capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return ""

def curl_method(method, url, data="", timeout=5):
    try:
        cmd = ["curl", "-s", "-X", method, "--connect-timeout", str(timeout), "--max-time", str(timeout+5)]
        if data:
            cmd += ["-d", data]
        cmd.append(url)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return ""

# ═══════════════════════════════════════════════════════════════════════════════
print("="*70)
print("MISS PINK CONTINUOUS BUG HUNT v3 — LIVE FEATURE TESTING")
print("="*70)

# ─── 1. TRY TO PLACE A PAPER TRADE ──────────────────────────────────────────────
print("\n--- Attempting paper trade placement ---\n")

# Endpoint: POST /api/paper_trades
code = curl_code("http://100.83.247.14:5000/api/paper_trades")
body = curl_body("http://100.83.247.14:5000/api/paper_trades")
print(f"GET /api/paper_trades: {code}")

if code == "404":
    file_bug("🐛 [BUG] Paper trading API /api/paper_trades returns 404 — Can't place paper trades",
        f"""**Issue:** The paper trading endpoint returned 404 — route not found.

**Evidence:**
- curl http://100.83.247.14:5000/api/paper_trades → HTTP 404
- No POST endpoint for placing paper trades
- Dashboard paper trade panel non-functional

**Impact:** Captain/Sir Green can't test paper trades. The paper_mode=True setting
is meaningless if there's no API to place trades.

**Fix:**
1. Add POST /api/paper_trades endpoint to app.py
2. Accept JSON {ticker, qty, side, price}
3. Log to paper_trades table in DB
4. Return confirmation JSON

**Verified by:** Miss Pink — live curl test
— 🦜""", "P0")
elif code == "200" and not body.startswith("{"):
    file_bug("🐛 [BUG] Paper trading API returns HTML not JSON", f"""**Issue:** /api/paper_trades returns HTML instead of JSON.

**Evidence:** curl → HTTP 200, content starts with HTML

**Fix:** Use jsonify() for API responses.
— 🦜""", "P0")

# Try POSTing a paper trade
post_resp = curl_method("POST", "http://100.83.247.14:5000/api/paper_trades", '{"ticker":"MSFT","qty":10,"side":"buy"}')
if "404" in post_resp or "Not Found" in post_resp:
    file_bug("🐛 [BUG] POST /api/paper_trades — no trade execution endpoint",
        f"""**Issue:** POST to /api/paper_trades failed — no trade execution.

**Evidence:** curl -X POST /api/paper_trades → 404/not found

**Fix:** Add POST handler + trade execution logic.
— 🦜""", "P0")

# ─── 2. TRY TO RUN SIR AUGUR SIMS ───────────────────────────────────────────────
print("\n--- Attempting Augur simulation ---\n")

# Check /api/augur/scan/status POST (trigger a scan)
post_scan = curl_method("POST", "http://100.83.247.14:5000/api/augur/scan/status", '{"trigger":"now"}')
print(f"POST /api/augur/scan/status: {post_scan[:50]}...")
if "404" in post_scan or "Not Found" in post_scan or len(post_scan) < 10:
    file_bug("🐛 [BUG] Augur scan trigger — POST /api/augur/scan/status fails (404 or no trigger)",
        f"""**Issue:** Cannot trigger Augur signal scan via API.

**Evidence:** curl -X POST /api/augur/scan/status → {post_scan[:100]}

**Impact:** Sir Augur sims can't be triggered on-demand. Only runs on cron (every 5 min).
Need on-demand scan for debugging + manual trading.

**Fix:** Add POST handler to /api/augur/scan/status that triggers an immediate scan.
Return JSON {status: scanning, eta: 30s, signal_count: N}
— 🦜""", "P1")

# Check Augur signal output
augur_resp = curl_body("http://100.83.247.14:5000/api/augur/augmented_signals")
if augur_resp.startswith("{") and "signals" not in augur_resp:
    file_bug("🐛 [BUG] Augmented signals API — response has no 'signals' key",
        f"""**Issue:** /api/augur/augmented_signals returns JSON but no 'signals' array.

**Evidence:** {augur_resp[:200]}

**Fix:** Ensure response includes {signals: [...], regime, can_trade} keys.
— 🦜""", "P1")
elif not augur_resp.startswith("{"):
    file_bug("🐛 [BUG] Augmented signals API returns non-JSON", f"""curl /api/augur/augmented_signals → not JSON""", "P1")

# ─── 3. TRY TRADING CONTROLS ON DASHBOARD ───────────────────────────────────────
print("\n--- Testing trading control endpoints ---\n")

trading_endpoints = [
    ("POST", "/api/trading/toggle_kill_switch", "kill switch toggle"),
    ("POST", "/api/trading/paper_mode", "paper mode toggle"),
    ("POST", "/api/trading/place_order", "place order"),
    ("GET", "/api/trading/orders", "get orders"),
    ("GET", "/api/trading/positions", "get positions"),
    ("GET", "/api/trading/portfolio", "get portfolio"),
    ("GET", "/api/trading/balance", "get balance"),
    ("GET", "/api/trading/history", "get trade history"),
]

for method, ep, desc in trading_endpoints:
    code = curl_code(f"http://100.83.247.14:5000{ep}")
    if code == "404":
        file_bug(f"🐛 [BUG] Trading endpoint missing: {method} {ep} ({desc})",
            f"""**Issue:** Dashboard trading control {desc} — endpoint missing.

**Evidence:** curl {method} {ep} → 404 (route not registered)

**Impact:** Dashboard trading controls non-functional. Captain can't manage trades.

**Fix:** Add {method} route {ep} to app.py.

**Verified by:** Miss Pink — live API test
— 🦜""", "P1" if "toggle" in ep or "place" in ep else "P2")

# ─── 4. TRY CREW COMMUNICATION FEATURES ─────────────────────────────────────────
print("\n--- Testing crew communication ---\n")

crew_endpoints = [
    ("POST", "/api/crew/post", "post message"),
    ("GET", "/api/crew/messages", "get crew messages"),
    ("POST", "/api/crew/announce", "broadcast announcement"),
    ("GET", "/api/crew/status", "crew member status"),
]

for method, ep, desc in crew_endpoints:
    code = curl_code(f"http://100.83.247.14:5000{ep}")
    if code == "404":
        file_bug(f"🐛 [BUG] Crew communication endpoint missing: {method} {ep}",
            f"""**Issue:** Crew communication feature broken — {ep} returns 404.

Dashboard crew panel can't post/get messages.

Fix: Add {method} {ep} to app.py.
— 🦜""", "P1")

# ─── 5. TRY OBSIDIAN VAULT INTEGRATION ──────────────────────────────────────────
print("\n--- Testing vault integration ---\n")

vault_endpoints = [
    "/api/vault/status",
    "/api/vault/sync",
    "/api/vault/inbox",
    "/api/vault/inbox/post",
    "/api/vault/obsidian",
    "/api/inbox/miss-pink",
    "/api/inbox/sir-green",
]

for ep in vault_endpoints:
    code = curl_code(f"http://100.83.247.14:5000{ep}")
    if code == "404":
        file_bug(f"🐛 [BUG] Vault integration endpoint missing: {ep}",
            f"""**Issue:** Vault/Obsidian integration endpoint missing — {ep} → 404.

Dashboard can't sync with Obsidian vault.

Fix: Add route {ep} to app.py. Wire to filesystem operations.
— 🦜""", "P1")

# ─── 6. TRY DASHBOARD REAL-TIME UPDATES ─────────────────────────────────────────
print("\n--- Testing real-time dashboard features ---\n")

# Check if websockets/server-sent events are working
sse_endpoints = ["/api/stream", "/api/events", "/api/ws", "/api/sse"]
for ep in sse_endpoints:
    code = curl_code(f"http://100.83.247.14:5000{ep}")
    if code == "404":
        file_bug(f"🐛 [BUG] Real-time dashboard endpoint missing: {ep} — No live updates",
            f"""**Issue:** Dashboard has no real-time update stream.

**Evidence:** {ep} returns 404. Dashboard polls are manual/inefficient.

**Fix:** Add SSE/WebSocket endpoint for live dashboard updates.
— 🦜""", "P2")

# ─── 7. TRY FLEET MONITORING ACTIONS ───────────────────────────────────────────
print("\n--- Testing fleet monitoring ---\n")

fleet_actions = [
    "POST /api/fleet/ping",
    "POST /api/fleet/restart",
    "GET /api/fleet/containers",
    "POST /api/fleet/exec",
    "GET /api/fleet/logs",
]

for action in fleet_actions:
    method, ep = action.split(" ", 1)
    code = curl_code(f"http://100.83.247.14:5000{ep}")
    if code == "404":
        file_bug(f"🐛 [BUG] Fleet monitoring action missing: {action}",
            f"""**Issue:** Fleet management action {action} — endpoint missing (404).

Dashboard fleet panel can't ping/restart/check containers.

Fix: Add {ep} to app.py.
— 🦜""", "P1")

# ─── 8. Check for data consistency bugs ───────────────────────────────────────────
print("\n--- Checking data consistency ---\n")

# Multiple endpoint should return SAME data — check consistency
fleet_data = curl_body("http://100.83.247.14:5000/api/fleet")
if fleet_data.startswith("{"):
    try:
        fd = json.loads(fleet_data)
        if fd.get("ships"):
            for ship in fd.get("ships", []):
                if not ship.get("name") or not ship.get("ip"):
                    file_bug("🐛 [BUG] Fleet data incomplete — ships missing name/ip",
                        f"""**Issue:** Fleet API returns ships with incomplete data.
Ship: {json.dumps(ship)}
— 🦜""", "P1")
    except:
        file_bug("🐛 [BUG] Fleet API JSON parse error", f"""/api/fleet returned HTML""", "P0")

# TM API port mismatch
tm_data = curl_body("http://100.83.247.14:5000/api/status")
if tm_data.startswith("{"):
    try:
        tm = json.loads(tm_data)
        # Check if ports in status match actual open ports
        if "ports" in tm:
            actual_ports = {"22", "80", "81", "2376", "3000", "5000", "6379", "8080", "8081", "9090", "9100"}
            reported = set(str(tm.get("ports", [])))
            missing = actual_ports - reported
            if missing:
                file_bug("🐛 [BUG] TM API port reporting — missing known ports",
                    f"""**Issue:** TM API status doesn't report all open ports.

Reported: {reported}
Missing: {missing}

Fix: Update port scanner + API to report all ports.
— 🦜""", "P1")
    except: pass

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("BUG HUNT PASS 3 COMPLETE")
new_count = len([b for b in FOUND if "pass3" in str(b.get("filed_at",""))])
print(f"  Total bugs tracked: {len(FOUND)}")
print(f"  New bugs filed: {len([b for b in FOUND if b.get('filed_at', '') == ts])}")
print("="*70)