"""Final board state check."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

for board_id, name in [("6a595669b8f8f99c93392f4f", "VOID_Ops"), ("6a70a3157d0db4214ac3f9a3", "Torus_Ops")]:
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open&limit=1000")
    cards = json.loads(resp.read())
    open_cards = [c for c in cards if not c.get("closed")]
    print(f"\n{name}: {len(open_cards)} open")
    for c in sorted(open_cards, key=lambda x: x["name"]):
        labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
        lbl_str = ",".join(labels)
        print(f"  [{lbl_str[:25]}] {c['name'][:55]}")