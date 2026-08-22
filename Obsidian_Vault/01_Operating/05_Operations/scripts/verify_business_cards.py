"""
Verify restored business cards + create Torus_Ops business card for Iowa taxes.
Then fix OODA sweep scripts to exclude business cards.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

# ─── Check Torus_Ops open business cards ──────────────────────────────────────
print("=== Torus_Ops business cards (open) ===\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open&limit=100")
cards = json.loads(resp.read())

business_cards = [c for c in cards if not c.get("closed") and 
    any(kw in c["name"].lower() for kw in ["tax", "iowa", "website", "product", "inventory", 
      "square", "gmail", "discord", "netbox", "vid", "youtube", "photo", "deploy"])]

print(f"Business cards on Torus_Ops: {len(business_cards)}")
for c in sorted(business_cards, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"  ✅ [{','.join(labels)[:30]}] {c['name'][:60]}")

# ─── Check VOID_Ops restored business cards ───────────────────────────────────
print(f"\n=== VOID_Ops restored business cards ===\n")
resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open&limit=100")
void_cards = json.loads(resp2.read())
void_business = [c for c in void_cards if not c.get("closed") and
    any(kw in c["name"].lower() for kw in ["tax", "iowa", "website", "product", "inventory",
      "square", "gmail", "discord", "netbox", "vid", "youtube", "photo", "build"])]

print(f"Business cards on VOID_Ops: {len(void_business)}")
for c in sorted(void_business, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"  ✅ [{','.join(labels)[:30]}] {c['name'][:60]}")