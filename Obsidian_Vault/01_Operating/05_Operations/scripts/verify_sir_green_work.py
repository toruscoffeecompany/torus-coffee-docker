"""
Miss Pink — Read ALL Trello cards on BOTH boards + verify Sir Green's work.
+ Continue the continuous dashboard bug hunt.
"""
import json, urllib.request, subprocess, time, os
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS = "6a70a3157d0db4214ac3f9a3"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_board_cards(board_id, batch_size=50):
    """Fetch all cards from a board in small batches (Trello 401 on long URLs)."""
    all_cards = []
    page = 0
    while True:
        url = f"https://api.trello.com/1/boards/{board_id}/cards?fields=id,name,labels,desc,closed,idMembers,due,dateLastActivity&limit={batch_size}&key={TRELLO_KEY}&token={TRELLO_TOKEN}"
        resp = urllib.request.urlopen(url)
        batch = json.loads(resp.read())
        if not batch or len(batch) < batch_size:
            all_cards.extend(batch)
            break
        all_cards.extend(batch)
        page += 1
        if page > 20: break  # safety
    return all_cards

def get_board_cards_closed(board_id):
    """Get recently closed cards."""
    url = f"https://api.trello.com/1/boards/{board_id}/cards?fields=id,name,labels,closed,dateLastActivity&filter=closed&limit=50&key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    try:
        resp = urllib.request.urlopen(url)
        return json.loads(resp.read())
    except:
        return []

def get_labels(card):
    return [l.get("name","") for l in card.get("labels",[]) if isinstance(l,dict)]

def get_members(card):
    return card.get("idMembers", [])

# ─── Read ALL Torus_Ops cards ────────────────────────────────────────────────────
print("="*70)
print("TORUS_OPS BOARD — READING ALL CARDS")
print("="*70)

torus_cards = get_board_cards(TORUS)
torus_open = [c for c in torus_cards if not c.get("closed")]
print(f"\nTorus_Ops: {len(torus_open)} open cards")

torus_sg = []
torus_mp = []
torus_sa = []
torus_cross = []
torus_unlabeled = []

for c in torus_open:
    labels = get_labels(c)
    labels_lower = [l.lower() for l in labels]
    name = c["name"][:55]
    
    sg = "sir-green" in labels_lower
    mp = "miss-pink" in labels_lower
    sa = "sir-azure" in labels_lower
    
    if sg and not mp and not sa:
        torus_sg.append(c)
    elif mp and not sg and not sa:
        torus_mp.append(c)
    elif sa and not mp and not sg:
        torus_sa.append(c)
    elif sg and mp:
        torus_cross.append(c)
    else:
        torus_unlabeled.append(c)

print(f"\n  Sir Green (only): {len(torus_sg)} — must be 0!")
if torus_sg:
    for c in torus_sg:
        print(f"  ⚠️  SG-ONLY: {c['name'][:50]} | labels={get_labels(c)}")

print(f"  Miss Pink (only): {len(torus_mp)}")
for c in torus_mp[:20]:
    print(f"    MP: {c['name'][:50]} | labels={get_labels(c)}")

print(f"  Sir Azure (only): {len(torus_sa)}")
for c in torus_sa[:10]:
    print(f"    SA: {c['name'][:50]} | labels={get_labels(c)}")

print(f"  Cross-crew (SG+MP): {len(torus_cross)}")
for c in torus_cross:
    print(f"    X: {c['name'][:50]} | labels={get_labels(c)}")

print(f"  Unlabeled: {len(torus_unlabeled)}")
for c in torus_unlabeled:
    print(f"    ?: {c['name'][:50]} | labels={get_labels(c)}")

# ─── Read ALL VOID_Ops cards ─────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("VOID_OPS BOARD — READING ALL CARDS")
print("="*70)

void_cards = get_board_cards(VOID)
void_open = [c for c in void_cards if not c.get("closed")]
print(f"\nVOID_Ops: {len(void_open)} open cards")

void_bugs = [c for c in void_open if "[BUG]" in c["name"].upper()]
void_done = [c for c in void_open if "DONE" in c["name"].upper() or "✅" in c["name"][:5]]
void_deploy = [c for c in void_open if "[BUG]" not in c["name"].upper()]

print(f"  Bug cards: {len(void_bugs)}")
print(f"  Deploy/work cards: {len(void_deploy)}")
for c in void_deploy:
    print(f"    DEPLOY: {c['name'][:50]} | labels={get_labels(c)}")

