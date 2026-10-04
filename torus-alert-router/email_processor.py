#!/usr/bin/env python3
"""IMAP Email Processor for toruscoffeecompany@gmail.com

Reads emails from Gmail IMAP → writes structured data to vault.
Runs via pythonw.exe (invisible background).

Architecture:
  Gmail IMAP → [pythonw: email_processor.py] → /vault/03_Communications/Inbox/
  Config: config/gmail.json (username + app_password from secrets.local.json)
"""

import imaplib
import email
import json
import os
import ssl
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─══ Paths ──
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "gmail.json"
SECRETS_FILE = BASE_DIR.parent.parent / "miss_pink_bot" / "secrets.local.json"
OUTPUT_DIR = BASE_DIR / "processed_emails"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─══ IMAP settings ──
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
CHECK_INTERVAL = 60  # seconds


def load_config():
    """Load Gmail config + secrets."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def load_secrets():
    """Load Discord app password from secrets file."""
    if SECRETS_FILE.exists():
        secrets = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        return secrets.get("GMAIL_APP_PASSWORD", "")
    return os.environ.get("GMAIL_APP_PASSWORD", "")


def connect_imap(username, app_password):
    """Connect to Gmail IMAP."""
    context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=context)
    mail.login(username, app_password)
    return mail


def process_unread_emails():
    """Check for unread emails and process them."""
    config = load_config()
    username = config.get("username", "toruscoffeecompany@gmail.com")
    app_password = load_secrets()

    if not app_password:
        print("No Gmail app password configured — skipping IMAP check")
        return

    try:
        mail = connect_imap(username, app_password)
        mail.select("INBOX")

        # ─◄ Search for unread ──
        status, messages = mail.search(None, "(UNSEEN)")
        email_ids = messages[0].split()

        if not email_ids:
            print("[EMAIL] No unread emails")
            return

        for eid in email_ids:
            try:
                status, msg_data = mail.fetch(eid, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        process_single_email(msg, mail, eid)
            except Exception as e:
                print(f"[EMAIL] Error processing email {eid}: {e}")

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"[EMAIL] IMAP error: {e}")


def process_single_email(msg, mail, eid):
    """Process a single email — extract data, write to vault."""
    subject = msg["subject"] or "(no subject)"
    sender = msg["from"] or "(unknown)"
    date_str = msg["date"] or "(unknown)"

    # ─◄ Extract body ──
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="replace") if msg.get_payload(decode=True) else ""

    # ─◄ Save email ──
    email_data = {
        "subject": subject,
        "from": sender,
        "date": date_str,
        "body": body[:2000],  # ─◄ truncated
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    filename = f"email_{int(time.time())}_{str(eid).strip()}.json"
    output_file = OUTPUT_DIR / filename
    output_file.write_text(json.dumps(email_data, indent=2), encoding="utf-8")
    print(f"[EMAIL] Saved: {subject[:60][:60]} → {filename}")

    # ─◄ Mark as read ──
    mail.store(eid, "+FLAGS", "\\Seen")


def main():
    print("[EMAIL] IMAP processor starting...")
    print(f"[EMAIL] Config: {CONFIG_FILE}")
    print(f"[EMAIL] Output: {OUTPUT_DIR}")

    while True:
        try:
            process_unread_emails()
        except Exception as e:
            print(f"[EMAIL] Loop error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
