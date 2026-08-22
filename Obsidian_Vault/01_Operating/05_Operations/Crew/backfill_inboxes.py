import requests
from pathlib import Path
import shutil
import json

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
OODA_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "ooda_loop.log"

text = CRED_FILE.read_text(errors="ignore")
api_key = token = None
lines = text.splitlines()
for i, line in enumerate(lines):
    if "API Key" in line and i+1 < len(lines):
        api_key = lines[i+1].strip().strip("`")
    elif "Token" in line and "OAuth" not in line and i+1 < len(lines):
        token = lines[i+1].strip().strip("`")

gh_token = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))["github_token"]
headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer " + gh_token}

def log(msg: str) -> None:
    from datetime import datetime, timezone
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    try:
        OODA_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(OODA_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

base = "https://api.trello.com/1"
params = {"key": api_key, "token": token}
boards = requests.get(f"{base}/members/me/boards", params=params, timeout=15).json()
torus_ops = next(b for b in boards if b['name'] == 'Torus_Ops')
labels = requests.get(f"{base}/boards/{torus_ops['id']}/labels", params={**params, "fields": "name,id"}, timeout=15).json()
label_map = {l['name']: l['id'] for l in labels if l['name']}
lists = requests.get(f"{base}/boards/{torus_ops['id']}/lists", params={**params, "fields": "name,id"}, timeout=15).json()
list_map = {l['name']: l['id'] for l in lists}

backlog = list_map.get("Backlog") or list_map.get("To_Do")
print(f"Backlog list ID: {backlog}")
print(f"Inbox label: {label_map.get('inbox')}")

INBOXES = {
    "miss_pink": Path(r"Z:\MISS_PINK_INBOX"),
    "sir_azure": Path(r"Z:\SIR_AZURE_INBOX"),
    "sir_green": Path(r"Z:\SIR_GREEN_INBOX"),
}
PROCESSED = Path(r"Z:\processed")

def process_inbox(owner: str) -> int:
    inbox = INBOXES[owner]
    if not inbox.exists():
        print(f"INBOX_MISSING: {inbox}")
        return 0
    files = sorted(inbox.glob("*.md"))
    print(f"{owner}: {len(files)} files")
    moved = 0
    for path in files:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            name = path.stem.replace("_", " ")[:120]

            card_data = {
                "key": api_key,
                "token": token,
                "idList": backlog,
                "name": f"📨 [INBOX] {name}",
                "desc": content[:1000],
            }
            if label_map.get('inbox'):
                card_data['idLabels'] = label_map['inbox']

            r = requests.post(f"{base}/cards", data=card_data, timeout=15)
            print(f"  TRELLO {r.status_code} {name}")

            r2 = requests.post(
                "https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues",
                json={"title": f"📨 Inbox: {name}", "body": content[:1000], "labels": ["inbox"]},
                headers=headers,
                timeout=15,
            )
            print(f"  GITHUB {r2.status_code} {name}")

            target = PROCESSED / owner
            target.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target / path.name))
            moved += 1
        except Exception as exc:
            log(f"INBOX_PROCESS_ERROR {path.name}: {exc}")
    return moved

for owner in ["miss_pink", "sir_azure", "sir_green"]:
    count = process_inbox(owner)
    log(f"BACKFILL_PROCESSED {owner}: {count}")
