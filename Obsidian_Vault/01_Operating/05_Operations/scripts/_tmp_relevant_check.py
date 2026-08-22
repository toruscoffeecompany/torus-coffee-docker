from pathlib import Path
import requests
from collections import Counter
creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
key = lines[0].strip("`")
token = lines[2].strip("`")
lists = requests.get(
    "https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=15,
).json()
cards = requests.get(
    "https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards",
    params={"key": key, "token": token, "fields": "id,name,due,idList,labels", "limit": 1000, "filter": "all"},
    timeout=30,
).json()
list_counts = Counter(c.get("idList") for c in cards)
relevant = []
for c in cards:
    list_name = next((l["name"] for l in lists if l["id"] == c.get("idList")), "")
    if not c.get("due"):
        continue
    if any(f in list_name.lower() for f in ["done","future ideas","sir azure's queue","sir green's queue"]):
        continue
    if list_name in {"Top 10 — Focus Fleet", "P1 - High / Doing Now"}:
        relevant.append(c)
        continue
    label_names = [l.get("name","").lower() for l in c.get("labels",[])]
    if any(name in label_names for name in ["p0","p1","p2","top 10"]):
        relevant.append(c)
print('TOTAL', len(cards))
for l in lists:
    print('LIST', l['name'], list_counts.get(l['id'],0))
print('RELEVANT', len(relevant))
