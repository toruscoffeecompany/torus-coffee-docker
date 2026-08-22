#!/usr/bin/env python3
"""
Miss Pink inbox watcher / alerter + auto-processor.
Watches /z/ shared inboxes for new *.msg.md files.
When new files appear:
- creates Trello card
- creates GitHub issue
- moves file to /z/processed/<owner>/
Logs alerts to 10_Skills_Library/05_Operations/logs/inbox_alerts.json
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
STATE = BASE / "10_Skills_Library" / "05_Operations" / "Crew" / ".pink_inbox_state.json"
ALERTS = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "inbox_alerts.json"
PROCESSED = Path("/z/processed")
INBOXES = {
    "miss_pink": Path("/z/MISS_PINK_INBOX"),
    "sir_green": Path("/z/SIR_GREEN_INBOX"),
    "sir_azure": Path("/z/SIR_AZURE_INBOX"),
}
CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    try:
        ALERTS.parent.mkdir(parents=True, exist_ok=True)
        data = []
        if ALERTS.exists():
            try:
                data = json.loads(ALERTS.read_text(encoding="utf-8"))
            except Exception:
                data = []
        data.append({"ts": now_iso(), "msg": msg})
        ALERTS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {"processed": {}}
    return {"processed": {}}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


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
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
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
            create_trello_card(api_key, token, f"📨 {name}", content[:500], label_names=["inbox", "automation"])
            create_github_issue(f"📨 Inbox: {name}", content[:1000])
            target = PROCESSED / owner
            target.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target / path.name))
            processed += 1
        except Exception as exc:
            print(f"[{owner}] failed {path.name}: {exc}")
    return processed


def run_once() -> int:
    state = load_state()
    processed = state.setdefault("processed", {})
    total = 0
    for owner, inbox in INBOXES.items():
        if not inbox.exists():
            continue
        files = sorted(inbox.glob("*.md"))
        new_files = [f for f in files if f.name not in processed]
        if new_files:
            log(f"NEW_INBOX_FILES: {owner} {[f.name for f in new_files]}")
            api_key, token = load_trello_creds()
            count = process_inbox(api_key, token, owner, inbox)
            log(f"PROCESSED: {owner} {count} files")
            total += count
            for f in new_files:
                processed[f.name] = now_iso()
    save_state(state)
    return total


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        count = run_once()
        print(f"Processed {count} inbox files")
        return 0
    log("WATCHER_STARTED")
    last_total = 0
    while True:
        try:
            count = run_once()
            if count > 0:
                log(f"WATCHER_CYCLE processed={count}")
            last_total += count
            import time
            time.sleep(30)
        except KeyboardInterrupt:
            log("WATCHER_STOPPED")
            break
        except Exception as exc:
            log(f"WATCHER_ERROR {exc}")
            import time
            time.sleep(30)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
