#!/usr/bin/env python3
"""
Miss Pink Hermes Bridge Watcher — monitors Discord messages → Hermes → responses

Runs as background daemon on PINKCADY.
- Monitors: miss_pink_bot/inbox/ for new message files
- When new message arrives → triggers Hermes processing
- Reads Hermes responses from: miss_pink_bot/outbox/
- Bot picks up responses via file monitoring

Usage:
  pythonw.exe miss_pink_bridge_watcher.py  (no terminal window)
"""

import json
import os
import time
import sys
from pathlib import Path
from datetime import datetime, timezone

# ─══ Configuration ─────────────────────────────────────────────────────────
VAULT = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
BOT_DIR = VAULT / "02_Business_Operations" / "Communications" / "Discord" / "miss_pink_bot"
INBOX = BOT_DIR / "inbox"
OUTBOX = BOT_DIR / "outbox"
STATE_FILE = BOT_DIR / "bridge_state.json"

# ─══ Create directories ──────────────────────────────────────────────────────
INBOX.mkdir(parents=True, exist_ok=True)
OUTBOX.mkdir(parents=True, exist_ok=True)

# ─══ State tracking ─────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"processed_messages": [], "last_check": None}

def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass

def mark_processed(msg_id):
    state = load_state()
    state["processed_messages"].append(msg_id)
    state["processed_messages"] = state["processed_messages"][-100:]  # ─══ Keep last 100
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

def is_processed(msg_id):
    state = load_state()
    return msg_id in state.get("processed_messages", [])

# ─══ Message processing ──────────────────────────────────────────────────────
def process_discord_message(msg_file):
    """Read message from Discord, trigger Hermes workflow."""
    try:
        data = json.loads(msg_file.read_text())
        msg_id = data["id"]
        author = data["author"]
        content = data["content"]
        author_id = data["author_id"]
        
        print(f"[BRIDGE] New message from {author}: {content[:80]}")
        
        # ─══ TODO: This is where Hermes processes the message ────────────────────────────────────
        # ─══ For now — write a placeholder response ─────────────────────────────────────────────────
        # ─══ Real implementation will call Hermes tools (Trello, etc.) ─────────────────────────────────────
        
        response = (
            f"Aye, Captain! Brewbeard Ledgerbane at your service. 📡\n"
            f"Received your message: '{content[:50]}'\n"
            f"I've logged this to the Torus Coffee ops vault.\n"
            f"Processing queue active — stand by for results."
        )
        
        # ─══ Write response to outbox ─────────────────────────────────────────────────────────────
        resp_file = OUTBOX / f"resp_{msg_id}_{int(time.time())}.json"
        resp_data = {
            "author_id": author_id,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_msg_id": msg_id,
            "status": "ready"
        }
        resp_file.write_text(json.dumps(resp_data, indent=2))
        print(f"[BRIDGE] Response written to outbox: {resp_file.name}")
        
        mark_processed(msg_id)
        return True
        
    except Exception as e:
        print(f"[BRIDGE] Error processing {msg_file.name}: {e}")
        return False

# ─══ Main watcher loop ───────────────────────────────────────────────────────
def main():
    print(f"[BRIDGE] Hermes watcher started")
    print(f"[BRIDGE] Monitoring: {INBOX}")
    print(f"[BRIDGE] Outbox: {OUTBOX}")
    print(f"[BRIDGE] State: {STATE_FILE}")
    
    state = load_state()
    already_processed = set(state.get("processed_messages", []))
    
    # ─══ Process any existing unprocessed messages ─────────────────────────────────────────────
    for msg_file in sorted(INBOX.glob("msg_*.json")):
        if msg_file.stem.replace("msg_", "") not in already_processed:
            print(f"[BRIDGE] Found unprocessed: {msg_file.name}")
            process_discord_message(msg_file)
    
    # ─══ Continuous monitoring loop ─────────────────────────────────────────────────────────────
    print(f"\n[BRIDGE] Entering watch loop (polling every 2 seconds)")
    poll_interval = int(os.environ.get("BRIDGE_POLL_INTERVAL", "2"))
    
    while True:
        try:
            state = load_state()
            already_processed = set(state.get("processed_messages", []))
            
            # ─══ Check for new messages ─────────────────────────────────────────────────────────
            for msg_file in sorted(INBOX.glob("msg_*.json")):
                msg_id = msg_file.stem.replace("msg_", "")
                if msg_id not in already_processed:
                    process_discord_message(msg_file)
            
            # ─══ Optional: cleanup old inbox files ─────────────────────────────────────────────
            now = time.time()
            for old_file in INBOX.glob("msg_*.json"):
                if now - old_file.stat().st_mtime > 86400:  # ─══ 24 hours old
                    old_file.unlink()
                    print(f"[BRIDGE] Cleaned old message: {old_file.name}")
            
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            print(f"\n[BRIDGE] Watcher stopped by user")
            break
        except Exception as e:
            print(f"[BRIDGE] Loop error: {e}")
            time.sleep(5)  # ─══ Back off on errors

if __name__ == "__main__":
    main()
