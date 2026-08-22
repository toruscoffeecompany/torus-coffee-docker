"""
Check ALL Trello boards for business cards that were wrongly archived.
Look for tax, website, product cards.
"""
import json, urllib.request, os, time

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

boards = {
    "6a595669b8f8f99c93392f4f": "VOID_Ops",
    "6a70a3157d0db4214ac3f9a3": "Torus_Ops",
    "6a70a3152b3a6c2f9748f53b": "Business_Docs",
    "6a6e26f5cebe5c5a4c205726": "My_Trello_Board",
    "6a70a316f8849dbfd6848384": "Website_Rebuild",
}

# ─── Check closed cards for business terms ────────────────────────────────────
business_keywords = ["tax", "iowa", "website", "product", "catalog", "inventory", 
                      "sop", "automation", "filing", "quarterly", "monthly"]

print("=== Searching CLOSED cards for wrongly archived business cards ===\n")

for board_id, board_name in boards.items():
    print(f"--- {board_name} ---")
    try:
        # Get closed cards (archived)
        resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed,desc,dateLastActivity&filter=closed&limit=1000")
        cards = json.loads(resp.read())
        
        if len(cards) == 0:
            print("  No closed cards found")
            continue
        
        print(f"  Total closed: {len(cards)}")
        
        # Find business cards that might be wrongly archived
        wrongly_archived = []
        for c in cards[:100]:  # Check last 100
            name_l = c.get("name", "").lower()
            desc_l = c.get("desc", "").lower()
            if any(kw in name_l or kw in desc_l for kw in business_keywords):
                if "sir green" not in name_l and "sir azure" not in name_l and "[bug]" not in name_l and "[rule]" not in name_l:
                    wrongly_archived.append(c)
        
        if wrongly_archived:
            print(f"  ⚠️ POTENTIALLY WRONG ARCHIVED: {len(wrongly_archived)}")
            for c in wrongly_archived[:5]:
                print(f"    • {c['name'][:50]} (labels: {','.join([l.get('name','') for l in c.get('labels',[]) if isinstance(l,dict)])[:30]})")
        else:
            print(f"  ✅ No wrongly archived business cards")
            
    except Exception as e:
        print(f"  Error: {e}")
    print()