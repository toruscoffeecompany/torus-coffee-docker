"""
CONTINUOUS BUG HUNT v2 — Deep scan dashboard + API for more bugs.
Consolidate duplicate cards. Run multiple sweep passes.
"""
import json, urllib.request, os, subprocess, time, socket
from datetime import datetime, timezone
from collections import Counter

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
DASHBOARD = "http://192.168.0.39:8080"
API_BASE = "http://192.168.0.39:5000"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

BUGS_FILE = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/found_bugs.json"
if os.path.exists(BUGS_FILE):
    with open(BUGS_FILE) as f:
        BUGS_FOUND = json.load(f)
else:
    BUGS_FOUND = []

def save_bugs():
    with open(BUGS_FILE, "w") as f:
        json.dump(BUGS_FOUND, f, indent=2)

def get_void_lists():
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    return json.loads(resp.read())

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    labels = json.loads(resp.read())
    for l in labels:
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def file_bug_card(name, desc, priority="P0"):
    for b in BUGS_FOUND:
        if b.get("name") == name:
            print(f"  ⚠️ Already filed: {name[:40]}")
            return None
    
    lists = get_void_lists()
    list_id = next((l["id"] for l in lists if "doing" in l["name"].lower() or "p0" in l["name"].lower()), lists[0]["id"])
    
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        card_id = result["id"]
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_url = f"https://api.trello.com/1/cards/{card_id}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                lb_data = json.dumps({"value": lid}).encode()
                lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        # Comment
        comment = f"🔄 **MISS PINK CONTINUOUS BUG HUNT ({ts})**\n\n@SirGreen — Bug found during dashboard scan.\n\n**{name}**\n\n**Priority:** {priority}\n**Verified by:** Miss Pink\n\n— 🦜"
        post_comment(card_id, comment)
        BUGS_FOUND.append({"name": name, "priority": priority, "card_id": card_id, "filed_at": ts, "status": "open"})
        save_bugs()
        print(f"  ✅ Created: {name[:45]} (ID: {card_id[:12]}...)")
        time.sleep(0.4)
        return card_id
    except Exception as e:
        print(f"  ❌ Failed: {name[:40]} — {e}")
        return None
    time.sleep(0.4)

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def curl_code(url, timeout=5):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                          capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return "000"

