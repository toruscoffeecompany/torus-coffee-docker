#!/usr/bin/env python3
"""Auto-process inbox alerts and create/sort Trello cards or GitHub issues.

FIX: Added crew coordination check + name-based deduplication to prevent
the 800+ Smart Bridge card duplication issue where multiple OODA scripts
created duplicate cards from the same inbox message.
"""
import re
import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Crew coordination system — prevents duplicate work across all 3 PCs
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Crew"))
try:
    from crew_coordination import claim_work_item, release_work_item, is_claimed
    CREW_COORDINATION = True
except ImportError:
    CREW_COORDINATION = False

CREW_ID = "misspink"

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
TRELLO_CREDENTIALS = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
GITHUB_SECRETS = REPO_ROOT / "10_Skills_Library/05_Operations/secrets.local.json"
ALERT_LOG = REPO_ROOT / "10_Skills_Library/05_Operations/ALERT_PROCESSING_LOG.json"

BOARD_ID = "6a70a3157d0db4214ac3f9a3"

def get_trello_credentials():
    creds = TRELLO_CREDENTIALS.read_text(encoding="utf-8")
    lines = [ln for ln in creds.splitlines() if ln.startswith("`")]
    key = lines[0].strip("`")
    token = lines[2].strip("`")
    return key, token

def get_github_token():
    return json.loads(GITHUB_SECRETS.read_text(encoding="utf-8"))["github_token"]

PRIORITY_KEYWORDS = {
    "P0": ["🚨", "alert", "blocked", "403", "502", "critical", "emergency", "security", "breach", "down", "outage"],
    "Top 10": ["freeze-dried production", "square developer", "payments live", "pos deployment", "website launch", "first sale", "confirm pat works"],
    "P1": ["launch", "deploy", "go live", "critical fix", "urgent", "asap", "this week", "must do", "blocking", "blocker"],
    "P2": ["build", "create", "implement", "integrate", "connect", "design", "write", "develop", "test", "verify", "fix", "update"],
    "P3": ["follow", "email", "graphics", "template", "content", "research", "review", "audit", "plan", "schedule", "track", "maintenance"],
    "P4": ["backlog", "later", "maybe", "park", "hold", "someday", "polish", "cleanup", "refactor"],
    "P5": ["assess", "evaluate", "validate", "check", "approval", "review needed", "get ", "confirm ", "verify "],
    "P6": ["blocked", "waiting", "dependency", "external", "waiting on", "blocked by"],
    "Future Ideas": ["future", "ai answering", "phone number", "sms", "research free", "voice ai receptionist", "ar menu preview", "q1 2027", "2027", "2028", "paid upgrade", "someday", "next year", "new year new", "halloween", "christmas"],
    "Sir Azure": ["sir azure", "sirazure", "nikto", "tshark", "yara", "squidstation", "security tools"],
    "Sir Green": ["sir green", "sirgreen", "docker", "dashboard", "api/", "build docker", "fleet", "swarm", "compose"],
}

def classify_alert(text: str) -> str:
    t = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(k in t for k in keywords):
            return priority
    return "P3"

def find_card_by_name(name: str, key=None, token=None):
    """Check if a card with the same name already exists (prevents duplication)."""
    if not key or not token:
        try:
            key, token = get_trello_credentials()
        except Exception:
            return None
    try:
        r = requests.get(
            f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
            params={"key": key, "token": token, "fields": "name,id,closed"},
            timeout=15,
        )
        if r.status_code == 200:
            for card in r.json():
                if not card.get("closed") and card.get("name") == name:
                    return card.get("id")
    except Exception:
        pass
    return None

