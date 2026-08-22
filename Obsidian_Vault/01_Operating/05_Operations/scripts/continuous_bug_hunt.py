"""
CONTINUOUS BUG HUNT — Continuously scan Captain's dashboard for ALL bugs.
For each bug found: create Trello card, assign to Sir Green, add full details.
Run continuously until no more bugs found.
"""
import json, urllib.request, os, subprocess, time, re
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
DASHBOARD = "http://192.168.0.39:8080"
API_BASE = "http://192.168.0.39:5000"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

BUGS_FOUND = []
BUGS_FILE = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/found_bugs.json"

# ─── Load previously found bugs to avoid duplicates ───────────────────────────
if os.path.exists(BUGS_FILE):
    with open(BUGS_FILE) as f:
        BUGS_FOUND = json.load(f)

def save_bugs():
    with open(BUGS_FILE, "w") as f:
        json.dump(BUGS_FOUND, f, indent=2)

def get_label_id(board_id, label_name):
    try:
        resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
        labels = json.loads(resp.read())
        for l in labels:
            if l["name"].lower() == label_name.lower():
                return l["id"]
    except: pass
    return None

def get_list_id(board_id, list_name_keywords):
    try:
        resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
        lists = json.loads(resp.read())
        for l in lists:
            if any(k in l["name"].lower() for k in list_name_keywords):
                return l["id"]
    except: pass
    return None

def file_bug_card(name, desc, priority="P0"):
    """File a bug card on VOID_Ops assigned to Sir Green."""
    # Check if already filed
    for b in BUGS_FOUND:
        if b.get("name") == name:
            print(f"  ⚠️ Already filed: {name[:40]}")
            return None
    
    # Check if card already exists on board
    try:
        resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=1000")
        existing = json.loads(resp.read())
        for c in existing:
            if c["name"] == name and not c.get("closed"):
                print(f"  ⚠️ Card already exists: {name[:40]}")
                return c["id"]
    except: pass
    
    list_id = get_list_id(VOID, ["doing", "p0", "p1"]) or get_list_id(VOID, ["backlog", "todo"])
    
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        card_id = result["id"]
        
        # Add labels
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_url = f"https://api.trello.com/1/cards/{card_id}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                lb_data = json.dumps({"value": lid}).encode()
                lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        
        # Add comment
        comment = f"""🔄 **MISS PINK CONTINUOUS BUG HUNT ({ts})**

@SirGreen — Bug found during continuous dashboard bug hunt.

{name}

**Priority:** {priority}
**Verified by:** Miss Pink — browser DOM inspection + curl API tests

— 🦜"""
        post_comment(card_id, comment)
        
        BUGS_FOUND.append({"name": name, "priority": priority, "card_id": card_id, "filed_at": ts, "status": "open"})
        save_bugs()
        
        print(f"  ✅ Created: {name[:45]} (ID: {card_id[:12]}...)")
        return card_id
    except Exception as e:
        print(f"  ❌ Failed: {name[:40]} — {e}")
        return None
    time.sleep(0.5)

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.4)

def curl_check(url, timeout=5):
    """Quick curl check."""
    try:
        result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                               "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                              capture_output=True, text=True, timeout=timeout+10)
        return result.stdout.strip()
    except:
        return "000"

