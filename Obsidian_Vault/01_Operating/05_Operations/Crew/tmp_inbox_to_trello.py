import requests
from pathlib import Path
import json

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"

text = CRED_FILE.read_text(errors="ignore")
api_key = token = None
lines = text.splitlines()
for i, line in enumerate(lines):
    if "API Key" in line and i+1 < len(lines):
        api_key = lines[i+1].strip().strip("`")
    elif "Token" in line and "OAuth" not in line and i+1 < len(lines):
        token = lines[i+1].strip().strip("`")

gh_token = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))["github_token"]

base = "https://api.trello.com/1"
params = {"key": api_key, "token": token}
boards = requests.get(f"{base}/members/me/boards", params=params, timeout=15).json()
torus_ops = next(b for b in boards if b['name'] == 'Torus_Ops')
labels = requests.get(f"{base}/boards/{torus_ops['id']}/labels", params={**params, "fields": "name,id"}, timeout=15).json()
label_map = {l['name']: l['id'] for l in labels if l['name']}
lists = requests.get(f"{base}/boards/{torus_ops['id']}/lists", params={**params, "fields": "name,id"}, timeout=15).json()
list_map = {l['name']: l['id'] for l in lists}

backlog = list_map.get("Backlog") or list_map.get("To_Do")

inbox_dir = Path("/z/MISS_PINK_INBOX")
for path in sorted(inbox_dir.glob("*.md")):
    content = path.read_text(encoding="utf-8", errors="ignore")
    name = path.stem.replace("_", " ")[:120]
    card_data = {
        "key": api_key,
        "token": token,
        "idList": backlog,
        "name": "📨 [INBOX] " + name,
        "desc": content[:1000],
        "idLabels": label_map.get('inbox', ''),
    }
    r = requests.post(f"{base}/cards", data=card_data, timeout=15)
    print(r.status_code, card_data["name"])
