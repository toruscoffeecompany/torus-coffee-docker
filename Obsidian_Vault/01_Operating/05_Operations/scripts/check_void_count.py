"""Check VOID_Ops card counts."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed&filter=open")
cards = json.loads(resp.read())
print(f"VOID_Ops open: {len(cards)}")

sg = sa = other = 0
for c in cards:
    labels = [l.get("name", "").lower() for l in c.get("labels", []) if isinstance(l, dict)]
    if "sir-green" in labels: sg += 1
    elif "sir-azure" in labels: sa += 1
    else: other += 1

print(f"  Sir Green: {sg}")
print(f"  Sir Azure: {sa}")
print(f"  Other: {other}")