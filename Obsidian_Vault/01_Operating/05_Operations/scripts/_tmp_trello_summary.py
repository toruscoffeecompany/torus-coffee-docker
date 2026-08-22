from pathlib import Path
import requests
from collections import Counter, defaultdict

creds = Path("01_Operating/Operating Paperwork/Trello_API_Credentials.md").read_text(encoding="utf-8")
lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
key = lines[0].strip("`")
token = lines[2].strip("`")
board_id = "6a70a3157d0db4214ac3f9a3"

lists = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=15,
).json()
cards = requests.get(
    f"https://api.trello.com/1/boards/{board_id}/cards",
    params={"key": key, "token": token, "fields": "id,name,idList,labels,dateLastActivity,due", "limit": 1000, "filter": "all"},
    timeout=30,
).json()

list_counts = Counter(c.get("idList") for c in cards)
name_groups = defaultdict(list)
for c in cards:
    name_groups[c["name"].strip().lower()].append(c)
dup_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
active_dups = 0
for name, group in dup_groups.items():
    newest = max(group, key=lambda c: c.get("dateLastActivity") or "")
    for c in group:
        if c["id"] != newest["id"]:
            active_dups += 1

print('TOTAL', len(cards))
for l in lists:
    print(f"{l['name']}: {list_counts.get(l['id'],0)}")
print('DUPLICATE_GROUPS', len(dup_groups))
print('ACTIVE_DUPLICATE_CARDS', active_dups)
