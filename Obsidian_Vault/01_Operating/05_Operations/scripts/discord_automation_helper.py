#!/usr/bin/env python3
"""Discord automation helper for Torus Coffee.

Uses local bot/webhook secrets from miss_pink_bot/secrets.local.json.
Does not require the discord.py runtime; uses HTTP webhooks + bot token REST.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
PACKAGE_DIR = Path(__file__).resolve().parent
SECRETS_LOCAL = VAULT / "02_Business_Operations/Communications/Discord/miss_pink_bot/secrets.local.json"


def load_secrets() -> dict:
    if SECRETS_LOCAL.exists():
        try:
            return json.loads(SECRETS_LOCAL.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


SECRETS = load_secrets()
DISCORD_BOT_TOKEN = SECRETS.get("DISCORD_BOT_TOKEN", "")
DISCORD_WEBHOOK_URL = SECRETS.get("DISCORD_WEBHOOK_URL", "")


def _headers() -> dict:
    return {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def post_webhook(message: str) -> bool:
    if not DISCORD_WEBHOOK_URL:
        return False
    try:
        r = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": message},
            timeout=20,
        )
        return r.status_code in (200, 204)
    except Exception:
        return False


def post_channel(channel_id: str, message: str) -> bool:
    if not channel_id or not DISCORD_BOT_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=_headers(),
            json={"content": message},
            timeout=20,
        )
        return r.status_code in (200, 201, 204)
    except Exception:
        return False


def get_channel(channel_id: str) -> dict:
    if not channel_id or not DISCORD_BOT_TOKEN:
        return {}
    try:
        r = requests.get(
            f"https://discord.com/api/v10/channels/{channel_id}",
            headers=_headers(),
            timeout=20,
        )
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def get_guild_channels(guild_id: str) -> list[dict]:
    if not guild_id or not DISCORD_BOT_TOKEN:
        return []
    try:
        r = requests.get(
            f"https://discord.com/api/v10/guilds/{guild_id}/channels",
            headers=_headers(),
            timeout=20,
        )
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def ooda_status_update(title: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    msg = f"[OODA {ts}] {title}"
    if not post_webhook(msg):
        # Best-effort channel post requires explicit channel IDs
        pass


def ticket_status_update(trello_card_id: str, title: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    msg = f"[SmartTicket {ts}] {title} | card={trello_card_id}"
    post_webhook(msg)


def alert(message: str, severity: str = "info") -> None:
    prefix = {
        "critical": "🚨",
        "warning": "⚠️",
        "info": "ℹ️",
        "debug": "🐛",
    }.get(severity, "ℹ️")
    post_webhook(f"{prefix} {message}")


def send_connect_confirm_once() -> None:
    state_path = SECRETS_LOCAL.with_name("discord_connect_state.json")
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    if state.get("connected"):
        return
    sent = False
    channel_id = os.environ.get("DISCORD_CONFIRM_CHANNEL_ID", "")
    if channel_id and DISCORD_BOT_TOKEN:
        sent = post_channel(channel_id, "Miss Pink is online and synced to Torus Coffee ops.")
    if not sent:
        post_webhook("Miss Pink is online and synced to Torus Coffee ops.")
    state["connected"] = True
    state["confirmed_at"] = datetime.now(timezone.utc).isoformat()
    try:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    print("webhook_present=", bool(DISCORD_WEBHOOK_URL))
    print("bot_token_present=", bool(DISCORD_BOT_TOKEN))
    alert("Miss Pink Discord automation helper online.", "info")
    try:
        send_connect_confirm_once()
    except Exception as exc:
        print("connect_confirm_failed:", exc)
