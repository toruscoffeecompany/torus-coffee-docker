"""
FINAL TASKLIST — All Trello cards from Torus Ops board, categorized by owner.
Miss Pink working all cards assigned to miss-pink that are NOT Sir Green's lane.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"  # Torus_Ops board

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

# Get all card data in parallel
lists = trello_get(f"boards/{BOARD_ID}/lists")
list_map = {l["id"]: l["name"] for l in lists}
cards = trello_get(f"boards/{BOARD_ID}/cards")

# Categorize
miss_pink_cards = []
sir_green_cards = []
sir_azure_cards = []
p0_cards = []
p1_cards = []
augur_related = []

for c in cards:
    name = c.get("name", "")
    labels = [l.get("name", "") for l in c.get("labels", [])]
    list_name = list_map.get(c.get("idList", ""), "?")
    is_done = "Done" in list_name or "Done" in str(labels)

    card = {
        "name": name,
        "list": list_name,
        "labels": labels,
        "done": is_done,
        "short_link": c.get("shortLink", ""),
        "id": c["id"],
    }

    if "miss-pink" in labels:
        miss_pink_cards.append(card)
    if "sir-green" in labels:
        sir_green_cards.append(card)
    if "sir-azure" in labels:
        sir_azure_cards.append(card)
    if "P0" in labels or "P0" in list_name:
        p0_cards.append(card)
    if "P1" in labels or "P1" in list_name:
        p1_cards.append(card)
    if any(kw in name.lower() for kw in ["augur", "signal", "regime", "genome", "price_history", "scan", "kill", "paper trade", "profitability", "data", "yfinance"]):
        augur_related.append(card)

print("=" * 80)
print("📊 TORUS OPS — COMPLETE CARD AUDIT")
print("=" * 80)
print(f"Total cards: {len(cards)}")
print(f"Miss Pink (miss-pink label): {len(miss_pink_cards)}")
print(f"Sir Green (sir-green label): {len(sir_green_cards)}")
print(f"Sir Azure (sir-azure label): {len(sir_azure_cards)}")
print(f"P0 priority: {len(p0_cards)}")
print(f"P1 priority: {len(p1_cards)}")
print(f"Augur-related: {len(augur_related)}")

print(f"\n{'='*80}")
print("🎯 MISS PINK CARDS (WORK THESE)")
print(f"{'='*80}")
for c in sorted(miss_pink_cards, key=lambda x: (0 if "P0" in x["labels"] else 1 if "P1" in x["labels"] else 2, x["name"])):
    status = "✅ DONE" if c["done"] else "🚧 IN PROGRESS"
    priority = [l for l in c["labels"] if l.startswith("P")]
    print(f"  [{status}] {priority} {c['name'][:60]}")
    print(f"         List: {c['list']} | Labels: {c['labels']}")

print(f"\n{'='*80}")
print("🐙 SIR GREEN CARDS (SKIP — Sir Green's lane)")
print(f"{'='*80}")
for c in sir_green_cards[:5]:
    status = "✅ DONE" if c["done"] else "🚧"
    print(f"  [{status}] {c['name'][:60]}")
    print(f"         Labels: {c['labels']}")

print(f"\n{'='*80}")
print("🔑 AUGUR-RELATED CARDS (all owners)")
print(f"{'='*80}")
for c in sorted(augur_related, key=lambda x: (0 if "P0" in x["labels"] else 1 if "P1" in x["labels"] else 2, x["name"])):
    status = "✅ DONE" if c["done"] else "🚧"
    owner = "PINK" if "miss-pink" in c["labels"] else "GREEN" if "sir-green" in c["labels"] else "AZURE" if "sir-azure" in c["labels"] else "UN"
    priority = [l for l in c["labels"] if l.startswith("P")]
    print(f"  [{status}] [{owner}] {priority} {c['name'][:55]}")