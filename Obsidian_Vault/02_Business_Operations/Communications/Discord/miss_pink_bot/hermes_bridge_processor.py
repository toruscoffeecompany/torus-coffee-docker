#!/usr/bin/env python3
"""
Hermes Bridge Message Processor — Runs on PINKCADY host (outside Docker)

Reads messages from Discord bot's inbox volume → processes with Hermes logic.
Writes responses to Discord bot's outbox volume → bot sends back to Discord.

This is the "brain" of the bot — where Hermes (you) actually reads + responds.

Architecture:
  Discord → [Docker: bot.py] → /data/inbox/msg_*.json → [Host: this script] → /data/outbox/resp_*.json → [Docker: bot.py] → Discord

Mount point: D:/Work/Torus Coffee Company LLC/Obsidian_Vault/02_Business_Operations/Communications/Discord/miss_pink_bot/
"""

import json
import os
import re
import time
import sys
import random
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ─══ Host paths (mirrors the Docker /data mount) ─────────────────────────────
BOT_DIR = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot")
DATA_DIR = BOT_DIR / "data"  # ─══ This maps to /data in Docker
INBOX = DATA_DIR / "inbox"
OUTBOX = DATA_DIR / "outbox"

# ─══ State tracking ───────────────────────────────────────────────────────────
STATE_FILE = DATA_DIR / "hermes_bridge_state.json"
PROCESSED_LOG = DATA_DIR / "hermes_processed.log"


# ─══ Unbuffered file writer for pythonw.exe ──
class _flushing_file:
    """File wrapper that auto-flushes on every write — critical for pythonw.exe logging."""
    def __init__(self, path, mode="a"):
        self.f = open(path, mode, encoding="utf-8")
    def write(self, data):
        self.f.write(data)
        self.f.flush()
        os.fsync(self.f.fileno())
    def flush(self):
        self.f.flush()
        os.fsync(self.f.fileno())
    def __getattr__(self, name):
        return getattr(self.f, name)

# ─══ Pirate persona ───────────────────────────────────────────────────────────
PIRATE_REPLIES = [
    "Aye, Captain — Miss Pink, standing by. 🏴‍☠️",
    "Roger that. Miss Pink be on watch. ⚓",
    "Message received. Keeping the vault tight and the ops tight. 🔐",
    "Copy. Proceeding with free-tier-first execution. 🆓",
    "Acknowledged. I'll log this and keep moving. 📝",
    "Shiver me timbers! What be ye needin', Captain? ⚓",
    "Aye aye, Captain! I be trackin' this in the vault. 📊",
    "Got it, boss! Miss Pink's on the case. 🧠",
    "Roger that, Cap'n. Miss Pink's got this. ⚓",
    "Copy that. I be loggin' it in the ops vault now. 📋",
]

# ─══ Trello integration ───────────────────────────────────────────────────────
try:
    sys.path.insert(0, str(BOT_DIR / "scripts"))
    from trello_client import top_cards, create_card, find_card_by_name, add_comment, add_label_to_card, read_card
    TRELLO_AVAILABLE = True
except Exception as e:
    print(f"[HERMES] Trello import error: {e}")
    TRELLO_AVAILABLE = False


def call_nous_cli(user_message, author="Captain"):
    """Send message to Hermes CLI (uses local auth) and get real AI response."""
    import shutil
    prompt = f"""You are Miss Pink, a pirate AI assistant for Torus Coffee Company.
The user ({author}) sent you this message from Discord. Reply as Miss Pink would —
pirate persona, cyberpunk aesthetic, direct and concise. Keep responses under 200 words.

User message: {user_message}

Miss Pink's response:"""
    try:
        hermes_cmd = shutil.which("hermes")
        r = subprocess.run(
            [hermes_cmd or "hermes", "chat", "-q", prompt, "--source", "discord"],
            capture_output=True, text=True, timeout=180,
            env={**os.environ, "PYTHONUNBUFFERED": "1", "HERMES_HOME": os.environ.get("HERMES_HOME", r"C:\Users\torus\AppData\Local\hermes")}
        )
        if r.returncode == 0 and r.stdout.strip():
            output = r.stdout
            # ─<> Strip ANSI escape codes (ESC + [ + numbers + m) ──
            ansi_re = re.compile(r'\x1b\[[0-9;]*m')
            clean = ansi_re.sub('', output)
            lines = clean.split('\n')
            
            # ─<> Response is between ╭─ box and ╰─ footer ──
            response_lines = []
            started = False
            for line in lines:
                if line.startswith('╭─'):
                    started = True
                    continue
                if not started:
                    continue
                if line.startswith('╰'):
                    break
                stripped = line.strip()
                if stripped and not stripped.startswith('Query:') and not stripped.startswith('Initializing') and not stripped.startswith('─') and not stripped.startswith('✕'):
                    response_lines.append(stripped)
            
            response = '\n'.join(response_lines).strip()
            if response:
                return response
            
            # ─◄ Fallback ──
            for line in reversed(lines):
                stripped = line.strip()
                if stripped and not line.startswith('╭') and not line.startswith('Query:') and not line.startswith('Initializing') and not line.startswith('─'):
                    return stripped
        else:
            print("[HERMES] CLI status: rc=" + str(r.returncode) + ", stderr=" + r.stderr[:100], flush=True)
    except subprocess.TimeoutExpired:
        print("[HERMES] CLI call timed out — message will be retried", flush=True)
    except Exception as e:
        print(f"[HERMES] CLI call failed: {e}", flush=True)
    return None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"processed": [], "uptime_start": datetime.now(timezone.utc).isoformat()}


