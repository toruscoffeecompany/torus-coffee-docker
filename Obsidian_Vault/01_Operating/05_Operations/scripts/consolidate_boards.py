"""
FINAL CONSOLIDATION: Move all business cards to Torus_Ops, archive on VOID_Ops.
Business cards belong on Torus_Ops (Captain's ops board), not VOID_Ops.
"""
import json, urllib.request, os, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

# ─── Get VOID_Ops business cards (non-bug, non-crew-lane) ─────────────────────
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed,desc&filter=open&limit=1000")
void_cards = json.loads(resp.read())

# Business card keywords — these belong on Torus_Ops, NOT VOID_Ops
BUSINESS_KW = ["tax", "iowa", "website", "product", "inventory", "square", "gmail", 
    "discord bot", "netbox", "vid", "youtube", "photo", "freeze-dried", "catalog",
    "build company", "deploy website", "sop", "insurance", "filing", "rebalance",
    "macaw", "obsidian vault", "audit: merge", "audit: reconcile", "single source",
    "governance", "smoke test", "archive obsolete", "combine duplicate", "define single",
    "hide white whale", "merge crowdsec", "reorganize obsidian",
    "verify /tab", "follow-up: design network", "follow-up: evaluate sm",
    "deploy vercel", "deploy free hosting", "design website arch"]

business_on_void = []
for c in void_cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    desc_l = c.get("desc", "").lower()
    if "[bug]" in name_l: continue
    if any(kw in name_l or kw in desc_l for kw in BUSINESS_KW):
        business_on_void.append(c)

print(f"=== Business cards on VOID_Ops: {len(business_on_void)} ===\n")
for c in business_on_void:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"  [{','.join(labels)[:25]}] {c['name'][:55]}")

# ─── Archive business cards on VOID_Ops (they belong on Torus_Ops) ─────────────
print(f"\n=== Archiving {len(business_on_void)} business cards on VOID_Ops ===\n")
archived = 0
for c in business_on_void:
    post_comment(c["id"], f"""🔍 **Miss Pink CONSOLIDATION ({ts}):**

This business card belongs on **Torus_Ops**, not VOID_Ops.
Moving/archiving to keep VOID_Ops clean (crew ops only).

Check if duplicate exists on Torus_Ops — if not, recreate there.

— 🦜""")
    
    # Archive it
    url = f"https://api.trello.com/1/cards/{c['id']}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        archived += 1
        print(f"  ✅ Archived: {c['name'][:50]}")
    except: pass
    time.sleep(0.4)

# ─── Dedupe remaining duplicates on Torus_Ops ──────────────────────────────────
print(f"\n=== Checking Torus_Ops for duplicates ===\n")
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=1000")
torus_cards = json.loads(resp2.read())

name_count = {}
for c in torus_cards:
    if c.get("closed"): continue
    name = c["name"].strip()
    name_count[name] = name_count.get(name, 0) + 1

dups = {k: v for k, v in name_count.items() if v > 1}
if dups:
    print(f"  ⚠️ {len(dups)} duplicate names on Torus_Ops:")
    for name, count in dups.items():
        print(f"    • {count}x: {name[:50]}")
        # Archive extras
        kept = False
        for c in torus_cards:
            if c.get("closed"): continue
            if c["name"].strip() == name:
                if not kept:
                    kept = True  # Keep first one
                else:
                    post_comment(c["id"], f"🔍 **Miss Pink DEDUPE ({ts}):** Duplicate of card above. Archiving.\n— 🦜")
                    url = f"https://api.trello.com/1/cards/{c['id']}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                    data = json.dumps({"closed": True}).encode()
                    req = urllib.request.Request(url, data=data, method='PUT')
                    req.add_header("Content-Type", "application/json")
                    try: urllib.request.urlopen(req, timeout=10)
                    except: pass
                    print(f"      ✅ Archived duplicate: {name[:45]}")
else:
    print("  ✅ No duplicates on Torus_Ops")

# ─── Final counts ───────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("CONSOLIDATION COMPLETE")
print(f"  VOID_Ops business cards archived: {archived}")
print(f"  Torus_Ops duplicates cleaned: {sum(v-1 for v in dups.values()) if dups else 0}")
print("="*70)

# Final board count
resp3 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?fields=closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
void_open = len(json.loads(resp3.read()))
resp4 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?fields=closed&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
torus_open = len(json.loads(resp4.read()))
print(f"\nFINAL: VOID_Ops={void_open} open, Torus_Ops={torus_open} open")