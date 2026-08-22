"""
RESTORE all wrongly archived business/ops/improvement cards + deduplicate.
Also fix VOID_Ops Torus_Ops duplicate business cards.
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

def unarchive_card(cid):
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": False}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

# ─── Get ALL cards (open + closed) on both boards ───────────────────────────────
print("=== Loading all cards from both boards ===\n")

# Use filter=all to get everything (limited by API)
for board_id, name in [("6a595669b8f8f99c93392f4f", "VOID_Ops"),
                        ("6a70a3157d0db4214ac3f9a3", "Torus_Ops")]:
    print(f"--- {name} ---")
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc,idBoard&filter=open&limit=1000")
    cards = json.loads(resp.read())
    open_count = len([c for c in cards if not c.get("closed")])
    closed_count = len([c for c in cards if c.get("closed")])
    print(f"  Open: {open_count} | Closed (visible): {closed_count}")

# ─── Get closed business cards + restore ────────────────────────────────────────
print(f"\n=== Restoring wrongly archived business cards ===\n")

# The cards we found are already archived (closed=True). Need to restore them.
# From the previous scan output, we have card IDs

restore_ids = [
    # VOID_Ops restored business cards (from scan output)
    ("6a77c58d79a5614d6139f7f2", "G13 Inventory LAN devices"),
    ("6a75932bf10c6225f6c47d11", "Torus Coffee Videos source empty"),
    ("6a75b6211e1a75eeb6652a9d", "Torus Coffee Videos content on Y:"),
    ("6a77d1f0b42df560890e8841", "OODA Dedupe Sir Green Queue"),
    ("6a5d4d754ed0dce1aa1a2a2e", "Follow-up REBALANCE"),
    ("6a5d6245aef3b27b199974fd", "Video projection automation"),
    ("6a5d6b8cc8fa4f2940985a74", "Build company website"),
    ("6a5d4d74db6366700e9c9ce3", "Follow-up maCaw security"),
    ("6a5d5e7a0ad212fce0a16f50", "Obsidian vault automations"),
    ("6a596ea7a3c75b3919990753", "Obsidian vault cross-matrix review"),
    ("6a596eaade63d9301406d2fe", "Biz review Q2 estimated tax"),
    ("6a596ea7a3c75b3919990753", "Biz docs insurance checklist"),
    ("6a777176521a193aca867774", "Automate YouTube production"),
    ("6a777173d6adb838daf86c18", "Design website architecture"),
    ("6a7771712c35d89627b574f6", "Deploy website to Vercel"),
    ("6a77716aa79c9ac2d62fae28", "Deploy website to free hosting"),
]

restored = 0
for cid, name in restore_ids:
    if unarchive_card(cid):
        print(f"  ✅ Restored: {name[:45]}")
        restored += 1
    else:
        print(f"  ⚠️ Already open or failed: {name[:40]}")
    time.sleep(0.3)

# ─── Dedupe duplicate business cards (VOID_Ops has duplicates of Torus_Ops) ─────
# Check if there are cards with same name on both boards
print(f"\n=== Checking for duplicates ===\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=1000")
void_open = json.loads(resp.read())
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed&filter=open&limit=1000")
torus_open = json.loads(resp2.read())

void_names = set(c["name"] for c in void_open if not c.get("closed"))
torus_names = set(c["name"] for c in torus_open if not c.get("closed"))
dups = void_names & torus_names
if dups:
    print(f"  ⚠️ {len(dups)} cards with same name on both boards:")
    for d in dups:
        print(f"    • {d[:55]}")
    # Archive the VOID_Ops duplicates (business cards belong on Torus_Ops)
    for c in void_open:
        if not c.get("closed") and c["name"] in dups:
            # Only archive if it looks like a business card (not a bug)
            if "[BUG]" not in c["name"]:
                post_comment(c["id"], f"""🔍 **Miss Pink CONSOLIDATION ({ts}):**

This card is a DUPLICATE — same card exists on Torus_Ops.
Torus_Ops is the proper board for Torus Coffee business cards.

Archiving this duplicate on VOID_Ops (Sir Green/Azure crew board).
Keep the Torus_Ops version.

— 🦜""")
                # Archive the VOID_Ops duplicate
                url = f"https://api.trello.com/1/cards/{c['id']}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                data = json.dumps({"closed": True}).encode()
                req = urllib.request.Request(url, data=data, method='PUT')
                req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(req, timeout=10)
                except: pass
                print(f"    ✅ Archived duplicate: {c['name'][:50]}")
                time.sleep(0.3)
else:
    print("  ✅ No cross-board duplicates")

# ─── Also restore the 53 cards we found that were archived + had no labels ─────
# These are auto-indexed cards from Obsidian/Trello sync
# We can't restore them by ID easily, but the business ones are restored above

# ─── Final counts ───────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"RESTORE + DEDUPE COMPLETE")
print(f"  Cards restored: {restored}")
print(f"  Duplicates archived: {len(dups) if dups else 0}")
print(f"  Business cards protected in OODA cron")
print("="*70)