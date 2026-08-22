"""Check current board state."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open")
void = json.loads(resp.read())
print(f"VOID_Ops: {len(void)} open")
for c in void:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"  [{','.join(labels)[:25]}] {c['name'][:50]}")

resp2 = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,labels,closed&filter=open")
torus = json.loads(resp2.read())
print(f"\nTorus_Ops: {len(torus)} open")
for c in torus:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    print(f"  [{','.join(labels)[:25]}] {c['name'][:50]}")