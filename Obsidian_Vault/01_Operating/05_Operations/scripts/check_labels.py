"""Check Torus_Ops cards by actual label assignment."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards?fields=name,labels,idList&filter=open&limit=1000&key={TRELLO_KEY}&token={TRELLO_TOKEN}")
cards = json.loads(resp.read())

print(f"Torus_Ops: {len(cards)} open cards\n")

sg_cards = []
mp_cards = []
sa_cards = []
no_label = []

for c in cards:
    labels = [l.get("name","") for l in c.get("labels",[]) if isinstance(l,dict)]
    label_str = ",".join(labels)
    
    if "sir-green" in labels and "miss-pink" not in labels:
        sg_cards.append(c)
        print(f"  [SG-ONLY]   {c['name'][:55]}  labels=[{label_str[:40]}]")
    elif "sir-azure" in labels and "miss-pink" not in labels and "sir-green" not in labels:
        sa_cards.append(c)
        print(f"  [SA-ONLY]   {c['name'][:55]}  labels=[{label_str[:40]}]")
    elif "miss-pink" in labels:
        mp_cards.append(c)
        print(f"  [MP]        {c['name'][:55]}  labels=[{label_str[:40]}]")
    else:
        no_label.append(c)
        print(f"  [NO-LABEL]  {c['name'][:55]}  labels=[{label_str[:40]}]")

print(f"\n=== Summary ===")
print(f"Sir Green only: {len(sg_cards)}")
print(f"Sir Azure only: {len(sa_cards)}")
print(f"Miss Pink: {len(mp_cards)}")
print(f"No label: {len(no_label)}")