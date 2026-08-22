#!/usr/bin/env python3
"""
Check TORUS_OPS board for next tasks to work on.
Board: 6a70a3157d0db4214ac3f9a3
Compare with VOID_OPS Done cards to decide priority.
"""
import json, time, urllib.request, urllib.parse

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS_OPS = "6a70a3157d0db4214ac3f9a3"
VOID_OPS = "6a595669b8f8f99c93392f4f"

def trello_get(path, params=None):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    if params:
        url += "&" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8")
    except:
        return None

time.sleep(5)

# ─── Get TORUS_OPS lists ─────────────────────────────────────────────────
print("=== TORUS_OPS BOARD ===\n")
lists_out = trello_get(f"/boards/{TORUS_OPS}/lists", {"fields": "id,name"})
lists = json.loads(lists_out)
list_map = {l["id"]: l["name"] for l in lists}

# Get cards per list
print("TORUS_OPS board — cards by list:")
torus_cards = {}
for l in lists:
    time.sleep(3)
    cards_out = trello_get(f"/lists/{l['id']}/cards", {"fields": "id,name,labels"})
    if cards_out:
        cards = json.loads(cards_out)
        torus_cards[l["name"]] = cards
        # Show P0/P1 cards only
        important = [c for c in cards if any(label.get("name","").startswith(("P0","P1","Top")) for label in c.get("labels",[]))]
        if important:
            print(f"\n  {l['name']} ({len(cards)} total, {len(important)} P0/P1):")
            for c in important[:10]:
                labels = [lbl.get("name","") for lbl in c.get("labels",[])]
                print(f"    • {c['name'][:70]}")
                print(f"      Labels: {', '.join(labels)}")

# ─── VOID_OPS Done cards count ──────────────────────────────────────────
print(f"\n\n=== VOID_OPS BOARD ===\n")
time.sleep(5)
vlists_out = trello_get(f"/boards/{VOID_OPS}/lists", {"fields": "id,name"})
vlists = json.loads(vlists_out)
vlist_map = {l["id"]: l["name"] for l in vlists}

total_done = 0
for vl in vlists:
    if "done" in vl["name"].lower() or "completed" in vl["name"].lower():
        time.sleep(3)
        cards_out = trello_get(f"/lists/{vl['id']}/cards", {"fields": "id,name"})
        if cards_out:
            cards = json.loads(cards_out)
            print(f"  {vl['name']}: {len(cards)} cards")
            total_done += len(cards)
            # Show recent ones
            for c in cards[:5]:
                print(f"    • {c['name'][:70]}")

print(f"\n  Total VOID_OPS Done cards: ~{total_done}")

# ─── Summary + recommendation ──────────────────────────────────────────
print(f"\n{'='*60}")
print("ANALYSIS")
print(f"{'='*60}")

# Get TORUS_OPS open card count
torus_open = sum(len(cards) for name, cards in torus_cards.items()
    if "done" not in name.lower() and "completed" not in name.lower())
print(f"\nTORUS_OPS open cards: ~{torus_open}")
print(f"VOID_OPS done cards: ~{total_done}")

print(f"\n{'='*60}")
print("NEXT STEPS RECOMMENDATION")
print(f"{'='*60}")
print("""
Given the user's priorities:
  A) Website rebuild (highest ROI)  
  B) Free monitoring setup
  C) OODA bug hunting

RECOMMENDATION:
1. Start TORUS_OPS Done card verification (smaller board, ~35 cards)
   — This directly serves Torus Coffee Company
2. Check for website-related cards on TORUS_OPS
3. Continue VOID_OPS Done card verification in parallel

Shall I proceed with TORUS_OPS Done card verification first,
or continue VOID_OPS Done cards (batch 2+)?
""")

os.remove(__file__)
