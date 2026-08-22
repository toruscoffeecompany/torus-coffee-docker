#!/usr/bin/env python3
"""
Torus Coffee OODA Loop Agent
Continuously processes Trello cards, executes tasks, and maintains git sync.
"""
import json
import os
import subprocess
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("D:/Work/Torus Coffee Company LLC")
TRELLO_CREDS = BASE / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
TASK_STATE = BASE / "10_Skills_Library/05_Operations/Crew/.ooda_loop_state.json"
LOG_FILE = BASE / "10_Skills_Library/05_Operations/logs/ooda_loop.log"
PYTHON = BASE / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"

# Trello board/list IDs sourced from local credentials file only.
CREDENTIALS_FILE = BASE / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"

BOARDS = {
    "Torus Ops": "6a70a3157d0db4214ac3f9a3",
    "Business Docs": "6a70a3152b3a1f6dca3fa08c",
    "Website Rebuild": "6a70a316f884c39f2dc5e6a6",
}
BACKLOG_LISTS = {
    "Torus Ops": "6a70a3282e405a2460afc170",
    "Business Docs": "6a70a32a2a0910e4acaed0ee",
    "Website Rebuild": "6a70a32df0e9e791ac70bf4f",
}

def log(msg):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except:
        pass

def load_credentials():
    try:
        with open(TRELLO_CREDS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading Trello credentials: {e}")
        return None

def get_trello_cards(creds, board_id):
    """Fetch all cards from a Trello board"""
    url = f"https://api.trello.com/1/boards/{board_id}/cards"
    params = {
        "key": creds["api_key"],
        "token": creds["token"],
        "fields": "id,name,desc,labels,idList,idMembers,dateLastActivity,closed"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"ERROR fetching cards from board {board_id}: {e}")
        return []

def get_trello_lists(creds, board_id):
    """Fetch all lists from a Trello board"""
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {
        "key": creds["api_key"],
        "token": creds["token"],
        "fields": "id,name,pos,closed"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"ERROR fetching lists from board {board_id}: {e}")
        return []

def create_trello_card(creds, board_id, name, desc="", list_id=None, labels=None):
    """Create a new Trello card with anti-duplication."""
    # ANTI-DUPLICATION: check if card with same name already exists on board
    try:
        search_url = f"https://api.trello.com/1/boards/{board_id}/cards"
        existing = requests.get(search_url, params={
            "key": creds["api_key"],
            "token": creds["token"],
            "fields": "id,name,closed"
        }, timeout=20)
        if existing.status_code == 200:
            for c in existing.json():
                if c.get("name") == name and not c.get("closed", False):
                    log(f"⚠ Duplicate card skipped: {name} (already exists: {c['id']})")
                    return c
    except Exception:
        pass
    """Create a new Trello card"""
    url = "https://api.trello.com/1/cards"
    params = {
        "key": creds["api_key"],
        "token": creds["token"],
        "idBoard": board_id,
        "name": name,
        "desc": desc
    }
    if list_id:
        params["idList"] = list_id
    if labels:
        params["idLabels"] = labels
    
    try:
        resp = requests.post(url, params=params, timeout=30)
        resp.raise_for_status()
        card = resp.json()
        log(f"✓ Created card: {name} (ID: {card['id']})")
        return card
    except Exception as e:
        log(f"ERROR creating card '{name}': {e}")
        return None

def update_trello_card(creds, card_id, name=None, desc=None, list_id=None, closed=None):
    """Update an existing Trello card"""
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        "key": creds["api_key"],
        "token": creds["token"]
    }
    if name:
        params["name"] = name
    if desc:
        params["desc"] = desc
    if list_id:
        params["idList"] = list_id
    if closed is not None:
        params["closed"] = closed
    
    try:
        resp = requests.put(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"ERROR updating card {card_id}: {e}")
        return None

def add_trello_comment(creds, card_id, text):
    """Add a comment to a Trello card"""
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    params = {
        "key": creds["api_key"],
        "token": creds["token"],
        "text": text
    }
    try:
        resp = requests.post(url, params=params, timeout=30)
        resp.raise_for_status()
        return True
    except Exception as e:
        log(f"ERROR adding comment to card {card_id}: {e}")
        return False

def load_state():
    if TASK_STATE.exists():
        try:
            return json.loads(TASK_STATE.read_text(encoding="utf-8"))
        except:
            return {"processed_cards": {}, "completed_tasks": [], "bugs": []}
    return {"processed_cards": {}, "completed_tasks": [], "bugs": []}

