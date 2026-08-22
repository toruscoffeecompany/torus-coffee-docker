"""
VOID_Ops sweep — find ALL remaining actionable cards, categorize for Miss Pink/Sir Green work.
Create task list + OODA loop until all verified done.
"""
import json, urllib.request, os, subprocess
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc,shortUrl&filter=open")
cards = json.loads(resp.read())
open_cards = [c for c in cards if not c.get("closed", True)]

print(f"VOID_Ops open: {len(open_cards)}")

# Categorize ALL open cards
categories = {
    "MISS_PINK_WORK": [],
    "SIR_GREEN_WORK": [],
    "SIR_AZURE_WORK": [],
    "CAPTAIN_BLOCKED": [],
    "FUTURE": [],
    "LORE": [],
    "CREW_SYNC": [],
    "OTHER": [],
}

for c in open_cards:
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    labels = [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]
    labels_l = [l.lower() for l in labels]

    # Skip Sir Green/Azure/Captain
    if "sir-green" in labels_l or "sir-azure" in labels_l:
        if "sir-green" in labels_l:
            categories["SIR_GREEN_WORK"].append(c)
        else:
            categories["SIR_AZURE_WORK"].append(c)
        continue
    if "captain" in labels_l or "[captain]" in name_l:
        categories["CAPTAIN_BLOCKED"].append(c)
        continue
    if "future" in labels_l or "future" in name_l:
        categories["FUTURE"].append(c)
        continue
    if "lore" in labels_l or "lore" in name_l:
        categories["LORE"].append(c)
        continue
    if any(k in combined for k in ["crew sync", "crew_coordination", "fleet merge"]):
        categories["CREW_SYNC"].append(c)
        continue

    # Check if miss-pink can work it
    if "miss-pink" in labels_l or "[miss_pink]" in name_l or "miss pink" in name_l:
        categories["MISS_PINK_WORK"].append(c)
    elif any(k in combined for k in ["sir green", "sir_azure", "sir-azure"]):
        categories["SIR_GREEN_WORK"].append(c)
    else:
        categories["OTHER"].append(c)

for cat, items in categories.items():
    print(f"\n{cat} ({len(items)}):")
    for c in sorted(items, key=lambda x: x["name"])[:15]:
        print(f"  • {c['name'][:60]}")
    if len(items) > 15:
        print(f"  ... ({len(items) - 15} more)")