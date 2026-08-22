"""Check remaining Torus_Ops Sir Green cards."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())
for c in cards:
    if c.get("closed"): continue
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    if any("sir-green" in l.lower() for l in labels) or "sir green" in c["name"].lower():
        lbl_str = ",".join(labels)
        print(f"  [{lbl_str[:30]}] {c['name'][:55]}")
        print(f"    desc: {c.get('desc','')[:100]}")