def save_state(state):
    TASK_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASK_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def git_commit_and_push(message):
    """Commit and push changes to git"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=BASE, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=True, capture_output=True)
        log(f"✓ Git: {message}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e}")
        return False

def categorize_card(card, lists_map):
    """Categorize a card based on its list and labels"""
    list_name = lists_map.get(card.get("idList"), "Unknown")
    labels = [l["name"] for l in card.get("labels", [])]
    
    # Determine priority from labels
    priority = "P3"
    if "P1" in labels:
        priority = "P1"
    elif "P2" in labels:
        priority = "P2"
    
    # Determine status
    status = "To Do"
    if "Done" in list_name or "Complete" in list_name:
        status = "Done"
    elif "In Progress" in list_name or "Doing" in list_name:
        status = "In Progress"
    elif "Blocked" in list_name:
        status = "Blocked"
    
    return {
        "priority": priority,
        "status": status,
        "list": list_name,
        "labels": labels
    }

def process_ooda_cycle(creds):
    """Execute one OODA cycle: Observe, Orient, Decide, Act"""
    log("\n=== OODA CYCLE START ===")
    
    state = load_state()
    all_cards = []
    
    # OBSERVE: Collect all cards from all boards
    for board_name, board_id in BOARDS.items():
        lists = get_trello_lists(creds, board_id)
        lists_map = {l["id"]: l["name"] for l in lists}
        cards = get_trello_cards(creds, board_id)
        
        for card in cards:
            card["board_name"] = board_name
            card["list_name"] = lists_map.get(card.get("idList"), "Unknown")
            all_cards.append(card)
    
    log(f"Observed {len(all_cards)} total cards across {len(BOARDS)} boards")
    
    # ORIENT: Analyze cards and identify tasks
    incomplete_cards = [c for c in all_cards if not c.get("closed", False) and c.get("list_name") != "Done"]
    log(f"Found {len(incomplete_cards)} incomplete cards")
    
    # Group by board and priority
    by_board = {}
    for card in incomplete_cards:
        board = card["board_name"]
        if board not in by_board:
            by_board[board] = []
        by_board[board].append(card)
    
    # DECIDE & ACT: Process each board's cards
    tasks_completed = []
    new_cards_created = []
    
    for board_name, cards in by_board.items():
        log(f"\nProcessing {board_name}: {len(cards)} cards")
        
        for card in cards:
            card_id = card["id"]
            card_name = card["name"]
            
            # Skip if already processed in this cycle
            if card_id in state.get("processed_cards", {}):
                continue
            
            log(f"  → Processing: {card_name}")
            
            # Mark as processed
            state.setdefault("processed_cards", {})[card_id] = {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "board": board_name
            }
            
            # Add comment to card
            comment = f"OODA Agent processed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\nStatus: Queued for execution"
            add_trello_comment(creds, card_id, comment)
            
            # Categorize
            cat = categorize_card(card, {})
            log(f"    Priority: {cat['priority']}, Status: {cat['status']}")
            
            # Based on card name/content, determine action
            card_lower = card_name.lower()
            
            if "bug" in card_lower or "issue" in card_lower or "error" in card_lower:
                # This is a bug/issue - create tracking card if needed
                bug_desc = f"Original card: {card['url']}\n\nDiscovered during OODA cycle."
                new_card = create_trello_card(
                    creds,
                    BOARDS.get(board_name, list(BOARDS.values())[0]),
                    f"[BUG] {card_name}",
                    desc=bug_desc,
                    labels=["bug"]
                )
                if new_card:
                    new_cards_created.append(new_card["name"])
                    state.setdefault("bugs", []).append({
                        "original_card": card_id,
                        "new_card": new_card["id"],
                        "name": card_name,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
            
            elif "verify" in card_lower or "check" in card_lower:
                # Verification task - mark as in progress
                update_trello_card(creds, card_id, desc=card.get("desc", "") + f"\n\n[OODA] Verification started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
            
            tasks_completed.append(card_name)
    
    # Save state
    save_state(state)
    
    # Git commit if changes made
    if tasks_completed or new_cards_created:
        commit_msg = f"OODA: processed {len(tasks_completed)} tasks, created {len(new_cards_created)} cards"
        git_commit_and_push(commit_msg)
    
    log(f"\n=== OODA CYCLE COMPLETE ===")
    log(f"Tasks processed: {len(tasks_completed)}")
    log(f"New cards created: {len(new_cards_created)}")
    log(f"Total bugs tracked: {len(state.get('bugs', []))}")
    
    return {
        "tasks_processed": len(tasks_completed),
        "cards_created": len(new_cards_created),
        "total_bugs": len(state.get("bugs", []))
    }

def main():
    log("=" * 60)
    log("Torus Coffee OODA Loop Agent - STARTED")
    log("=" * 60)
    
    creds = load_credentials()
    if not creds:
        log("FATAL: Cannot load Trello credentials")
        sys.exit(1)
    
    log(f"Loaded credentials for: {creds.get('api_key', 'unknown')[:8]}...")
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            log(f"\n{'='*60}")
            log(f"OODA Cycle #{cycle_count}")
            log(f"{'='*60}")
            
            result = process_ooda_cycle(creds)
            
            log(f"\nCycle #{cycle_count} complete. Waiting 60s for next cycle...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            log("\nOODA Loop stopped by user")
            break
        except Exception as e:
            log(f"ERROR in OODA cycle: {e}")
            import traceback
            log(traceback.format_exc())
            time.sleep(60)

if __name__ == "__main__":
    main()