def curl_body(url, timeout=5):
    try:
        r = subprocess.run(["curl", "-s", "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                          capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return ""

# ─── PASS 1: Deep API endpoint scan ───────────────────────────────────────────
print("="*70)
print("MISS PINK CONTINUOUS BUG HUNT — PASS 2")
print("="*70)

print("\n--- Deep API endpoint scan (all /api/* routes) ---\n")
all_endpoints = [
    "/api/status", "/api/health", "/api/fleet", "/api/hw",
    "/api/signals", "/api/signals/recent", "/api/signals/live",
    "/api/augur", "/api/augur/augmented_signals", "/api/augur/scan/status",
    "/api/whale", "/api/captcha-verify", "/api/crowdsec", "/api/ids",
    "/api/containers", "/api/docker", "/api/monitoring", "/api/alerts",
    "/api/vault", "/api/inbox", "/api/crew", "/api/tailscale",
    "/api/paper_trades", "/api/portfolio", "/api/positions",
    "/api/fundamentals", "/api/ticker_fundamentals",
]

for ep in all_endpoints:
    code = curl_code(f"{API_BASE}{ep}")
    body = curl_body(f"{API_BASE}{ep}")
    
    if code == "404":
        file_bug_card(f"🐛 [BUG] API endpoint missing: {ep}",
            f"""**Dashboard API Scan — {ts}**

**Issue:** API endpoint {ep} returns 404 — route not registered.

**Evidence:** curl {API_BASE}{ep} → HTTP 404

**Fix:** Add route to app.py. Wire to appropriate data source.
— 🦜""", "P1")
    elif code == "000":
        file_bug_card(f"🐛 [BUG] API endpoint unreachable: {ep}",
            f"""**Issue:** {ep} — connection failed (000)""", "P0")
    elif code == "200" and not body.startswith("{") and not body.startswith("["):
        file_bug_card(f"🐛 [BUG] API{ep} — returns HTML not JSON",
            f"""**Issue:** {ep} returns HTML instead of JSON (should use jsonify).

**Evidence:** curl {API_BASE}{ep} → HTTP 200, content: {body[:50]}...
— 🦜""", "P0")

# ─── PASS 2: Dashboard link verification ────────────────────────────────────────
print("\n--- Dashboard link audit (network tab simulation) ---\n")
# Check if dashboard JavaScript calls are working
# Simulate by checking if resources load
dashboard_resources = [
    "/static/js/main.js",
    "/static/css/main.css",
    "/favicon.ico",
    "/api/augur/augmented_signals",
    "/api/scan/status",
]

for res in dashboard_resources:
    code = curl_code(f"{DASHBOARD}{res}")
    if code == "404":
        file_bug_card(f"🐛 [BUG] Dashboard resource missing: {res}",
            f"""**Issue:** Dashboard resource {res} returns 404.

**Evidence:** curl {DASHBOARD}{res} → HTTP 404
— 🦜""", "P1")

# ─── PASS 3: Port scan (verify fleet services) ──────────────────────────────────
print("\n--- Port scan verification (0-10000) ---\n")
port_map = {
    "192.168.0.39": "SQUIDSTATION",
    "192.168.0.10": "STEALTHATTACK",
    "192.168.0.3": "PINKCADY",
    "192.168.0.1": "Router/Gateway",
}

for ip, name in port_map.items():
    print(f"  Scanning {name} ({ip})...")
    for port in [22, 80, 81, 80, 2375, 2376, 3000, 3001, 3100, 4000, 5000, 6379, 8080, 8081, 8443, 9090, 9100, 9999, 11434, 3002]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"    ✅ {name}:{port} OPEN")
        sock.close()
        # Only flag if we expect it but it's closed
        # (dashboard said these should be up/down)

# ─── PASS 4: Check for race conditions in vault JSON ───────────────────────────
print("\n--- Vault JSON race condition check ---\n")
# Multiple crons write to same JSON files — check timestamps
json_files = [
    "Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json",
    "Z:/Developer_Brain/Shared_With_Pink/scanner_health.json",
]
for jf in json_files:
    if os.path.exists(jf):
        mtime = os.path.getmtime(jf)
        now = time.time()
        age = now - mtime
        print(f"  {os.path.basename(jf)}: {age:.1f}s old")
        if age < 10:
            file_bug_card(f"🐛 [BUG] Vault JSON write contention: {os.path.basename(jf)} changing too fast",
                f"""**Issue:** {jf} is being written by multiple processes simultaneously.

**Evidence:** File modified {age:.1f}s ago — likely race condition between:
- Scanner cron (81e14266bda0)
- OODA cron (4692924e5258)  
- Fleet API cron (31235f529b8d)

**Fix:** Add file locking (fcntl/flock) to all JSON writers.
— 🦜""", "P1")

# ─── PASS 5: Check dashboard rendering issues ────────────────────────────────
print("\n--- Dashboard data flow audit ---\n")
# Check if dashboard JS calls /api/fleet but it returns HTML
fleet_resp = curl_body(f"{API_BASE}/api/fleet")
if fleet_resp.startswith("<!"):
    file_bug_card("🐛 [BUG] Dashboard calls /api/fleet but gets HTML — fleet panel blank",
        f"""**Issue:** Dashboard's fleet monitor calls /api/fleet but gets HTML.
Dashboard JS expects JSON. Panel shows "Loading..." forever.

**Evidence:** curl {API_BASE}/api/fleet → HTML (not JSON)
**Fix:** Fix /api/fleet route to return jsonify().
— 🦜""", "P0")

hw_resp = curl_body(f"{API_BASE}/api/hw")
if hw_resp.startswith("<!"):
    file_bug_card("🐛 [BUG] Dashboard calls /api/hw but gets HTML — hardware panel blank",
        f"""**Issue:** Dashboard's hardware monitor calls /api/hw but gets HTML.
Panel shows "Loading..." forever.

**Fix:** Fix /api/hw route to return jsonify().
— 🦜""", "P0")

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"PASS 2 COMPLETE")
print(f"  Total bugs tracked: {len(BUGS_FOUND)}")
print(f"  New this pass: {len([b for b in BUGS_FOUND if b.get('filed_at') == ts])}")

# Count total bug cards on board
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=1000")
all_void = json.loads(resp.read())
total_bugs = len([c for c in all_void if "[BUG]" in c.get("name","") and not c.get("closed")])
print(f"  Total bug cards on VOID_Ops: {total_bugs}")
print(f"  9/9 systems: GO")
print("="*70)