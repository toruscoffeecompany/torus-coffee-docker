#!/usr/bin/env python3
"""
Progress Updater — periodically updates GitHub issues and Trello cards with current status.
Runs as a background process.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
TRELLO_CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
OODA_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "ooda_loop.log"
UPDATE_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "progress_updater.log"
INTERVAL = 900  # 15 minutes


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    try:
        UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{now_iso()}] {msg}"
        with open(UPDATE_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass


def get_gh_token() -> str:
    try:
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        token = data.get("github_token", "")
        if not token:
            raise RuntimeError("GitHub token missing")
        return token
    except Exception as exc:
        raise RuntimeError(f"Failed to load GitHub token: {exc}")


def load_trello_creds() -> tuple[str, str]:
    text = TRELLO_CRED_FILE.read_text(errors="ignore")
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


def get_ooda_status() -> str:
    try:
        if OODA_LOG.exists():
            lines = OODA_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
            if lines:
                return lines[-1]
    except Exception:
        pass
    return "OODA loop status unknown"


def update_github_issues(token: str) -> int:
    try:
        r = requests.get(
            "https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues",
            params={"state": "open", "per_page": 100},
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code != 200:
            return 0
        issues = r.json()
        ooda_status = get_ooda_status()
        updated = 0
        for issue in issues:
            if issue.get("pull_request"):
                continue
            body = (
                f"OODA Loop Status: {ooda_status}\n"
                f"Last checked: {now_iso()}\n"
                "This issue is tracked by the automated OODA loop running on PINKCADY."
            )
            cr = requests.post(
                f"https://api.github.com/repos/toruscoffeecompany/Torus_Ops/issues/{issue['number']}/comments",
                json={"body": body},
                headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"},
                timeout=15,
            )
            if cr.status_code == 201:
                updated += 1
        return updated
    except Exception as exc:
        log(f"GITHUB_UPDATE_ERROR {exc}")
        return 0


def update_trello_cards(api_key: str, token: str) -> int:
    try:
        base = "https://api.trello.com/1"
        params = {"key": api_key, "token": token}
        boards = requests.get(f"{base}/members/me/boards", params=params, timeout=15).json()
        torus_ops = next((b for b in boards if b["name"] == "Torus_Ops"), None)
        if not torus_ops:
            return 0
        cards = requests.get(
            f"{base}/boards/{torus_ops['id']}/cards",
            params={**params, "fields": "name,id,desc", "limit": 200},
            timeout=15,
        ).json()
        ooda_status = get_ooda_status()
        updated = 0
        for c in cards:
            status_note = (
                f"\n\n[PROGRESS UPDATE {now_iso()}] OODA Loop Status: {ooda_status}"
            )
            new_desc = c["desc"] + status_note if c["desc"] else status_note
            r = requests.put(
                f"{base}/cards/{c['id']}",
                data={"key": api_key, "token": token, "desc": new_desc},
                timeout=15,
            )
            if r.status_code == 200:
                updated += 1
        return updated
    except Exception as exc:
        log(f"TRELLO_UPDATE_ERROR {exc}")
        return 0


def run_update() -> None:
    gh_token = get_gh_token()
    api_key, token = load_trello_creds()
    gh_updated = update_github_issues(gh_token)
    trello_updated = update_trello_cards(api_key, token)
    log(f"PROGRESS_UPDATE complete: github={gh_updated}, trello={trello_updated}")


def main() -> int:
    log("PROGRESS_UPDATER_STARTED")
    while True:
        try:
            run_update()
        except Exception as exc:
            log(f"PROGRESS_UPDATE_ERROR {exc}")
        time.sleep(INTERVAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
