from pathlib import Path
import requests
from datetime import datetime
from collections import defaultdict

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

list_counts = {}
for c in cards:
    list_counts[c.get("idList")] = list_counts.get(c.get("idList"), 0) + 1

name_groups = defaultdict(list)
for c in cards:
    name_groups[c["name"].strip().lower()].append(c)

dup_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
to_archive = []
for name, group in dup_groups.items():
    newest = max(group, key=lambda c: c.get("dateLastActivity") or "")
    for c in group:
        if c["id"] != newest["id"]:
            to_archive.append(c)

print(f"Total cards: {len(cards)}")
print(f"Duplicate groups: {len(dup_groups)}")
print(f"Cards to archive: {len(to_archive)}")
for l in lists:
    print(f"  {l['name']}: {list_counts.get(l['id'], 0)}")
print("\nArchiving duplicates...")
for i, c in enumerate(to_archive, 1):
    r = requests.put(
        f"https://api.trello.com/1/cards/{c['id']}",
        params={"key": key, "token": token},
        data={"closed": "true"},
        timeout=10,
    )
    print(f"  {i}/{len(to_archive)}: {r.status_code} {c['name'][:50]}")
    if i % 20 == 0:
        import time
        time.sleep(2)
print("Done")
