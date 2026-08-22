import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())
open_cards = [c for c in cards if not c.get("closed", True)]

# Categorize
sg = sa = other = inbox = 0
for c in open_cards:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    labels_l = [l.lower() for l in labels]
    name_l = c["name"].lower()
    desc = c.get("desc","").lower()
    combined = name_l + " " + desc

    if "sir-green" in labels_l: sg += 1
    elif "sir-azure" in labels_l: sa += 1
    elif any(k in combined for k in ["sir green", "sir_azure", "sir-azure"]): sg += 1
    elif "inbox" in name_l or "[inbox]" in name_l or "📨" in c.get("name",""):
        inbox += 1
    else:
        other += 1

print(f"VOID_Ops open: {len(open_cards)}")
print(f"  Sir Green: {sg}")
print(f"  Sir Azure: {sa}")
print(f"  Inbox: {inbox}")
print(f"  Other: {other}")