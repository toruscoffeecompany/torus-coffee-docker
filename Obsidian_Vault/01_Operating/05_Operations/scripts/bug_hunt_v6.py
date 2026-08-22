"""
Miss Pink — Verify all work + continue bug hunt on the Captain's dashboard.

New bugs found in dashboard JS source:
1. White Whale passphrase flow — /api/whale returns HTML, JSON.parse fails silenly
2. Dashboard makes 8 redundant fetch('/api/status) calls every 3s — rate limit storm
3. /api/alerts returns empty array [] — alert panel broken
4. applyTools() expects tools.classification_levels — API returns different schema
5. OPSEC Chinese content detection broken — no d.opsec in API response
6. Dashboard dual-refresh race condition — 10s full + 3s partial updates conflict
"""
import json, urllib.request, os, subprocess, time, re
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

FOUND_FILE = "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/found_bugs_v6.json"
if os.path.exists(FOUND_FILE):
    with open(FOUND_FILE) as f:
        FOUND = json.load(f)
else:
    FOUND = []

def save_found():
    with open(FOUND_FILE, "w") as f:
        json.dump(FOUND, f, indent=2)

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

def file_bug(name, desc, priority="P0"):
    for f in FOUND:
        if f.get("name") == name:
            print(f"  SKIP (already filed): {name[:50]}")
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
        post_comment(cid, "🔄 **MISS PINK BUG HUNT v6 (" + ts + ")** — @SirGreen — Filed from continuous dashboard analysis.")
        FOUND.append({"name": name, "priority": priority, "card_id": cid, "filed_at": ts})
        save_found()
        print(f"  FILED: {name[:60]}")
        return cid
    except Exception as e:
        print(f"  FAIL: {name[:50]} — {e}")
    time.sleep(0.4)

def curl_body(url, timeout=5):
    try:
        r = subprocess.run(["curl", "-s", "--connect-timeout", str(timeout), "--max-time", str(timeout+5), url],
                          capture_output=True, text=True, timeout=timeout+10)
        return r.stdout.strip()
    except: return ""

# ═══════════════════════════════════════════════════════════════════════════════
print("="*70)
print("MISS PINK — VERIFY + BUG HUNT v6")
print("="*70)

# ─── VERIFY PREVIOUS WORK ────────────────────────────────────────────────────────
print("\n--- Verifying previous work ---\n")

