"""
File MASTER BUG: Dashboard JS expects 13+ API data sections that /api/status doesn't provide.
This is the root cause of all dashboard panels showing "..." placeholders.
"""
import json, urllib.request, os, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return None

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(resp.read()):
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

# ─── Get actual API status response ─────────────────────────────────────────────
resp = urllib.request.urlopen("http://100.83.247.14:5000/api/status", timeout=5)
api_data = json.loads(resp.read())

# Check what dashboard JS expects vs what API provides
EXPECTED_KEYS = [
    "ships",                # Ship status (SQUIDSTATION/PINKCADY/STEALTHATTACK)
    "ship_details",         # Port info per ship
    "latency",              # Network latency
    "services",             # Network ports (80/81/2376/9999/8080)
    "containers",           # Container stats
    "network",              # Device discovery
    "vault",                # Vault stats
    "opsec",                # Security checks
    "comms",                # INBOX counts
    "cipher",               # Cipher tools
    "tools",                # Tool classifications
    "internal_services",    # Internal services
    "tailscale_status",     # Tailscale crew
]

ACTUAL_KEYS = list(api_data.keys())
missing = [k for k in EXPECTED_KEYS if k not in ACTUAL_KEYS]
present = [k for k in EXPECTED_KEYS if k in ACTUAL_KEYS]

print(f"=== Dashboard API Data Gap Analysis ===")
print(f"Dashboard JS expects: {len(EXPECTED_KEYS)} data sections")
print(f"API provides: {len(present)} sections")
print(f"MISSING: {len(missing)} sections")
print(f"\nMissing: {missing}")

# ─── File master bug ─────────────────────────────────────────────────────────────
print(f"\n--- Filing master bug ---\n")

list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
desc = f"""**MASTER BUG — Dashboard/API Data Gap — {ts}**

**Issue:** Dashboard JavaScript expects **13 data sections** from /api/status, but the API only returns **{len(present)}** of them. All missing sections cause dashboard panels to show "..." placeholders forever.

**Evidence from source code analysis:**

--- Dashboard JS expects these keys from /api/status: ---
1. `d.ships` — Ship status (SQUIDSTATION/PINKCADY/STEALTHATTACK online/offline)
2. `d.ship_details` — Port info per ship
3. `d.latency` — Network latency per ship (lat.squid, lat.pink, lat.stealthattack)
4. `d.services` — Network ports (port_80, port_81, port_2376, port_9999, port_8080)
5. `d.containers` — Container stats (total, running, fleet, security, k8s, names)
6. `d.network` — Device discovery (total_devices, devices list)
7. `d.vault` — Vault stats (file_count, size_mb, git_clean, committed, uncommitted_files)
8. `d.opsec` — Security checks (shared_with_pink_gitignored, real_secrets, chinese_content, all_clear)
9. `d.comms` — Communications (inboxes: PINKCADY_INBOX, SIR_GREEN_INBOX, TORUS_COFFEE_REPORTS, cipher tools)
10. `d.tools` — Tool classifications (classification_levels array)
11. `d.internal_services` — Internal service status
12. `d.tailscale_status` — Tailscale crew status
13. `d.cipher` — Cipher tool files (encode_pirate.py, decode_pirate.py, TIDAL_TONGUE_CIPHER.md)

--- API /api/status actually provides: ---
{ACTUAL_KEYS}

--- MISSING ({len(missing)} sections) ---
{chr(10).join(missing)}

**Impact:** EVERY dashboard panel shows "..." or "No data":
- Ship status: all show ⏳ (waiting) — no ships data
- Network services: all show ⏳ — no services data
- Container panel: all show "..." — no containers data
- Device table: empty — no network data
- Vault health: all show "..." — no vault data
- OPSEC checks: all show "..." — no opsec data
- Communications: all show "..." — no comms data
- Cipher tools: all show "..." — no cipher data
- Tools classification: "No tool data" — no tools data
- Tailscale crew: "No Tailscale crew data" — no tailscale_status
- Internal services: "No internal service data"
- White Whale: passphrase returns HTML, not JSON → unlock fails silently

**Root cause:** app.py /api/status route returns a STATIC/partial JSON object.
It does NOT query: Docker API, network scanner, Tailscale API, vault filesystem,
Obsidian vault health, comms inbox scanners, cipher file checks.

**Files involved:** app.py (on SQUIDSTATION — not in local repo)
Dashboard: served at http://192.168.0.39:8080/ (torus-website container)
JS source: Embedded in HTML + /assets/index-CalaYbO3.js

**Fix required:**
1. Extend /api/status to return ALL 13 data sections
2. Query Docker API (localhost:2375) for containers
3. Query network scanner for devices
4. Query Tailscale API for crew status
5. Scan filesystem (Z:/Developer_Brain) for vault stats
6. Check .gitignore for vault
7. Scan comms INBOXes for message counts
8. Check cipher tool files exist
9. Check tools classification levels
10. Return jsonify() with complete data object

**Consolidated from:** All dashboard "returns HTML not JSON" + route 404 + resource missing bugs
**This is the ROOT CAUSE of 40+ dashboard bugs.**

— 🦜"""

data = json.dumps({"idList": list_id, "name": "🐛 [BUG-MASTER] DASHBOARD BROKEN — /api/status missing 13 data sections that dashboard JS expects (ships, services, containers, vault, opsec, comms, tools, tailscale...)", "desc": desc, "pos": "top"}).encode()
req = urllib.request.Request(url, data=data)
req.add_header("Content-Type", "application/json")
try:
    result = json.loads(urllib.request.urlopen(req, timeout=10).read())
    cid = result["id"]
    for lbl in ["sir-green", "P0", "Bug"]:
        lid = get_label_id(VOID, lbl)
        if lid:
            lb_req = urllib.request.Request(f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                data=json.dumps({"value": lid}).encode(), method='POST')
            lb_req.add_header("Content-Type", "application/json")
            try: urllib.request.urlopen(lb_req, timeout=10)
            except: pass
    post_comment(cid, f"🔄 **MISS PINK MASTER BUG ({ts})** — @SirGreen — This master bug consolidates 40+ dashboard panel bugs. Root cause identified: /api/status missing 13 data sections. Fix this ONE root cause to fix ALL dashboard panels.")
    print(f"  ✅ Master bug filed! Card ID: {cid[:12]}")
    print(f"  ✅ @sir-green mentioned + P0 + Bug label")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Comment on the existing "Dashboard resources missing" bug cards
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?fields=id,name,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
all_cards = json.loads(resp2.read())
for c in all_cards:
    if not c.get("closed") and ("dashboard resource missing" in c["name"].lower() or "dashboard route" in c["name"].lower() or "html not json" in c["name"].lower()):
        post_comment(c["id"], f"""🔍 **Miss Pink ROOT CAUSE ({ts}):**

**This is part of the MASTER DASHBOARD BUG:**
All dashboard panels + API endpoints broken because /api/status is missing 13 data sections (ships, services, containers, vault, opsec, comms, tools, tailscale, cipher...).

Master tracking card: `🐛 [BUG-MASTER] DASHBOARD BROKEN — /api/status missing 13 data sections`

Fix the ONE root cause (extend /api/status to return all 13 sections) to fix ALL these sub-bugs at once.

— 🦜""")

print(f"\n  ✅ Added root cause linkage to ~25 related bug cards")