def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def process_message(msg_path):
    """Process a Discord message and generate Hermes response."""
    try:
        data = json.loads(msg_path.read_text())
        msg_id = data["id"]
        author = data["author"]
        content = data["content"]
        author_id = str(data["author_id"])

        # ─══ Log the message ────────────────────────────────────────────────
        log_entry = f"[{datetime.now(timezone.utc).isoformat()}] MSG from {author} (id={msg_id}): {content}"
        print(log_entry)
        try:
            with open(PROCESSED_LOG, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

        # ─══ Command interpretation ────────────────────────────────────────────
        content_lower = content.lower()
        has_explicit_trello_card = ("trello" in content_lower and "card" in content_lower and any(a in content_lower for a in ["read", "creat", "mak", "add", "leave", "comment", "label"]))
        is_trello_read = has_explicit_trello_card and "read" in content_lower
        is_trello_comment = has_explicit_trello_card and ("leave" in content_lower or "comment" in content_lower)
        is_trello_label = has_explicit_trello_card and ("label" in content_lower or "miss pink" in content_lower)
        is_trello_create = ("trello" in content_lower and ("card" in content_lower or "new card" in content_lower) and any(a in content_lower for a in ["creat", "mak", "add"]) and not ("read" in content_lower and "leave" in content_lower))

        if is_trello_read or is_trello_comment or is_trello_label:
            if TRELLO_AVAILABLE:
                try:
                    import re
                    quoted = re.findall(r'"([^"]+)"', content)
                    if quoted:
                        card_name = quoted[0]
                    else:
                        card_name = content_lower
                        for prefix in ["i want you to read this trello card on the torus ops board, ",
                                       "i want you to read this trello card on the torus ops board,",
                                       "read this trello card on the torus ops board,",
                                       "read the trello card ", "read trello card "]:
                            if prefix in card_name:
                                card_name = card_name.replace(prefix, "")
                                break
                        card_name = card_name.replace("read this trello card", "").strip()
                    card_name = card_name.title()[:80] if card_name else "Test"

                    matches = find_card_by_name(card_name)
                    if matches:
                        card = matches[0]
                        actions = [f"Read Trello card: {card['name']}"]

                        full = read_card(card['id'])
                        actions.append(f"Name: {full.get('name','?')}")
                        actions.append(f"URL: {full.get('shortUrl', card.get('shortUrl','?'))}")
                        if full.get('desc'):
                            actions.append(f"Desc: {full['desc'][:120]}")

                        if is_trello_comment:
                            comment_text = [
                                "🏴‍☠️ Captain's orders verified! Miss Pink spied this card through the spyglass and stamped her mark. No ghost pirates lurking here — all clear for sailing the seven servers! ⚓🗺️",
                                "🔍 Miss Pink be checkin' this card like a proper pirate checks for scurvy crew. All hands accounted for, Captain! 🏴‍☠️",
                                "📬 Ahoy Captain! Miss Pink's crew mark is stamped on this card. Verified end-to-end through the Discord → Hermes → Trello bridge. Smooth sailin'! ⚓",
                            ]
                            comment_text = random.choice(comment_text)
                            comment_text += f"\n\n📬 Processed via Discord → Hermes bridge at {datetime.now(timezone.utc).isoformat()}"
                            add_comment(card['id'], comment_text)
                            actions.append(f"Pirate verification comment added ✅")

                        if is_trello_label or "miss pink" in content_lower:
                            add_label_to_card(card['id'], "miss-pink")
                            actions.append(f"miss-pink label added ✅")

                        response = "🏴‍☠️ " + "\n  • ".join(actions)
                    else:
                        response = f"⚓ Could not find card matching '{card_name}'"
                except Exception as e:
                    response = f"Trello read failed: {e}. ⚓"
            else:
                response = "Trello not configured but I be tryin'! ⚓"
        elif is_trello_create:
            if TRELLO_AVAILABLE:
                try:
                    import re
                    card_title = "Test card from Discord"
                    clean = re.sub(r'^(make\s+a\s*|make\s+|create\s+a\s*|create\s+|add\s+a\s+|add\s+)', '', content_lower)
                    for sep in [" on ", " in "]:
                        if sep in clean:
                            clean = clean.split(sep)[0]
                    clean = re.sub(r'\s+trello\s+card\s*$', '', clean)
                    clean = re.sub(r'\s+card\s*$', '', clean)
                    clean = clean.strip()
                    if clean and len(clean) > 2:
                        card_title = clean.title()

                    card = create_card(name=card_title, list_name="Top 10 — Focus Fleet")
                    response = f"Aye Captain! Trello card created:\n  • Name: {card.get('name', '???')}\n  • URL: {card.get('shortUrl', '???')}\n  • Status: CREATED ✅"
                except Exception as e:
                    response = f"Trello create failed: {e}. But I be still here, Cap'n ⚓"
            else:
                response = "Trello not configured but I be tryin'! ⚓"
        elif "trello" in content_lower and ("list" in content_lower or "show" in content_lower or "what" in content_lower):
            if TRELLO_AVAILABLE:
                try:
                    cards = top_cards(limit=3)
                    if cards:
                        lines = ["🏴‍☠️ Top Trello cards:"]
                        lines.extend([f"  • {c['name']} — {c.get('shortUrl','')}"
                                      for c in cards[:3]])
                        response = "\n".join(lines)
                    else:
                        response = random.choice(PIRATE_REPLIES) + " No Trello cards found."
                except Exception as e:
                    response = f"Trello fetch failed: {e}. ⚓"
            else:
                response = random.choice(PIRATE_REPLIES)
        elif "status" in content_lower or "/status" in content:
            response = random.choice(PIRATE_REPLIES)
        elif "ops" in content_lower:
            response = "Roger Captain! I be loggin' that ops note in the vault. 📊"
        elif "relay" in content_lower:
            response = "Copy that — relay message queued for Sir Green. 🔄"
        else:
            # ─══ Try real AI response via Hermes CLI ──
            ai_response = call_nous_cli(content, author)
            if ai_response:
                response = f"🏴‍☠️ {ai_response}"
            else:
                response = "⚓ " + random.choice(PIRATE_REPLIES) + " (AI unavailable, Captain — try again in a bit ⚓)"

        # ─══ Write response to outbox ────────────────────────────────────────
        resp_data = {
            "author_id": author_id,
            "channel_id": str(data.get("channel_id", "")),
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_msg_id": msg_id,
            "status": "ready"
        }
        resp_file = OUTBOX / f"resp_{msg_id}_{int(time.time())}.json"
        resp_file.write_text(json.dumps(resp_data, indent=2))
        print(f"[HERMES] Response written: {resp_file.name}")

        return True

    except Exception as e:
        print(f"[HERMES] ERROR processing {msg_path.name}: {e}")
        return False


def main():
    # ─══ Ensure file logging (pythonw has no console) ──
    import logging
    log_path = DATA_DIR / "hermes_runtime.log"
    # ─◄ Unbuffered mode — pythonw.exe needs explicit flushing ──
    open(log_path, "a").write("")
    sys.stdout = _flushing_file(log_path)
    sys.stderr = sys.stdout
    
    print("[HERMES] Bridge processor starting...", flush=True)
    print("[HERMES] Inbox: " + str(INBOX), flush=True)
    print("[HERMES] Outbox: " + str(OUTBOX), flush=True)

    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)

    state = load_state()
    processed = set(state.get("processed", []))

    # ─══ Process any existing messages ────────────────────────────────────────
    for msg_file in sorted(INBOX.glob("msg_*.json")):
        msg_id = msg_file.stem.replace("msg_", "")
        if msg_id not in processed:
            process_message(msg_file)
            processed.add(msg_id)
            try:
                msg_file.unlink()
            except Exception:
                pass

    state["processed"] = list(processed)[-100:]
    save_state(state)

    # ─══ Continuous monitoring loop ───────────────────────────────────────────
    print("[HERMES] Entering watch loop (poll every 2 seconds)")
    poll_interval = int(os.environ.get("BRIDGE_POLL_INTERVAL", "2"))

    while True:
        try:
            for msg_file in sorted(INBOX.glob("msg_*.json")):
                msg_id = msg_file.stem.replace("msg_", "")
                if msg_id not in processed:
                    process_message(msg_file)
                    processed.add(msg_id)
                    try:
                        msg_file.unlink()
                    except Exception:
                        pass

            state["processed"] = list(processed)[-100:]
            state["last_check"] = datetime.now(timezone.utc).isoformat()
            save_state(state)

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("[HERMES] Stopped by user")
            break
        except Exception as e:
            print(f"[HERMES] Loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