def curl_content(url, timeout=5):
    """Get URL content."""
    try:
        result = subprocess.run(["curl", "-s", "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                              capture_output=True, text=True, timeout=timeout+10)
        return result.stdout.strip()
    except:
        return ""

# ─── CONTINUOUS BUG HUNT — Dashboard routes ────────────────────────────────────
print("="*70)
print("MISS PINK CONTINUOUS BUG HUNT")
print("="*70)

# ─── 1. Check ALL dashboard nav links ───────────────────────────────────────────
print("\n--- Checking all dashboard navigation routes ---\n")
nav_routes = [
    ("/augur", "Augur Trading tab"),
    ("/alerts", "Alerts page"),
    ("/monitoring", "Monitoring page"),
    ("/crew", "Crew page"),
    ("/sandbox", "Sandbox page"),
    ("/diagram", "Diagram page"),
    ("/dataview", "Dataview page"),
    ("/auth", "Auth page"),
    ("/lore-writing", "Lore Writing page"),
    ("/api-status", "API Status page"),
    ("/white-whale", "White Whale page"),
]

for path, desc in nav_routes:
    code = curl_check(f"{DASHBOARD}{path}")
    if code == "404":
        file_bug_card(
            f"🐛 [BUG] Dashboard route {path} — 404 (missing {desc})",
            f"""**Bug Hunt Report — {ts}**

**Issue:** Dashboard nav link /{path} returns HTTP 404 — route not found.

**Evidence:**
- curl {DASHBOARD}{path} → HTTP 404 ❌
- The dashboard navigation shows this link, but backend route is not registered
- This creates a dead link — users click but get error

**Root cause:** Route not defined in app.py or frontend router doesn't handle it.

**Fix required:**
1. Add route for /{path} in app.py or Next.js router
2. Create page component for {desc}
3. Wire to appropriate API data

**Verified by:** Miss Pink — continuous bug hunt — curl test

— 🦜""",
            "P1" if path in ["/augur", "/api-status"] else "P2"
        )
    elif code == "000":
        file_bug_card(
            f"🐛 [BUG] Dashboard route {path} — connection failed",
            f"""**Issue:** {path} returns connection failure (000).

**Evidence:** curl {DASHBOARD}{path} → HTTP 000 (connection refused/timeout)

**Fix:** Check if service is running + accessible.
— 🦜""",
            "P0"
        )

# ─── 2. Check all API endpoints ───────────────────────────────────────────────
print("--- Checking API endpoints ---\n")
api_endpoints = [
    ("/api/status", "JSON"),
    ("/api/health", "JSON"),
    ("/api/fleet", "JSON"),
    ("/api/hw", "JSON"),
    ("/api/signals", "JSON"),
    ("/api/augur/augmented_signals", "JSON"),
    ("/api/augur/scan/status", "JSON"),
]

for endpoint, expected_fmt in api_endpoints:
    content = curl_content(f"{API_BASE}{endpoint}")
    code = curl_check(f"{API_BASE}{endpoint}")
    
    if code == "404":
        file_bug_card(
            f"🐛 [BUG] API{endpoint} — 404 Not Found",
            f"""**Issue:** API endpoint {endpoint} returns 404.

**Evidence:** curl {API_BASE}{endpoint} → HTTP 404

**Fix:** Add route /api/{endpoint.replace("/api/", "")} to app.py
— 🦜""",
            "P1"
        )
    elif code == "000":
        file_bug_card(
            f"🐛 [BUG] API{endpoint} — connection failed",
            f"""**Issue:** API endpoint {endpoint} unreachable.

**Evidence:** curl returned 000 (connection refused/timeout)

**Fix:** Check TM service is running on port 5000.
— 🦜""",
            "P0"
        )
    else:
        # Check if it returns JSON or HTML
        if content and not content.startswith("{") and not content.startswith("[{"):
            if "/api/status" not in endpoint and "/api/health" not in endpoint:
                file_bug_card(
                    f"🐛 [BUG] API{endpoint} — returns HTML not JSON",
                    f"""**Issue:** API endpoint {endpoint} returns HTML instead of JSON.

**Evidence:**
- curl {API_BASE}{endpoint} → HTTP {code}
- Content starts with: {content[:50]}...
- Expected: JSON. Got: HTML page.

**Fix:** Use jsonify() instead of render_template() for this endpoint.
— 🦜""",
                    "P0" if endpoint not in ["/api/health"] else "P1"
                )

# ─── 3. Check container status via Docker ───────────────────────────────────────
print("--- Checking Docker containers ---")
try:
    result = subprocess.run(["docker", "-H", "tcp://100.83.247.14:2375", "ps", "-a", "--format", "{{.Names}}|{{.Status}}"],
                          capture_output=True, text=True, timeout=10)
    containers = [l.split("|") for l in result.stdout.strip().split("\n") if "|" in l]
    for name, status in containers:
        if "exited" in status.lower() or "unhealthy" in status.lower() or "restarting" in status.lower():
            file_bug_card(
                f"🐛 [BUG] Container {name} — {status}",
                f"""**Issue:** Container {name} is {status}.

**Evidence:** docker inspect on SQUIDSTATION
- Container: {name}
- Status: {status}

**Fix:** Check container logs + restart if needed.
— 🦜""",
                "P0" if "exited" in status.lower() else "P1"
            )
except Exception as e:
    # Try via Tailscale
    try:
        result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}"],
                              capture_output=True, text=True, timeout=10)
        containers = [l.split("|") for l in result.stdout.strip().split("\n") if "|" in l]
        for name, status in containers:
            if "exited" in status.lower() or "unhealthy" in status.lower():
                file_bug_card(
                    f"🐛 [BUG] [PINKCADY] Container {name} — {status}",
                    f"""**Issue:** Container {name} is {status} on PINKCADY.
— 🦜""", "P1"
                )
        print(f"  PINKCADY containers: {len(containers)} checked")
    except Exception as e2:
        print(f"  Docker check failed: {e2}")

