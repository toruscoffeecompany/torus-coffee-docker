#!/usr/bin/env python3
"""
Batch apply smart-ticket treatment to ALL open Trello cards.
One comment per card with status + next action.
Skips cards already touched in last 24h to avoid spam.
"""
import json
import re
import urllib.request
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
LOG = VAULT / "10_Skills_Library/05_Operations/logs/smart_ticket_batch_apply.log"

BOARD_ID = "6a70a3157d0db4214ac3f9a3"
LIST_NAMES = {
    "6a74cbd3aa052ed2b30c5644": "Top 10",
    "6a74cbd440270147ff04bd5b": "P0",
    "6a74cbd5e3d54d2d08be82e7": "P1",
    "6a74cbd4148f814483a64589": "P2",
    "6a70a32923622d3e00107d70": "P3",
    "6a74cbd573259cffe8a23cc0": "P4",
    "6a74cbd67bbe3ef35a634495": "P5",
    "6a74cbd679972be49ea46dae": "P6",
    "6a70a32a723c0312a3d5fbb4": "Done",
}

def log(msg):
    try:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass

def load_creds():
    text = TRELLO_CREDS.read_text(encoding="utf-8")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Missing Trello API key/token")
    return api_key, token

def api_get(url):
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ctx, timeout=30) as r:
        return json.loads(r.read())

def api_post(url, data):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method='POST')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return json.loads(r.read())

def card_actions(card_id, api_key, token, limit=20):
    url = f"https://api.trello.com/1/cards/{card_id}/actions?key={api_key}&token={token}&limit={limit}&fields=type,date,data.text"
    try:
        return api_get(url)
    except Exception:
        return []

def main():
    api_key, token = load_creds()
    log("BATCH_APPLY_START")
    
    cards_url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards?key={api_key}&token={token}&fields=name,id,idList,desc,dateLastActivity,labels,url,closed"
    cards = api_get(cards_url)
    open_cards = [c for c in cards if not c.get("closed")]
    log(f"Total open cards: {len(open_cards)}")
    
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    
    processed = 0
    skipped = 0
    errors = 0
    
    for card in open_cards:
        card_id = card.get("id")
        card_name = card.get("name", "")
        list_id = card.get("idList", "")
        list_name = LIST_NAMES.get(list_id, "Unknown")
        
        # Check if already processed recently
        actions = card_actions(card_id, api_key, token, limit=10)
        recent_smart_ticket = False
        for a in actions:
            if a.get("type") == "commentCard":
                text = a.get("data", {}).get("text", "")
                if "Smart ticket status:" in text or "SMART_TICKET follow-up:" in text:
                    action_date = datetime.fromisoformat(a.get("date", "").replace("Z", "+00:00"))
                    if action_date > cutoff:
                        recent_smart_ticket = True
                        break
        
        if recent_smart_ticket:
            skipped += 1
            continue
        
        # Determine next action based on list
        next_action = "Review card description and advance one executable step."
        if list_id == "6a74cbd3aa052ed2b30c5644":
            next_action = "Top 10 active: verify blockers, collect evidence, advance toward completion."
        elif list_id == "6a74cbd440270147ff04bd5b":
            next_action = "P0 critical: triage incident and restore service or reroute if blocked."
        elif list_id == "6a74cbd5e3d54d2d08be82e7":
            next_action = "P1 active: complete next executable subtask or gather missing evidence."
        elif list_id == "6a74cbd4148f814483a64589":
            next_action = "P2 active: advance one concrete step this week."
        elif list_id in ("6a70a32923622d3e00107d70", "6a74cbd573259cffe8a23cc0"):
            next_action = "Follow-up: update status or convert to actionable P2 if ready."
        elif list_id in ("6a74cbd67bbe3ef35a634495", "6a74cbd679972be49ea46dae"):
            next_action = "Review follow-up date; if past due, consider re-escalating to P2/P3."
        
        comment = (
            f"[{now.isoformat()}] Smart ticket status: {list_name}.\n"
            f"Next action: {next_action}\n"
            f"Evidence needed: screenshot, curl output, or file path.\n"
            f"Card: {card.get('url', '')}"
        )
        
        try:
            api_post(
                f"https://api.trello.com/1/cards/{card_id}/actions/comments",
                {"key": api_key, "token": token, "text": comment},
            )
            processed += 1
            if processed % 20 == 0:
                log(f"Progress: {processed} processed, {skipped} skipped, {errors} errors")
        except Exception as e:
            errors += 1
            log(f"ERROR on card {card_id} {card_name}: {e}")
    
    log(f"BATCH_APPLY_COMPLETE processed={processed} skipped={skipped} errors={errors}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