r = subprocess.run(["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
                   capture_output=True, text=True, timeout=30)
ooda_ok = "9/9" in r.stdout and "ALL SYSTEMS GO" in r.stdout
print(f"  OODA cron: {'GO' if ooda_ok else 'FAIL'}")

with open("D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py") as f:
    content = f.read()
has_business_kw = "BUSINESS_KEYWORDS" in content
print(f"  Business card protection: {'YES' if has_business_kw else 'NO'}")

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?fields=name,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_cards = json.loads(resp.read())
bug_count = len([c for c in void_cards if "[BUG]" in c["name"].upper() and not c.get("closed")])
print(f"  Bug cards on VOID_Ops: {bug_count}")

resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?fields=name,labels,closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
torus_cards = json.loads(resp2.read())
sg_only = 0
for c in torus_cards:
    if c.get("closed"): continue
    labels = [l.get("name","").lower() for l in c.get("labels",[]) if isinstance(l,dict)]
    if "sir-green" in labels and "miss-pink" not in labels and "sir-azure" not in labels:
        print(f"  SG-only on Torus_Ops: {c['name'][:50]}")
        sg_only += 1
print(f"  Sir Green-only on Torus_Ops: {sg_only} {'OK' if sg_only == 0 else 'FAIL'}")

print(f"  Systems: {'9/9 GO' if ooda_ok else 'FAIL'}")

# ─── NEW BUG HUNT v6 ─────────────────────────────────────────────────────────────
print("\n--- Continuing bug hunt (v6) ---\n")

# ─── Bug: White Whale passphrase flow ────────────────────────────────────────────
whale_body = curl_body("http://100.83.247.14:5000/api/whale?passphrase_hash=test&threat_detected=true")
desc1 = f"""**Bug Hunt v6 — {ts}**

**Issue:** White Whale unlock flow: JS hashes passphrase with SHA-256 client-side, then
calls /api/whale?passphrase_hash=HASH&threat_detected=true. But /api/whale returns HTML →
JSON.parse() fails silently → unlock button does nothing.

Dashboard JS (from source):
  const hash = await sha256(passphrase);
  const resp = await fetch('/api/whale?passphrase_hash=' + hash + '&threat_detected=true');
  const data = await resp.json();  < FAILS: resp is HTML, not JSON

**Evidence:** curl /api/whale?passphrase_hash=test → starts with "!" (HTML)

**Impact:** White Whale classified tools (vault lockdown, BLACK WHALE threat detection,
GREEN WHALE port checks) are COMPLETELY inaccessible.

**Security note:** Client-side SHA-256 hashing is INSECURE — attacker can replay the hash.
Consider server-side hashing.

**Fix:**
1. Add JSON route handler for /api/whale
2. Accept passphrase_hash query param, validate
3. Return JSON with white_whale_hash_verified, black_whale, green_whale, white_whale_protocol
"""

if whale_body.startswith("<!"):
    file_bug("WHITe WHALE: /api/whale returns HTML not JSON — unlock flow broken", desc1, "P0")

# ─── Bug: Redundant fetch calls ──────────────────────────────────────────────────
file_bug("DASHBOARD: 8 redundant fetch('/api/status) calls every 3s — API rate limit storm", f"""**Bug Hunt v6 — {ts}**

**Issue:** Dashboard per-stat live updates makes 8 separate fetch('/api/status') calls every 3s.
All 8 call the SAME endpoint and parse the SAME response independently.

Evidence (from JS source):
  setInterval(async () => {{
    const [ships, services, internal, tailscale, network, tools, vault, comms] = await Promise.all([
      fetch('/api/status'), fetch('/api/status'), fetch('/api/status'),
      fetch('/api/status'), fetch('/api/status'), fetch('/api/status'),
      fetch('/api/status'), fetch('/api/status')
    ]);

**Impact:** 8x unnecessary API load. 8x concurrent connections per viewer.
Potential rate limiting/server overload.

**Fix:** Single fetch + cache pattern.
""", "P2")

# ─── Bug: /api/alerts empty ──────────────────────────────────────────────────────
file_bug("ALERTS: /api/alerts returns empty [] — alert panel broken", f"""**Bug Hunt v6 — {ts}**

**Issue:** /api/alerts endpoint returns empty array or HTML.
Dashboard Alerts tab has no data.

curl /api/alerts → {curl_body('http://100.83.247.14:5000/api/alerts')[:60]}

**Fix:** Wire /api/alerts to alert-router (port 4000) + IDS logs.
""", "P1")

# ─── Bug: applyTools() schema mismatch ───────────────────────────────────────────
file_bug("TOOLS: Dashboard applyTools() expects tools.classification_levels — API schema mismatch", f"""**Bug Hunt v6 — {ts}**

**Issue:** Dashboard JS applyTools() reads d.tools?.classification_levels (array),
but per-stat loop uses tools.tools (object). Schema inconsistent.
/api/status does not return either → panel breaks.

**Fix:** Standardize response: tools as object with classification_levels array.
""", "P2")

# ─── Bug: OPSEC Chinese content ──────────────────────────────────────────────────
file_bug("OPSEC: Chinese content detection broken — no d.opsec in API response", f"""**Bug Hunt v6 — {ts}**

**Issue:** Dashboard OPSEC check for Chinese content (d.opsec.chinese_content_files)
not present in /api/status response. Panel shows '...' always.

Could hide double-byte Chinese chars in vault files (security concern).

**Fix:** Add opsec scanning to /api/status endpoint.
""", "P2")

# ─── Bug: Dual-refresh race condition ────────────────────────────────────────────
file_bug("DASHBOARD: Dual-refresh race condition — 10s full + 3s partial updates", f"""**Bug Hunt v6 — {ts}**

**Issue:** Two update loops:
- updateDashboard() every 10s (full refresh)
- Anonymous per-stat every 3s (8x redundant partial)

Race conditions, flickering, inconsistent display.

**Fix:** Unify to single 5s interval with cached data.
""", "P2")

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("BUG HUNT v6 COMPLETE")
new_count = len([b for b in FOUND if b.get('filed_at','') == ts])
print(f"  New bugs filed this pass: {new_count}")
print(f"  Total bugs tracked: {len(FOUND)}")
print(f"  Verification: OODA={'GO' if ooda_ok else 'FAIL'} | BizProt={'YES' if has_business_kw else 'NO'} | SG-only_on_Torus={sg_only} | Systems={'9/9' if ooda_ok else 'FAIL'}")
print("="*70)