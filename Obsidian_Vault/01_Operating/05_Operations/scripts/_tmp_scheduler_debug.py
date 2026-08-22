from pathlib import Path
import requests
import os
import json
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TRELLO_CREDENTIALS = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
GITHUB_REPO = "toruscoffeecompany/Torus_Ops"

def get_trello_credentials():
    raw = TRELLO_CREDENTIALS.read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines() if ln.startswith("`")]
    return lines[0].strip("`"), lines[2].strip("`")

key, token = get_trello_credentials()
lists = requests.get(
    "https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/lists",
    params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
    timeout=15,
).json()
cards = requests.get(
    "https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards",
    params={"key": key, "token": token, "fields": "id,name,due,idList,labels,dateLastActivity", "limit": 1000, "filter": "all"},
    timeout=30,
).json()

lists_by_id = {l["id"]: l for l in lists}
TRELLO_SYNC_LISTS = {"Top 10 — Focus Fleet", "P1 - High / Doing Now"}
TRELLO_SYNC_LABELS = {"P0", "P1", "P2", "Top 10"}
TRELLO_SKIP_LIST_FRAGMENTS = ["done", "future ideas", "sir azure's queue", "sir green's queue"]

relevant = []
for c in cards:
    list_name = (lists_by_id.get(c.get("idList")) or {}).get("name", "").lower()
    if any(f in list_name for f in TRELLO_SKIP_LIST_FRAGMENTS):
        continue
    if not c.get("due"):
        continue
    label_names = [l.get("name", "").lower() for l in c.get("labels", [])]
    if list_name in {s.lower() for s in TRELLO_SYNC_LISTS}:
        relevant.append(c)
        continue
    if any(name in label_names for name in [n.lower() for n in TRELLO_SYNC_LABELS]):
        relevant.append(c)

print('cards', len(cards))
print('relevant', len(relevant))
print('sample_relevant')
for c in relevant[:10]:
    print(c['name'], c.get('due'))

# github
try:
    out = os.popen(f"gh issue list -R {GITHUB_REPO} --state open --limit 100 --json number,title,labels").read()
    issues = json.loads(out)
    print('github_issues', len(issues))
    for i in issues[:10]:
        print('issue', i['number'], i['title'], [l['name'] for l in i.get('labels',[])])
except Exception as e:
    print('github_error', str(e))