# Check recently closed (archived) — Sir Green fixed some
void_closed = get_board_cards_closed(VOID)
print(f"\n  Recently closed (archived): {len(void_closed)}")
for c in void_closed[:5]:
    print(f"    CLOSED: {c['name'][:50]} | last: {c.get('dateLastActivity','?')[:19]}")

# Check if Sir Green fixed anything — look for closed bug cards
void_closed_bugs = [c for c in void_closed if "[BUG]" in c["name"].upper()]
print(f"  Closed BUG cards: {len(void_closed_bugs)}")
for c in void_closed_bugs[:10]:
    print(f"    FIXED: {c['name'][:55]} | closed: {c.get('dateLastActivity','?')[:19]}")

# ─── Verify Sir Green's fixes ───────────────────────────────────────────────────
print(f"\n{'='*70}")
print("SIR GREEN — FIX VERIFICATION")
print("="*70)

try:
    resp = subprocess.run(["curl","-s","--connect-timeout","5","--max-time","10",
        "http://100.83.247.14:5000/api/status"], capture_output=True, text=True, timeout=10)
    tm = json.loads(resp.stdout)
    print(f"\nTM API Status:")
    print(f"  kill_trading: {tm.get('kill_trading')} {'✅ FIXED (False)' if tm.get('kill_trading')==False else '❌ Still True (bug)'}")
    print(f"  paper_mode: {tm.get('paper_mode')}")
    print(f"  signals: {len(tm.get('signals', []))}")
    print(f"  sim_lifetime_count: {tm.get('sim_lifetime_count')}")
    print(f"  latest_augur_run: {tm.get('latest_augur_run')}")
    print(f"  status: {tm.get('status')}")
except Exception as e:
    print(f"  TM API: UNREACHABLE — {e}")
    tm = {"error": str(e)}

# ─── Dashboard re-scan ───────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("DASHBOARD — RE-SCAN (find NEW bugs)")
print("="*70)

api_body = subprocess.run(["curl","-s","--connect-timeout","5",
    "http://100.83.247.14:5000/api/status"], capture_output=True, text=True, timeout=10).stdout

try:
    api_data = json.loads(api_body)
    expected = ["ships","ship_details","latency","services","containers","network",
        "vault","opsec","comms","cipher","tools","internal_services","tailscale_status"]
    missing = [k for k in expected if k not in api_data]
    present = [k for k in expected if k in api_data]
    print(f"\n/api/status sections:")
    print(f"  Present: {len(present)} — {present}")
    print(f"  Missing: {len(missing)} — {missing}")
    if missing:
        print(f"  ❌ Master bug STILL present: {len(missing)} sections missing")
except:
    print("  ❌ API returns non-JSON — broken")

# Quick endpoint probe
endpoints = ["/api/status","/api/signals","/api/whale","/api/paper_trades",
    "/api/crew_heartbeat","/api/sandbox","/api/alerts","/api/fleet",
    "/api/orders","/api/balance","/api/positions"]
for ep in endpoints:
    r = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","--connect-timeout","3",
        f"http://100.83.247.14:5000{ep}"], capture_output=True, text=True, timeout=5)
    status_code = r.stdout
    json_check = ""
    if status_code == "200":
        r2 = subprocess.run(["curl","-s","--connect-timeout","3",f"http://100.83.247.14:5000{ep}"],
            capture_output=True, text=True, timeout=5)
        ctype = r2.stdout[:200]
        if "<!DOCTYPE" in ctype: json_check = " (HTML!)"
        else: json_check = " (JSON)"
    print(f"  {ep}: HTTP {status_code}{json_check}")

# ─── Save results ───────────────────────────────────────────────────────────────
result = {
    "timestamp": ts,
    "torus_ops": {"open": len(torus_open), "sg_only": len(torus_sg), 
        "mp_only": len(torus_mp), "sa_only": len(torus_sa), "cross": len(torus_cross), "unlabeled": len(torus_unlabeled)},
    "void_ops": {"open": len(void_open), "bugs": len(void_bugs), "deploy": len(void_deploy),
        "closed": len(void_closed), "closed_bugs": len(void_closed_bugs)},
    "tm_api": tm,
    "api_missing_sections": missing if "missing" in dir() else [],
}
with open("D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/verify_sir_green_work.json", "w") as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n{'='*70}")
print("SCAN COMPLETE — results saved to verify_sir_green_work.json")
print("="*70)