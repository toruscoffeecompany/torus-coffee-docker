#!/usr/bin/env python3
"""
Inbox Processor — reads shared inbox messages, creates Trello cards + GitHub issues, moves to processed.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
PROCESSED_DIR = Path("/z/processed")
INBOXES = {
    "miss_pink": Path("/z/MISS_PINK_INBOX"),
    "sir_green": Path("/z/SIR_GREEN_INBOX"),
    "sir_azure": Path("/z/SIR_AZURE_INBOX"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_trello_creds() -> tuple[str, str]:
    text = CRED_FILE.read_text(errors="ignore")
    api_key = None
    token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello API credentials missing")
    return api_key, token


def load_github_token() -> str:
    try:
        data = json.loads(VAULT.joinpath("10_Skills_Library/05_Operations/secrets.local.json").read_text(encoding="utf-8"))
        token = data.get("github_token", "")
        if not token:
            raise RuntimeError("GitHub token missing")
        return token
    except Exception as exc:
        raise RuntimeError(f"Failed to load GitHub token: {exc}")


def create_trello_card(api_key: str, token: str, name: str, desc: str, board: str = "Torus_Ops", list_name: str = "Backlog", label_names: list[str] | None = None) -> dict | None:
    base = "https://api.trello.com/1"
    params = {"key": api_key, "token": token}
    boards = requests.get(f"{base}/members/me/boards", params=params, timeout=15).json()
    board_id = next((b["id"] for b in boards if b["name"] == board), None)
    if not board_id:
        return None
    lists = requests.get(f"{base}/boards/{board_id}/lists", params={**params, "fields": "name,id"}, timeout=15).json()
    list_id = next((l["id"] for l in lists if l["name"] == list_name), None)
    if not list_id:
        return None
    labels = requests.get(f"{base}/boards/{board_id}/labels", params={**params, "fields": "name,id"}, timeout=15).json()
    label_map = {l["name"]: l["id"] for l in labels if l["name"]}
    label_ids = [label_map[n] for n in (label_names or []) if n in label_map]
    # ANTI-DUPLICATION: check if card with same name already exists on this list
    existing_cards = requests.get(f"{base}/lists/{list_id}/cards", params={**params, "fields": "name,closed"}, timeout=15).json()
    for ec in existing_cards:
        if ec.get("name") == name and not ec.get("closed", False):
            return {"id": ec["id"], "name": name, "duplicate_skipped": True}
    card_data = {
        "key": api_key,
        "token": token,
        "idList": list_id,
        "name": name,
        "desc": desc,
    }
    if label_ids:
        card_data["idLabels"] = ",".join(label_ids)
    r = requests.post(f"{base}/cards", data=card_data, timeout=15)
    if r.status_code == 200:
        return r.json()
    return None


def create_github_issue(title: str, body: str, repo: str = "toruscoffeecompany/Torus_Ops") -> str | None:
    token = load_github_token()
    try:
        r = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            json={"title": title, "body": body},
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code == 201:
            return r.json().get("html_url")
        print(f"GitHub issue failed: {r.status_code} {r.text[:200]}")
    except Exception as exc:
        print(f"GitHub issue error: {exc}")
    return None


def process_inbox(api_key: str, token: str, owner: str, inbox_path: Path) -> int:
    if not inbox_path.exists():
        return 0
    files = sorted(inbox_path.glob("*.md"))
    processed = 0
    for path in files:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            name = path.stem.replace("_", " ")[:120]
            card = create_trello_card(api_key, token, f"📨 {name}", content[:500], label_names=["inbox", "automation"])
            if card:
                create_github_issue(f"📨 Inbox: {name}", content[:1000])
            target = PROCESSED_DIR / owner
            target.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target / path.name))
            processed += 1
        except Exception as exc:
            print(f"[{owner}] failed {path.name}: {exc}")
    return processed


def main() -> int:
    api_key, token = load_trello_creds()
    total = 0
    for owner, inbox in INBOXES.items():
        count = process_inbox(api_key, token, owner, inbox)
        print(f"[{owner}] processed {count}")
        total += count
    print(f"Total processed: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