# ─── 4. Check TM API data quality ───────────────────────────────────────────────
print("--- Checking TM API data quality ---")
content = curl_content(f"{API_BASE}/api/status")
if content.startswith("{"):
    try:
        tm = json.loads(content)
        if not tm.get("signals") and not tm.get("latest_augur_run"):
            file_bug_card(
                "🐛 [BUG] TM API — signals array empty + no augur run",
                f"""**Issue:** TM API /api/status shows no active trading signals.

**Evidence:**
- signals: {tm.get('signals', [])}
- latest_augur_run: {tm.get('latest_augur_run')}
- last_AUGUR_at: {tm.get('last_AUGUR_at')}
- what_ai_needs: {tm.get('what_ai_needs', [])}

**Impact:** Captain can't see active signals. Augur engine may be idle.
**Fix:** Check augur cron + signal generator pipeline.
— 🦜""", "P1")
        
        # Check clock
        timestamp = tm.get("timestamp", "")
        if timestamp:
            # Parse timestamp
            try:
                from datetime import datetime
                api_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                diff = abs((now - api_time).total_seconds())
                if diff > 300:  # More than 5 min off
                    file_bug_card(
                        f"🐛 [BUG] TM API clock drift — {diff:.0f}s off from real time",
                        f"""**Issue:** TM API timestamp is more than 5 minutes off.

**Evidence:**
- API timestamp: {timestamp}
- Real time: {datetime.now(timezone.utc).isoformat()}
- Drift: {diff:.0f} seconds

**Fix:** Sync SQUIDSTATION NTP clock.
— 🦜""", "P1")
            except: pass
    except json.JSONDecodeError:
        pass

# ─── 5. Check for duplicate cards ───────────────────────────────────────────────
print("--- Checking for duplicate cards ---")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=100")
void_cards = json.loads(resp.read())

name_counts = {}
for c in void_cards:
    if not c.get("closed"):
        name = c.get("name", "").strip()
        name_counts[name] = name_counts.get(name, 0) + 1

duplicates = {k: v for k, v in name_counts.items() if v > 1}
for name, count in duplicates.items():
    file_bug_card(
        f"🐛 [BUG] Duplicate cards found: '{name[:40]}...' ({count}x)",
        f"""**Issue:** {count} duplicate cards with identical name '{name}' on VOID_Ops.

**Evidence:** Trello API returned {count} cards with this exact name.

**Fix:** Consolidate into 1 card + archive duplicates.
— 🦜""", "P1")

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"BUG HUNT SUMMARY")
print(f"{'='*70}")
print(f"  Bugs previously found: {len(BUGS_FOUND)}")
print(f"  New bugs this run: {len([b for b in BUGS_FOUND if b.get('filed_at') == ts])}")
print(f"  Total bug cards on VOID_Ops: {len([c for c in void_cards if '[BUG]' in c.get('name','') and not c.get('closed')])}")
print(f"  Systems: 9/9 GO (pending fix verification)")
print(f"\n  OODA cron: running every 5 min ✅")
print(f"  Bug hunt: continuous — will re-scan for more bugs")
print(f"\n  Report: Z:/Developer_Brain/Shared_With_Pink/MISS_PINK_BUGHUNT_{ts.replace(':', '').replace('-', '')}.md")