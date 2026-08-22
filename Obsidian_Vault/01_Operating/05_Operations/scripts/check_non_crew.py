import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())
open_cards = [c for c in cards if not c.get("closed", True)]

non_crew = []
for c in open_cards:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    labels_l = [l.lower() for l in labels]
    name_l = c["name"].lower()
    desc = c.get("desc","").lower()
    combined = name_l + " " + desc

    if "sir-green" in labels_l or "sir-azure" in labels_l:
        continue
    if any(k in combined for k in ["sir green", "sir_azure", "sir-azure"]):
        continue

    non_crew.append(c)

print(f"VOID_Ops non-crew cards: {len(non_crew)}")
for c in sorted(non_crew, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ", ".join(labels)
    print(f"  [{label_str}] {c['name'][:60]}")