def create_trello_card(title: str, body: str, classification: str):
    key, token = get_trello_credentials()
    board_id = BOARD_ID
    list_map = {
        "P0": "6a74cbd440270147ff04bd5b",
        "Top 10": "6a74cbd3aa052ed2b30c5644",
        "P1": "6a74cbd5e3d54d2d08be82e7",
        "P2": "6a74cbd4148f814483a64589",
        "P3": "6a70a32923622d3e00107d70",
        "P4": "6a74cbd573259cffe8a23cc0",
        "P5": "6a70a3282e405a2460afc170",
        "P6": "6a74cbd67bbe3ef35a634495",
        "Future Ideas": "6a74cbd56a538340582a8897",
        "Sir Azure": "6a74cbd51b2662f6cdc37cce",
        "Sir Green": "6a74cbd679972be49ea46dae",
    }
    label_map = {
        "P0": "P0", "P1": "P1", "P2": "P2", "P3": "P3", "P4": "P4", "P5": "P5", "P6": "P6",
        "Top 10": "Top 10", "Future Ideas": "Future Ideas", "Sir Azure": "Sir Azure", "Sir Green": "Sir Green"
    }
    
    target_list = list_map.get(classification, list_map["P3"])
    
    r = requests.post(
        f"https://api.trello.com/1/cards",
        params={"key": key, "token": token, "idList": target_list, "name": title, "desc": f"Auto-generated from alert\n\n{body}"},
        timeout=15,
    )
    if r.status_code == 200:
        card_id = r.json().get("id")
        
        # Add priority label
        label_id = None
        labels = requests.get(
            f"https://api.trello.com/1/boards/{board_id}/labels",
            params={"key": key, "token": token, "fields": "id,name"},
            timeout=10,
        ).json()
        for l in labels:
            if l["name"] == classification:
                label_id = l["id"]
                break
        
        if label_id:
            requests.post(
                f"https://api.trello.com/1/cards/{card_id}/idLabels",
                params={"key": key, "token": token},
                data={"value": label_id},
                timeout=10,
            )
        
        return card_id
    return None

def create_github_issue(title: str, body: str, classification: str):
    token = get_github_token()
    repo = "toruscoffeecompany/Torus_Ops"
    
    label_map = {
        "P0": "P0", "P1": "P1", "P2": "P2", "P3": "P3", "P4": "P4", "P5": "P5", "P6": "P6",
        "Top 10": "Top 10", "Future Ideas": "Future Ideas", "Sir Azure": "Sir Azure", "Sir Green": "Sir Green"
    }
    
    payload = {
        "title": f"[ALERT] {title}",
        "body": f"Auto-generated from critical alert\n\n{body}\n\n---\nPriority: {classification}\nSource: inbox automation",
        "labels": [label_map.get(classification, "P3")]
    }
    
    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        json=payload,
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
        timeout=15,
    )
    if r.status_code == 201:
        return r.json().get("number")
    return None

def process_inbox():
    """Process inbox messages and create Trello/GitHub items."""
    inbox_dirs = [
        REPO_ROOT / "02_Business_Operations/Communications/Inbox",
        REPO_ROOT / "z/MISS_PINK_INBOX",
        REPO_ROOT / "z/SIR_GREEN_INBOX",
        REPO_ROOT / "z/SIR_AZURE_INBOX",
    ]
    
    log = {
        "processed_at": datetime.now().isoformat(),
        "processed": 0,
        "trello_created": 0,
        "github_created": 0,
        "errors": []
    }
    
    # Get Trello credentials once for duplicate checking
    try:
        key, token = get_trello_credentials()
    except Exception:
        key, token = None, None
    
    for inbox_dir in inbox_dirs:
        if not inbox_dir.exists():
            continue
        
        for msg_file in inbox_dir.glob("*.md"):
            try:
                text = msg_file.read_text(encoding="utf-8")
                title = msg_file.stem
                
                # CREW COORDINATION: Check if another crew member is processing this
                item_id = f"alert:{title}"
                if CREW_COORDINATION:
                    if is_claimed(item_id):
                        continue
                    if not claim_work_item(item_id, CREW_ID, f"Processing alert: {title[:100]}"):
                        continue
                
                # Extract classification
                classification = classify_alert(text)
                
                # Check for duplicate card by name before creating
                existing = find_card_by_name(title, key, token) if key and token else None
                if existing:
                    card_id = existing  # Use existing card ID instead of creating duplicate
                else:
                    # Create Trello card
                    card_id = create_trello_card(title, text[:500], classification)
                if card_id:
                    log["trello_created"] += 1
                
                # Create GitHub issue for P0/P1/Top 10
                if classification in ["P0", "P1", "Top 10"]:
                    issue_num = create_github_issue(title, text[:500], classification)
                    if issue_num:
                        log["github_created"] += 1
                
                log["processed"] += 1
                
                # RELEASE crew coordination claim
                if CREW_COORDINATION:
                    release_work_item(item_id)
            except Exception as e:
                log["errors"].append(f"{msg_file.name}: {str(e)}")
                if CREW_COORDINATION:
                    release_work_item(item_id)
    
    ALERT_LOG.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Alert processing complete: {log['processed']} processed, {log['trello_created']} Trello cards, {log['github_created']} GitHub issues")
    return log

if __name__ == "__main__":
    process_inbox()
