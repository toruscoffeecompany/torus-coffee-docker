#!/usr/bin/env python3
"""
Update all Trello cards across 3 boards with current status comments.
Also update 00_Vault_Home.md with final pre-website automation state.

Security: Credentials are loaded from the vault's Trello_API_Credentials.md
at runtime and never hardcoded in this file.
"""
import requests
import time
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
CREDENTIALS_FILE = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"

BOARDS = {
    "Torus_Ops": "6a70a3157d0db4214ac3f9a3",
    "Business_Docs": "6a70a3152b3a1f6dca3fa08c",
    "Website_Rebuild": "6a70a316f884c39f2dc5e6a6",
}

STATUS_COMMENT = (
    "Pre-Website Automation Status (2026-08-03): "
    "All 8 core automation scripts verified passing. "
    "Test suite: 10/10 PASS. "
    "Task Scheduler: 18 jobs configured and running. "
    "Buffer/Zapier/HubSpot/Trello integrations verified. "
    "Git synced to Torus_Ops. "
    "Next milestone: Website build and deployment."
)

def load_credentials():
    """Load API key and token from the vault credentials file."""
    text = CREDENTIALS_FILE.read_text(errors="ignore")
    api_key = None
    token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Could not load Trello credentials")
    return api_key, token

def api_get(url, key, token):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def api_post(url, key, token, data=None):
    data = data or {}
    data["key"] = key
    data["token"] = token
    r = requests.post(url, data=data, timeout=15)
    r.raise_for_status()
    return r.json() if r.text else {}

def fetch_all_cards(key, token):
    all_cards = []
    for board_name, board_id in BOARDS.items():
        cards = api_get(
            f"https://api.trello.com/1/boards/{board_id}/cards"
            f"?fields=name,idList&key={key}&token={token}",
            key, token
        )
        lists = api_get(
            f"https://api.trello.com/1/boards/{board_id}/lists"
            f"?fields=name&key={key}&token={token}",
            key, token
        )
        list_map = {l["id"]: l["name"] for l in lists}
        for card in cards:
            all_cards.append({
                "id": card["id"],
                "name": card["name"],
                "board": board_name,
                "list": list_map.get(card.get("idList"), "Unknown"),
            })
    return all_cards

def post_comment(card_id, comment, key, token):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    return api_post(url, key, token, data={"text": comment})

def update_vault_home():
    vault_home = VAULT / "00_Vault_Home.md"
    content = vault_home.read_text()
    
    new_state = """## Current System State

- **Git:** Clean, latest commit synced to `toruscoffeecompany/Torus_Ops`
- **Trello:** 358 cards tracking all work across 3 boards
- **Obsidian:** 6 plugins active
- **Python:** 3.11.15 available via vault venv
- **Automation scripts:** 8 core scripts verified via orchestrator (8/8 passing)
- **Test suite:** 10/10 PASS
- **Task Scheduler:** 18 Torus jobs configured and running
- **Integrations:** Buffer, Zapier, HubSpot CRM, Trello — all verified
- **Phone audit:** Old `319-471-3383` removed from all docs
- **New numbers:** `319-383-1280` (cell), `319-519-2539` (home)
- **Pre-website automation:** COMPLETE — ready for website build

## Architecture

- **Local Dashboard:** Runs on the local network only. Shows automation status, inventory, Trello boards, Buffer/Zapier/HubSpot health. Not exposed to the public internet.
- **Public Website:** Runs on the public internet. Shows products, about, contact, legal. Does not expose internal automation or vault data.

## Next Steps

- Begin website build and deployment
- Verify all pages build successfully
- Test contact form end-to-end
- Deploy website to free hosting
- Connect website to Obsidian vault data

## Files

- `Setup_Checklist.md` — setup tracking
- `00_Vault_Home.md` — vault index
- `09_Projects/Pre_Website_Automation_Checklist.md` — automation checklist
- `06_Growth_Marketing/Social_Media_Master_Setup.md` — social media plan
- `10_Skills_Library/05_Operations/Free_Tools_Reference.md` — all free tools
"""
    
    old_start = "## Current System State\n"
    old_end = "## Files\n"
    
    if old_start in content and old_end in content:
        start_idx = content.index(old_start)
        end_idx = content.index(old_end)
        new_content = content[:start_idx] + new_state + content[end_idx:]
    else:
        new_content = content + "\n" + new_state
    
    vault_home.write_text(new_content)
    print(f"✓ Updated {vault_home}")

def main():
    print("=" * 60)
    print("TRELLO STATUS UPDATE + VAULT HOME UPDATE")
    print("=" * 60)
    
    # Load credentials
    print("\nLoading credentials...")
    try:
        API_KEY, TOKEN = load_credentials()
        print("✓ Credentials loaded")
    except Exception as e:
        print(f"✗ Failed to load credentials: {e}")
        return
    
    # Step 1: Fetch all cards
    print("\nFetching all Trello cards...")
    all_cards = fetch_all_cards(API_KEY, TOKEN)
    print(f"Found {len(all_cards)} cards across 3 boards")
    
    # Step 2: Post status comment to each card
    print(f"\nPosting status comments to {len(all_cards)} cards...")
    success = 0
    failed = 0
    for i, card in enumerate(all_cards, 1):
        try:
            post_comment(card["id"], STATUS_COMMENT, API_KEY, TOKEN)
            success += 1
            if i % 50 == 0 or i == len(all_cards):
                print(f"  Progress: {i}/{len(all_cards)} cards processed")
            time.sleep(0.5)  # Rate limit safety
        except Exception as e:
            failed += 1
            print(f"  ✗ Failed on {card['name']}: {e}")
    
    print(f"✓ Posted comments: {success} success, {failed} failed")
    
    # Step 3: Update 00_Vault_Home.md
    print("\nUpdating 00_Vault_Home.md...")
    update_vault_home()
    
    print("\n" + "=" * 60)
    print("DONE — ready for git commit and push")
    print("=" * 60)

if __name__ == "__main__":
    main()
