"""Check actual card counts on both boards + find the signal_augmentation card."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

# ─── Check VOID_Ops ───────────────────────────────────────────────────────────
print("=== VOID_Ops ===")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed&filter=all&limit=1000")
all_cards = json.loads(resp.read())
open_cards = [c for c in all_cards if not c.get("closed", True)]
closed_cards = [c for c in all_cards if c.get("closed", True)]

print(f"  Total cards: {len(all_cards)}")
print(f"  Open: {len(open_cards)}")
print(f"  Closed: {len(closed_cards)}")

# Show open cards
print(f"\n  Open cards:")
for c in sorted(open_cards, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"    [{','.join(labels)[:30]}] {c['name'][:55]}")

# ─── Check Torus_Ops ───────────────────────────────────────────────────────────
print(f"\n=== Torus_Ops ===")
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed&filter=all&limit=1000")
all_cards2 = json.loads(resp2.read())
open_cards2 = [c for c in all_cards2 if not c.get("closed", True)]
closed_cards2 = [c for c in all_cards2 if c.get("closed", True)]

print(f"  Total cards: {len(all_cards2)}")
print(f"  Open: {len(open_cards2)}")
print(f"  Closed: {len(closed_cards2)}")

print(f"\n  Open cards:")
for c in sorted(open_cards2, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"    [{','.join(labels)[:30]}] {c['name'][:55]}")

# ─── Search for signal_augmentation card ───────────────────────────────────────
print(f"\n=== Searching for signal_augmentation card ===")
for c in all_cards + all_cards2:
    name_l = c.get("name", "").lower()
    if "signal_augmentation" in name_l or "signal augmentation" in name_l:
        board = "VOID_Ops" if c in all_cards else "Torus_Ops"
        print(f"  FOUND on {board}: '{c['name']}'")
        print(f"    ID: {c['id']}")
        print(f"    Closed: {c.get('closed', False)}")
        print(f"    Labels: {[l.get('name','') for l in c.get('labels',[]) if isinstance(l,dict)]}")