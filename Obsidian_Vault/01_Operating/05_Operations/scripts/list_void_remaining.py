"""Check remaining VOID_Ops cards."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed&filter=open&limit=1000")
cards = json.loads(resp.read())
open_cards = [c for c in cards if not c.get("closed", True)]
print(f"VOID_Ops: {len(open_cards)} open")
for c in sorted(open_cards, key=lambda x: x["name"]):
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ", ".join(labels)
    print(f"  [{label_str[:30]}] {c['name'][:55]}")