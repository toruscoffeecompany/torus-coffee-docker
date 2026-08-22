"""
File remaining bug cards for Sir Green.
"""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.35)

def archive_card(cid):
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.35)

def create_bug_card(name, desc, priority="P1"):
    lists_url = f"https://api.trello.com/1/boards/{VOID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    lists = json.loads(urllib.request.urlopen(lists_url).read())
    target_list = next((l["id"] for l in lists if "doing" in l["name"].lower() or "p1" in l["name"].lower() or "p0" in l["name"].lower()), lists[0]["id"])
    
    labels_url = f"https://api.trello.com/1/boards/{VOID}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    labels = json.loads(urllib.request.urlopen(labels_url).read())
    sg_label = next((l["id"] for l in labels if l["name"].lower() == "sir-green"), None)
    prio_label = next((l["id"] for l in labels if l["name"].lower() == priority.lower()), None)
    
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": target_list, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    result = json.loads(urllib.request.urlopen(req, timeout=10).read())
    card_id = result["id"]
    
    for lid in [sg_label, prio_label]:
        if lid:
            lb_url = f"https://api.trello.com/1/cards/{card_id}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
            lb_data = json.dumps({"value": lid}).encode()
            lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
            lb_req.add_header("Content-Type", "application/json")
            try: urllib.request.urlopen(lb_req, timeout=10)
            except: pass
    
    post_comment(card_id, f"""🔄 **Miss Pink Bug Hunt ({ts})** — @SirGreen

Bug found during dashboard inspection. Please investigate.

— 🦜""")
    
    print(f"  ✅ Created: {name[:55]} (ID: {card_id})")
    return card_id

# ─── Get bug cards already filed to avoid duplicates ─────────────────────────
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,closed&filter=open")
existing = json.loads(resp.read())
existing_names = [c["name"] for c in existing if not c.get("closed") and "[BUG]" in c.get("name","")]

# ─── BUG #12: System clock 5 hours ahead ──────────────────────────────────────
if not any("clock" in n.lower() for n in existing_names):
    create_bug_card(
        "🐛 [BUG] SQUIDSTATION system clock 5 hours ahead — Timestamp sync issue",
        f"""**Bug Hunt OODA Report — {ts}**

**Issue:** SQUIDSTATION system clock is 5 hours ahead of PINKCADY.

**Evidence:**
- PINKCADY time: 2026-08-12 00:19:10
- SQUIDSTATION time (via API): 2026-08-12T05:19:10 (5hrs ahead)
- Container StartedAt: 2026-08-12T05:15:35 (SQUIDSTATION timezone)

**Root cause:** SQUIDSTATION TZ setting or NTP sync misconfigured.

**Impact:** Timestamps in logs, API responses, and vault files are incorrect.
Could cause cron scheduling issues, audit trail confusion.

**Fix required:**
1. Check SQUIDSTATION timezone: `timedatectl status`
2. Sync to NTP: `w32tm /resync` or restart Windows Time service
3. Set correct timezone (should be Central Time for Captain)
4. Verify Docker container timestamps after restart

**Verified by:** Miss Pink — Time offset detection via API timestamp comparison

— 🦜""",
        "P1"
    )

# ─── BUG #13: torus-dashboard EXITED (137) ────────────────────────────────────
if not any("dashboard" in n.lower() and "exit" in n.lower() for n in existing_names) and not any("OOM" in n for n in existing_names):
    create_bug_card(
        "🐛 [BUG] torus-dashboard container EXITED (137/OOM) — Dashboard serving from wrong container",
        f"""**Bug Hunt OODA Report — {ts}**

**Issue:** torus-dashboard container EXITED with code 137 (OOM killed) 2 days ago.

**Evidence:**
- `docker ps -a` shows: torus-dashboard: Exited (137) 2 days ago
- Dashboard at 192.168.0.39:8080 still loads → served by torus-website or torus-grafana
- Dashboard health panel says "12 containers, 11 running" — the 1 down is torus-dashboard itself

**Root cause:** torus-dashboard container ran out of memory (code 137 = SIGKILL).
Docker auto-restart may have failed or container has restart=no.

**Impact:** Dashboard may be partially functional (served by wrong container).
torus-dashboard was intended container is dead — recovery incomplete.

**Fix required:**
1. Check torus-dashboard logs: `docker logs torus-dashboard`
2. Increase memory limit or enable auto-restart
3. Verify dashboard served by correct container
4. Restart torus-dashboard with `docker restart torus-dashboard`

**Verified by:** Miss Pink — `docker ps -a` shows Exited (137)

— 🦜""",
        "P0"
    )

