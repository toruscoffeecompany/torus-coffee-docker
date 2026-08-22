#!/usr/bin/env python3
"""
GitHub-to-Trello Smart Ticket Bridge for Torus Coffee Company.

Imports GitHub issues into Trello as cards, maintaining cross-platform sync.
Ensures all crew members follow the same OODA ticket lifecycle rules.

Usage:
    venv/Scripts/python.exe scripts/github_trello_bridge.py sync
    venv/Scripts/python.exe scripts/github_trello_bridge.py sync --dry-run
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library/05_Operations"
sys.path.insert(0, str(AUTOMATION_DIR / "scripts"))
from credential_loader import load_trello_credentials

GITHUB_REPOS = [
    "toruscoffeecompany/Torus_Ops",
    "toruscoffeecompany/torus-coffee-docker",
    "toruscoffeecompany/Torus_website_rebuild",
]

# Trello board + list IDs
BOARD_ID = "6a70a3157d0db4214ac3f9a3"
P0_LIST = "6a74cbd440270147ff04bd5b"   # P0 - Alert / Critical / Do Now
P1_LIST = "6a74cbd5e3d54d2d08be82e7"   # P1 - High / Doing Now
P2_LIST = "6a74cbd4148f814483a64589"   # P2 - Med High / This Week
P3_LIST = "6a70a32923622d3e00107d70"   # P3 - Medium / Follow Up

# Priority mapping from GitHub labels
PRIORITY_MAP = {
    "p0": {"list": P0_LIST, "label": "P0"},
    "p1": {"list": P1_LIST, "label": "P1"},
    "p2": {"list": P2_LIST, "label": "P2"},
    "p3": {"list": P3_LIST, "label": "P3"},
}

# Crew assignment rules (Miss Pink's OODA)
CREW_LABELS = {
    "miss-pink": "Miss Pink",
    "sir-green": "Sir Green",
    "sir-azure": "Sir Azure",
    "crew": "Crew",
}

# Label ID for miss-pink
MISS_PINK_LABEL_ID = "6a74dd623356f01be75f7d0c"
AUTOMATION_LABEL_ID = "6a739cca616c68bad376bcef"
OPS_LABEL_ID = "6a739cca998ce46096d11667"
DOCKER_LABEL_ID = "6a74cc133f8d2e6b144aa1d4"  # docker label ID (approximate)

# State file for tracking synced issues
STATE_FILE = AUTOMATION_DIR / "github_trello_bridge_state.json"


def log(msg: str):
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"synced": {}}
    return {"synced": {}}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_github_token() -> str:
    """Load GitHub token from vault secrets."""
    secrets_files = [
        AUTOMATION_DIR / "secrets.local.json",
        VAULT / ".secrets.local.json",
    ]
    for sf in secrets_files:
        if sf.exists():
            try:
                data = json.loads(sf.read_text(encoding="utf-8"))
                token = data.get("github_token") or data.get("miss_pink_github_token")
                if token and not token.startswith("REPLACE_WITH"):
                    return token
            except Exception:
                pass
    return None


def get_trello_creds() -> tuple:
    creds = load_trello_credentials()
    return creds["api_key"], creds["token"]


def get_trello_label_ids(key: str, token: str) -> dict:
    """Fetch all label IDs for the board."""
    r = requests.get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/labels",
        params={"key": key, "token": token},
        timeout=20,
    )
    labels = r.json()
    return {l["name"]: l["id"] for l in labels}


def create_trello_card(
    key: str, token: str, repo: str, issue: dict, label_ids: dict, dry_run: bool = False
) -> str | None:
    """Create a Trello card from a GitHub issue."""
    title = issue["title"]
    number = issue["number"]
    issue_url = issue.get("html_url", f"https://github.com/{repo}/issues/{number}")
    body = issue.get("body") or ""

    # Determine priority from labels
    gh_labels = [l["name"].lower() for l in issue.get("labels", [])]
    priority = "p1"  # default
    for label in gh_labels:
        if label in PRIORITY_MAP:
            priority = label
            break

    target_list = PRIORITY_MAP[priority]["list"]

    # Build card description
    desc = f"## GitHub Issue: {repo}#{number}\n\n"
    desc += f"**Repo:** `{repo}`\n"
    desc += f"**Issue URL:** {issue_url}\n"
    desc += f"**State:** {issue.get('state', 'open')}\n"
    desc += f"**Priority:** {priority.upper()}\n"
    desc += f"**GitHub Labels:** {', '.join(gh_labels) if gh_labels else '(none)'}\n\n"
    desc += f"## Description\n\n{body[:3000]}\n\n"
    desc += f"---\n## Sync Rules (OODA Ticket Lifecycle)\n"
    desc += f"1. ONE primary source of truth — GitHub issue remains the spec\n"
    desc += f"2. Progress tracked via Trello card status + comments\n"
    desc += f"3. Miss Pink: P0/P1 cards — work + close\n"
    desc += f"4. Sir Green: Sir Green Queue cards — do NOT process\n"
    desc += f"5. Sir Azure: Sir Azure Queue cards — do NOT process\n"
    desc += f"6. Card auto-requeued from Done if fleet mentions detected\n"

    # Collect label IDs for the card
    card_label_ids = []
    for label_name in ["automation", "ops", "docker", "P0", "P1", "P2", "P3"]:
        if label_name in label_ids:
            # Avoid duplicates with priority labels
            pass
    
    # Use priority label + miss-pink + automation + source labels
    card_labels = []
    if priority.upper() in label_ids:
        card_labels.append(label_ids[priority.upper()])
    if "miss-pink" in label_ids:
        card_labels.append(label_ids["miss-pink"])
    if "automation" in label_ids:
        card_labels.append(label_ids["automation"])
    if "docker" in gh_labels and "docker" in label_ids:
        card_labels.append(label_ids["docker"])
    if "obsidian" in gh_labels and "ops" in label_ids:
        card_labels.append(label_ids["ops"])

    if dry_run:
        log(f"  [DRY-RUN] Would create card: {title[:60]}")
        return None

    r = requests.post(
        "https://api.trello.com/1/cards",
        params={"key": key, "token": token},
        json={
            "name": f"[{repo}#{number}] {title[:100]}",
            "idList": target_list,
            "desc": desc,
            "idLabels": ",".join(card_labels),
            "pos": "top",
        },
        timeout=30,
    )
    if r.status_code == 200:
        card_id = r.json()["id"]
        log(f"  ✅ Created card: [{repo}#{number}] {title[:60]}")
        return card_id
    else:
        log(f"  ✗ Failed: [{repo}#{number}] {r.status_code} {r.text[:100]}")
        return None


def sync_issues(dry_run: bool = False) -> dict:
    """Sync GitHub issues to Trello cards."""
    token = get_github_token()
    if not token:
        log("ERROR: No GitHub token found in vault secrets")
        return {"status": "error", "error": "No GitHub token"}

    key, tkey = get_trello_creds()
    label_ids = get_trello_label_ids(key, tkey)

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    state = load_state()
    synced = state.setdefault("synced", {})

    created = 0
    skipped = 0
    updated = 0

    for repo in GITHUB_REPOS:
        log(f"\n--- Scanning {repo} ---")
        r = requests.get(
            f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100",
            headers=headers,
            timeout=30,
        )
        if r.status_code == 404:
            log(f"  ⚠ Repo not accessible: {repo}")
            continue
        issues = r.json()
        for issue in issues:
            # Skip PRs
            if "pull_request" in issue:
                continue

            number = issue["number"]
            key_str = f"{repo}#{number}"

            # Check if already synced
            if key_str in synced and synced[key_str].get("status") == "synced":
                # Check if issue was closed
                if issue.get("state") == "closed":
                    log(f"  🔄 {key_str} — Issue closed, marking Done in Trello")
                    card_id = synced[key_str].get("trello_card_id")
                    if card_id:
                        # Move to done list
                        requests.put(
                            f"https://api.trello.com/1/cards/{card_id}",
                            params={"key": key, "token": tkey, "idList": "6a70a32a723c0312a3d5fbb4"},
                            timeout=20,
                        )
                    synced[key_str]["status"] = "done"
                    updated += 1
                continue

            # Crew assignment rules — route issues to correct crew member
            gh_labels = [l["name"].lower() for l in issue.get("labels", [])]
            title_lower = issue["title"].lower()
            
            # Sir Azure exclusive — do NOT create Miss Pink cards
            title_sir_azure = "sir azure" in title_lower and "sir green" not in title_lower
            sir_azure_label = "sir-azure" in gh_labels or "sir_azure" in gh_labels
            if title_sir_azure or sir_azure_label:
                log(f"  ⏭️  {key_str} — Skipping (Sir Azure exclusive)")
                skipped += 1
                continue
            
            # Sir Green exclusive — do NOT create Miss Pink cards
            title_sir_green = "sir green" in title_lower and "sir azure" not in title_lower
            sir_green_label = "sir-green" in gh_labels or "sir_green" in gh_labels
            if (title_sir_green or sir_green_label) and "miss-pink" not in gh_labels:
                # Could be Sir Green/VOID — but if it's about Miss Pink work, sync it
                if "miss pink" not in title_lower and "misspink" not in title_lower and "torus coffee" in title_lower:
                    log(f"  ⏭️  {key_str} — Skipping (likely Sir Green/VOID scope)")
                    skipped += 1
                    continue
            # MISSING: also check crew labels for miss-gordon etc
            if any(t in gh_labels for t in ["miss-gordan", "miss-gordon", "sir-cobalt", "sir-violet"]):
                log(f"  ⏭️  {key_str} — Skipping (another crew member)")
                skipped += 1
                continue

            # Crew label check — skip if labeled for another crew member
            if "crew" in gh_labels and not any(t in gh_labels for t in ["miss-pink", "misspink", "automation", "ops", "P0", "P1", "P2", "P3"]):
                crew_tags = [t for t in gh_labels if t in ("sir-green", "sir-azure", "crew")]
                if crew_tags:
                    log(f"  ⏭️  {key_str} — Skipping (crew tag: {crew_tags})")
                    skipped += 1
                    continue

            # Create card for Miss Pink-relevant issues
            card_id = create_trello_card(key, tkey, repo, issue, label_ids, dry_run)
            if card_id:
                synced[key_str] = {
                    "trello_card_id": card_id,
                    "github_repo": repo,
                    "github_issue": number,
                    "title": issue["title"][:100],
                    "status": "synced",
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                }
                created += 1

    if not dry_run:
        save_state(state)

    return {"status": "complete", "created": created, "skipped": skipped, "updated": updated}


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        log("DRY RUN MODE — no cards will be created")

    result = sync_issues(dry_run=dry_run)
    log(f"\nSYNC_COMPLETE: {json.dumps(result, default=str)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
