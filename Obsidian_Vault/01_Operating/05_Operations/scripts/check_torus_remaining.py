import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())
open_cards = [c for c in cards if not c.get("closed", True)]

print(f"Torus_Ops open: {len(open_cards)}")
for c in sorted(open_cards, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ", ".join(labels)
    print(f"  [{label_str}] {c['name'][:60]}")