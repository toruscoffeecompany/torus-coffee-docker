#!/usr/bin/env python3
"""
Miss Pink — Post-reorganization dashboard bug scan.
Verify Sir Green's fixes + file any remaining/new bugs.
"""
import json, subprocess, urllib.request
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
API = "http://100.83.247.14:5000"
DASH = "http://192.168.0.39:8080"

def api_get(path):
    try:
        r = urllib.request.urlopen(f"{API}{path}", timeout=5)
        body = r.read().decode()[:500]
        if body.startswith('{') or body.startswith('['):
            return "JSON", json.loads(body)
        return "HTML", body[:100]
    except Exception as e:
        return "ERR", str(e)

def trello_post(name, desc):
    # Get list ID
    r = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    for l in json.loads(r.read()):
        if "p0" in l["name"].lower() or "p1" in l["name"].lower() or "backlog" in l["name"].lower():
            list_id = l["id"]
            break
    # Get labels
    r2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    labels = {l["name"].lower(): l["id"] for l in json.loads(r2.read())}
    
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", "p1", "bug"]:
            if lbl in labels:
                lb_req = urllib.request.Request(
                    f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}",
                    data=json.dumps({"value": labels[lbl]}).encode(), method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        return cid[:12]
    except Exception as e:
        return f"FAIL: {e}"

print(f"=== POST-ORGANIZATION DASHBOARD SCAN — {ts} ===\n")

# ─── 1. Check TM API status ─────────────────────────────────────────────────────
print("1. TM API STATUS:")
type_s, tm = api_get("/api/status")
if type_s == "JSON":
    print(f"  kill_trading: {tm.get('kill_trading')} {'✅ FIXED' if tm.get('kill_trading')==False else '❌ STILL TRUE'}")
    print(f"  paper_mode: {tm.get('paper_mode')}")
    print(f"  signals: {len(tm.get('signals', []))}")
    print(f"  sim_lifetime_count: {tm.get('sim_lifetime_count')}")
    print(f"  latest_augur_run: {tm.get('latest_augur_run')}")
    print(f"  status: {tm.get('status')}")
else:
    print(f"  API returned {type_s}: {tm[:80]}")

# ─── 2. Check the 13 missing API sections ────────────────────────────────────────
print(f"\n2. MASTER BUG — /api/status 13 sections:")
expected = ["ships","ship_details","latency","services","containers","network",
    "vault","opsec","comms","cipher","tools","internal_services","tailscale_status"]
missing = [k for k in expected if k not in (tm if type_s=="JSON" else {})]
print(f"  Missing: {len(missing)}/13 → {missing[:5]}...")
if len(missing) == 0:
    print("  ✅ MASTER BUG FIXED!")
else:
    print(f"  ❌ Master bug STILL present")

# ─── 3. Endpoint scan ───────────────────────────────────────────────────────────
print(f"\n3. ENDPOINT SCAN:")
endpoints = ["/api/status","/api/whale","/api/orders","/api/balance","/api/history",
    "/api/crew_heartbeat","/api/sandbox","/api/fleet","/api/vault/status","/api/inbox",
    "/api/monitoring","/api/ids","/api/containers","/api/docker",
    "/api/captcha-verify","/api/crowdsec","/api/augur","/api/vault/health",
    "/api/opsec/chinese_content","/api/tools/classification"]

json_eps = []
html_eps = []
for ep in endpoints:
    type_r, body = api_get(ep)
    status = "✅ JSON" if type_r == "JSON" else "❌ HTML" if type_r == "HTML" else f"❌ {type_r}"
    if type_r == "JSON": json_eps.append(ep)
    elif type_r == "HTML": html_eps.append(ep)
    print(f"  {ep:30s} {status}")

print(f"\n  JSON: {len(json_eps)} | HTML: {len(html_eps)}")

# ─── 4. Check dashboard itself (HTML page) ───────────────────────────────────────
print(f"\n4. DASHBOARD HTML:")
type_d, body = api_get("/api/status")
# Read the dashboard page directly
try:
    dash_resp = urllib.request.urlopen(f"{DASH}/", timeout=5)
    dash_html = dash_resp.read().decode()[:5000]
    print(f"  Dashboard loads: ✅ (HTTP {dash_resp.status})")
    # Check for JS errors in the page
    if "assets/index" in dash_html:
        # Get the JS file
        import re
        js_match = re.search(r'assets/index-[a-f0-9]+\.js', dash_html)
        if js_match:
            js_url = js_match.group(0)
            js_resp = urllib.request.urlopen(f"https://192.168.0.39:8080/{js_url}", timeout=5).read().decode()
            print(f"  Dashboard JS: {len(js_resp)} bytes")
            # Check if applyStatusData function exists
            if "applyStatusData" in js_resp:
                print(f"  applyStatusData() in JS: ✅")
            else:
                print(f"  applyStatusData() in JS: ❌ MISSING")
except Exception as e:
    print(f"  Dashboard: {e}")

# ─── 5. Check if Sir Green fixed the HTML return issue ───────────────────────────
print(f"\n5. SIR GREEN WORK VERIFICATION:")
new_html = [e for e in html_eps if e not in ["/api/status"]]  # /api/status returns JSON
if new_html:
    # Check if these were previously returning JSON in our last scan
    # (we scanned before and got: status, health, signals, paper_trades, alerts, positions as JSON
    # whale, orders, balance, history, crew_heartbeat, sandbox, fleet, vault_status, inbox,
    # tailscale, monitoring, containers, docker, captcha-verify, crowdsec, augur, augur/scan,
    # augur/augmented_signals, vault/health — were HTML)
    
    # Check which were HTML before vs now
    prev_json = ["status","health","signals","paper_trades","positions","alerts","tailscale",
                 "augur/scan/status","augur/augmented_signals"]
    prev_html = ["whale","orders","balance","history","crew_heartbeat","sandbox","fleet",
        "vault/status","inbox","monitoring","containers","docker","captcha-verify","crowdsec",
        "augur","vault/health","opsec/chinese_content","tools/classification"]
    
    new_json_eps = set(e.replace("/api/","") for e in json_eps)
    new_html_eps = set(e.replace("/api/","") for e in html_eps)
    
    fixed = [e for e in prev_html if e not in new_html_eps and e in new_json_eps]
    still_broken = [e for e in prev_html if e in new_html_eps]
    
    print(f"  Previously HTML endpoints now JSON (fixed): {len(fixed)}")
    for e in fixed: print(f"    ✅ FIXED: {e}")
    print(f"  Still HTML (unfixed): {len(still_broken)}")
    for e in still_broken: print(f"    ❌ {e}")
    
    # If no changes, Sir Green hasn't deployed fixes yet
    if len(fixed) == 0 and len(still_broken) == len(prev_html):
        print(f"  ⚠️ No changes detected — fixes not deployed yet")
    elif len(fixed) > 0:
        print(f"  ✅ Sir Green fixed {len(fixed)} endpoints!")
    # Update existing bug cards if endpoints were fixed
    if fixed:
        print(f"  📝 Consider closing bug cards for fixed endpoints")
else:
    print("  All HTML endpoints fixed!")

print(f"\n=== SCAN COMPLETE — {ts} ===")