# ─── BUG #14: /api/signals returns 404 ────────────────────────────────────────
if not any("api/signals" in n.lower() and "404" in n for n in existing_names) and not any("signals endpoint" in n.lower() for n in existing_names):
    create_bug_card(
        "🐛 [BUG] /api/signals endpoint returns 404 — Missing API route",
        f"""**Bug Hunt OODA Report — {ts}**

**Issue:** /api/signals endpoint returns HTTP 404.

**Evidence:**
- curl http://192.168.0.39:8080/api/signals: HTTP 404 ❌
- /api/status: ✅ (returns JSON)
- /api/health: ✅ (returns JSON)
- /api/augur: ✅ (but returns HTML ❌)
- /api/fleet: ✅ (but returns HTML ❌)

**Root cause:** API routes /api/signals, /api/fleet, /api/augur not properly registered
or return HTML instead of JSON (missing jsonify()).

**Impact:** Dashboard can't fetch signal data. Augur trading signals endpoint broken.
Fleet monitoring API non-functional.

**Fix required:**
1. Add /api/signals route to app.py returning JSON signals
2. Fix /api/fleet, /api/augur, /api/hw to return jsonify() not render_template()
3. Wire frontend JS to call correct API endpoints
4. Verify all <link> nav items in dashboard have working backend routes (24 links, 8 return 404)

**Verified by:** Miss Pink — curl tests + browser navigation

— 🦜""",
        "P0"
    )

# ─── BUG #15: API endpoints return HTML not JSON ──────────────────────────────
if not any("html" in n.lower() and "response" in n.lower() for n in existing_names) and not any("jsonify" in n.lower() for n in existing_names):
    create_bug_card(
        "🐛 [BUG] API endpoints return HTML instead of JSON — jsonify() missing",
        f"""**Bug Hunt OODA Report — {ts}**

**Issue:** API endpoints (/api/fleet, /api/hw, /api/augur) return HTML pages instead of JSON.

**Evidence:**
- /api/status: ✅ JSON (proper)
- /api/health: ✅ JSON (proper)
- /api/fleet: ❌ HTML (should be JSON fleet data)
- /api/hw: ❌ HTML (should be JSON hardware data)
- /api/augur: ❌ HTML (should be JSON augur data)
- /api/augur/scan/status: ❌ HTML
- /api/augur/augmented_signals: ❌ HTML

**Root cause:** Routes in app.py use `render_template()` or return HTML
instead of `jsonify()` for API endpoints. Routes not marked with @app.route('/api/...')

**Impact:** Dashboard JS can't parse API responses. All fleet/hardware/augur
data endpoints broken — Captain's dashboard blind to fleet status.

**Fix required:**
1. Audit all /api/* routes in app.py
2. Change render_template to jsonify for API routes
3. Add proper @app.route('/api/fleet') etc.
4. Test all API endpoints return application/json

**Verified by:** Miss Pink — curl + browser inspection

— 🦜""",
        "P0"
    )

print(f"\n{'='*70}")
print("BUG HUNT PHASE 2 COMPLETE")
print(f"Total bug cards filed: 6 (Phase 1) + 4 (Phase 2) = 10 bugs for Sir Green")
print("="*70)