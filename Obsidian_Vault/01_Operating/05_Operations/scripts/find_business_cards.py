"""
Deep search for wrongly archived Torus Coffee business cards.
Search across ALL cards (open + closed) on ALL boards for business terms.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

boards = {
    "6a595669b8f8f99c93392f4f": "VOID_Ops",
    "6a70a3157d0db4214ac3f9a3": "Torus_Ops",
}

# Strong business card indicators — things that should NOT be archived
business_indicators = [
    "torus coffee", "torus_website", "iowa tax", "sales tax", "use tax",
    "withholding tax", "1065", "federal tax", "quarterly estimated",
    "product", "catalog", "inventory", "sop", "filing",
    "website", "next.js", "tailwind", "e-commerce", "storefront",
    "invoice", "payment", "customer", "vendor",
    "moon phase", "coffee", "freeze-dried", "product photo",
]

print("=== Deep search for wrongly archived BUSINESS cards ===\n")

for board_id, board_name in boards.items():
    print(f"--- {board_name} ---")
    # Search closed cards (archived) - need filter=closed for all
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc,dateLastActivity&filter=closed&limit=1000")
    cards = json.loads(resp.read())
    
    business_archived = []
    for c in cards:
        name_l = c.get("name", "").lower()
        desc_l = c.get("desc", "").lower()
        
        # Skip VOID ops cards, rules, bugs — those SHOULD be archived
        if any(x in name_l for x in ["[rule]", "[bug]", "void", "pirate", "squidstation", 
                                      "stealthattack", "g12", "crew", "fleet", "ids",
                                      "suricata", "zeek", "crowdsec", "docker"]):
            continue
        
        # Check for business indicators
        if any(kw in name_l or kw in desc_l for kw in business_indicators):
            business_archived.append(c)
    
    if business_archived:
        print(f"  ⚠️ {len(business_archived)} wrongly archived BUSINESS cards:")
        for c in business_archived:
            labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
            print(f"    • {c['name'][:60]}")
            print(f"      labels: {','.join(labels)[:40]}")
            print(f"      closed: {c.get('closed')}")
            print(f"      desc: {c.get('desc','')[:80]}...")
            print(f"      id: {c['id']}")
            print()
    else:
        print("  ✅ No wrongly archived business cards")
    print()

# ─── Also check: what business cards are still OPEN? ───────────────────────────
print("=== Currently OPEN business cards ===\n")
for board_id, board_name in boards.items():
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open&limit=1000")
    cards = json.loads(resp.read())
    open_business = [c for c in cards if not c.get("closed") and not any(x in c.get("name","").lower() for x in ["[bug]","void","pirate","fleet","ids"])]
    if open_business:
        print(f"  {board_name}: {len(open_business)} open")
        for c in open_business:
            labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
            print(f"    • [{','.join(labels)[:30]}] {c['name'][:50]}")
    print()