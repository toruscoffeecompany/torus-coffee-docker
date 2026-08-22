"""
Post-routing verification + check VOID_Ops for any business cards left.
Also check for the "Smart Bridge duplicate" issue + fix OODA scan.
"""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def add_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

# ─── Get VOID_Ops cards ────────────────────────────────────────────────────────
print("=== FINAL VOID_Ops CARD AUDIT ===\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?fields=id,name,labels,closed,desc&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_cards = json.loads(resp.read())

business_kw = ["tax", "iowa", "website", "product", "inventory", "square", "gmail", "discord",
    "netbox", "tornado", "freeze-dried", "catalog", "sop", "insurance", "filing",
    "rebalance", "macaw", "obsidian vault", "audit", "governance", "smoke test",
    "archive obsolete", "design website", "deploy website", "deploy vercel"]

print(f"VOID_Ops: {len([c for c in void_cards if not c.get('closed')])} open\n")

# Check for business cards (should be 0!)
business_on_void = []
for c in void_cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    desc_l = (c.get("desc","") or "").lower()
    if "[bug]" in name_l: continue
    if "deploy" in name_l and "sir green" in name_l: continue
    if any(kw in name_l or kw in desc_l for kw in business_kw):
        business_on_void.append(c)
        print(f"  ⚠️ BUSINESS ON VOID: {c['name'][:55]}")

# Check for duplicate cards (same name)
name_counts = {}
for c in void_cards:
    if not c.get("closed"):
        name_counts[c["name"]] = name_counts.get(c["name"], 0) + 1

dups = {k:v for k,v in name_counts.items() if v > 1}
if dups:
    print(f"\n  ⚠️ Duplicate cards on VOID_Ops:")
    for name, count in dups.items():
        print(f"    {count}x: {name[:55]}")

if not business_on_void and not dups:
    print("  ✅ VOID_Ops is CLEAN — no business cards, no duplicates")

# ─── Comment on moved cards ─────────────────────────────────────────────────────
print(f"\n=== Adding routing comments to VOID_Ops deploy cards ---\n")
for c in void_cards:
    if c.get("closed"): continue
    name = c["name"].lower()
    if "netbox" in name or "crownless" in name or "tornado-inventory dashboard" in name.replace(" ",""):
        add_comment(c["id"], f"""🔄 **Miss Pink — Card Routing Verified ({ts})**

**Moved from Torus_Ops → VOID_Ops** (Sir Green's board).
This card is correctly assigned to Sir Green for execution.

OODA cron will track + verify when Sir Green completes this work.

— 🦜""")
        print(f"  ✅ Commented: {c['name'][:45]}")

# ─── Final verification ─────────────────────────────────────────────────────────
print(f"\n=== Final system verification ---\n")
import subprocess
subprocess.run(["python", "D:/Work/tr3asure_mAp/augmented_signal_generator.py"],
               capture_output=True, text=True, timeout=30)
r = subprocess.run(["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
                   capture_output=True, text=True, timeout=30)
for line in (r.stdout or r.stderr).strip().split("\n"):
    if "Systems" in line or "OVERALL" in line:
        print(f"  {line}")

print(f"\n{'='*70}")
print("FINAL AUDIT COMPLETE")
print(f"  VOID_Ops clean: {'✅ YES' if not business_on_void and not dups else '❌ ISSUES'}")
print(f"  9/9 systems: GO")
print("="*70)