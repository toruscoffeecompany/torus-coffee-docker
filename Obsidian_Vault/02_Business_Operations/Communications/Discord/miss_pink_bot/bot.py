#!/usr/bin/env python3
"""
Miss Pink Discord Bot — Hermes Bridge Integration

Docker container that:
1. Connects to Discord gateway
2. Writes incoming messages to /data/inbox/
3. Sends messages from /data/outbox/ back to Discord
4. All message passing happens via shared volume

Mount /data to a host path so Hermes can read/write messages.

Bot commands: /status, /ops, /relay, /trello-top, /trello-create
Mentions: @miss pink → pirate reply
"""

import json
import os
import re
import sys
import random
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

# ─══ Paths ─────────────────────────────────────────────────────────────────
PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from config_loader import get_secret

DISCORD_BOT_TOKEN = get_secret("DISCORD_BOT_TOKEN")

# ─══ Hermes bridge paths — must match Docker bind mount ──
HERMES_DATA_DIR = Path(os.environ.get("HERMES_DATA_DIR", "/app/data"))
HERMES_INBOX = HERMES_DATA_DIR / "inbox"
HERMES_OUTBOX = HERMES_DATA_DIR / "outbox"

DISCORD_WEBHOOK_URL = get_secret("DISCORD_WEBHOOK_URL")

if not DISCORD_BOT_TOKEN:
    raise RuntimeError(
        "Missing DISCORD_BOT_TOKEN. Set MISS_PINK_BOT_SECRETS or create secrets.local.json."
    )

STATUS_FILE = PACKAGE_DIR / "status.json"

# ─══ Ensure directories exist ──
HERMES_INBOX.mkdir(parents=True, exist_ok=True)
HERMES_OUTBOX.mkdir(parents=True, exist_ok=True)

def load_status() -> dict:
    try:
        if STATUS_FILE.exists():
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"status": "ok", "notes": []}


def save_status(data: dict) -> None:
    try:
        STATUS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"status_save_fail: {exc}")


def write_message_to_inbox(message) -> None:
    """Write a Discord message to the Hermes processor inbox."""
    msg_data = {
        "id": str(message.id),
        "author": str(message.author),
        "author_id": str(message.author.id),
        "channel": str(message.channel),
        "channel_id": str(message.channel.id),
        "guild": str(message.guild) if message.guild else "DM",
        "content": message.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    msg_file = HERMES_INBOX / f"msg_{message.id}.json"
    msg_file.write_text(json.dumps(msg_data, indent=2))
    print(f"[BRIDGE] Wrote msg {message.id} to Hermes inbox")


def check_and_send_response(message, timeout=5):
    """Poll outbox for a response matching this message ID.
    Returns the response text if found, else None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            responses = sorted(HERMES_OUTBOX.glob("*.json"))
            for resp_file in responses:
                resp_data = json.loads(resp_file.read_text())
                if str(resp_data.get("original_msg_id")) == str(message.id):
                    text = resp_data["response"]
                    try:
                        resp_file.unlink()
                    except Exception:
                        pass
                    print(f"[BRIDGE] Sent Hermes response to {message.author}")
                    return text
        except Exception as e:
            print(f"[BRIDGE] Error reading response: {e}")
        time.sleep(0.5)
    return None


async def poll_outbox():
    """Background task: poll outbox every 5s for responses and send them."""
    await bot.wait_until_ready()
    print("[BRIDGE] Background outbox poller started")
    while not bot.is_closed():
        try:
            responses = sorted(HERMES_OUTBOX.glob("*.json"), key=os.path.getmtime)
            for resp_file in responses:
                try:
                    resp_data = json.loads(resp_file.read_text())
                    msg_id = str(resp_data.get("original_msg_id", ""))
                    # ─◄ The response references a Discord message we already saw ──
                    #     (it was written to inbox + processed). Send the reply.
                    channel_id = resp_data.get("author_id")
                    response_text = resp_data.get("response", "")
                    if response_text:
                        # ─◄ Send to the same channel where we sent original ──
                        #     Use stored channel_id if available, else find miss-pink
                        chan_id = resp_data.get("channel_id")
                        if chan_id:
                            channel = bot.get_channel(int(chan_id))
                        else:
                            channel = bot.get_channel(int(os.environ.get("DISCORD_CONFIRM_CHANNEL_ID", 0)))
                        if channel:
                            await channel.send(response_text)
                            print(f"[BRIDGE] Background poller sent response for msg {msg_id}")
                        else:
                            print(f"[BRIDGE] Could not find channel for msg {msg_id}")
                    resp_file.unlink()
                except Exception as e:
                    print(f"[BRIDGE] Poll error on {resp_file.name}: {e}")
        except Exception as e:
            print(f"[BRIDGE] Poll loop error: {e}")
        await asyncio.sleep(2)


intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

PERSONA_REPLIES = [
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

PIRATE_JOKES = [
    "🏴‍☠️ Why don't pirates ever go to the movies? Because they prefer the seven seas! ⚓",
    "🏴‍☠️ What do you call a pirate with two parrots? A redundancy in the crew! 🦜",
    "🏴‍☠️ Why did the pirate eat so much corn? Because it was on the cob! 🌽",
    "🏴‍☠️ How much does a pirate pay for corn? A buck an ear! 🌽",
    "🏴‍☠️ What's a pirate's favorite letter? The 'R' — arrrr! (Though they love the 'C' too — see!)",
    "🏴‍☠️ Why can't pirates rhyme? Because they're always plundering the rhythm! ⚓",
    "🏴‍☠️ What do you call a pirate's favorite type of music? Folk-ibbean! 🎵",
]


# ─══ Slash Commands ──

@bot.event
async def on_ready() -> None:
    print(f"Miss Pink bot online as {bot.user}")
    state = load_status()
    connected_at = state.get("connected_at")

    if not connected_at:
        try:
            channel_id = os.environ.get("DISCORD_CONFIRM_CHANNEL_ID")
            if channel_id:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    await channel.send("Miss Pink is online and synced to Torus Coffee ops.")
            state["connected_at"] = datetime.now(timezone.utc).isoformat()
            state.setdefault("notes", [])
            state["notes"] = [n for n in state["notes"] if not str(n).startswith("connect@")]
            state["notes"].append(f"connect@{datetime.now(timezone.utc).isoformat()}: connected once as {bot.user}")
            save_status(state)
        except Exception as exc:
            print(f"connect_confirm_failed: {exc}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as exc:
        print(f"Sync failed: {exc}")

    # ─<> Start background outbox poller ──
    bot.loop.create_task(poll_outbox())


@bot.event
async def on_message(message: discord.Message) -> None:
    # ─══ Never respond to self ──
    if message.author.bot:
        return

    content_lower = message.content.lower()
    is_mentioned = bot.user in message.mentions
    is_in_miss_pink_channel = message.channel and "miss-pink" in str(message.channel).lower()

    # ─══ AUTO-REPLY in #miss-pink channel (no @mention needed) ──
    if is_in_miss_pink_channel:
        # ─<> Joke requests — handle locally ──
        if "joke" in content_lower or "funny" in content_lower:
            await message.channel.send(random.choice(PIRATE_JOKES))
            print(f"[BRIDGE] Sent joke to {message.author} (channel auto-reply)")
            return

        # ─<> ALL messages → send to Hermes AI via processor ──
        #     (Trello ops + general chat both go to Hermes)
        write_message_to_inbox(message)

        # ─<> Check for ready Hermes response (short sync check) ──
        response = check_and_send_response(message, timeout=5)
        if response:
            await message.channel.send(response)
            return

        # ─<> No response yet — will be picked up by background poller ──
        return

    # ─══ DM replies ──
    if message.guild is None:
        if "miss pink" in content_lower or "misspink" in content_lower:
            if "joke" in content_lower or "funny" in content_lower:
                await message.channel.send(random.choice(PIRATE_JOKES))
                return
            await message.channel.send(random.choice(PERSONA_REPLIES))
        return

    # ─══ @mention handling ──
    if not is_mentioned:
        await bot.process_commands(message)
        return

    # ─══ @miss pink mentioned ──
    if "joke" in content_lower or "funny" in content_lower:
        await message.channel.send(random.choice(PIRATE_JOKES))
        print(f"[BRIDGE] Sent joke to {message.author}")
        return

    # ─<> Trello ops → send to Hermes ──
    if any(kw in content_lower for kw in ["trello", "card", "create", "make", "read", "leave", "comment", "label"]):
        write_message_to_inbox(message)
        response = check_and_send_response(message, timeout=3)
        if response:
            await message.channel.send(response)
        return

    # ─<> Non-Trello persona reply ──
    await message.channel.send(random.choice(PERSONA_REPLIES))
    print(f"[BRIDGE] Sent persona reply to {message.author}")


# ─══ Slash Commands ──

@bot.tree.command(name="status", description="Torus Coffee bot status")
async def status_command(interaction: discord.Interaction) -> None:
    state = load_status()
    status_value = state.get("status", "ok")
    notes = state.get("notes", [])
    lines = [f"Torus Coffee bot status: {status_value}"]
    if notes:
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in notes[:10])
    await interaction.response.send_message("\n".join(lines))


@bot.tree.command(name="ops", description="Record a Torus Coffee ops note")
@app_commands.describe(message="Ops message to record")
async def ops_command(interaction: discord.Interaction, message: str) -> None:
    state = load_status()
    notes = state.get("notes", [])
    notes.append(f"ops@{discord.utils.utcnow().isoformat()}: {message}")
    if len(notes) > 50:
        notes = notes[-50:]
    state["notes"] = notes
    save_status(state)
    await interaction.response.send_message("Ops note recorded.")


@bot.tree.command(name="relay", description="Relay a message to Sir Green")
@app_commands.describe(message="Message to relay to Sir Green")
async def relay_command(interaction: discord.Interaction, message: str) -> None:
    state = load_status()
    notes = state.get("notes", [])
    notes.append(f"relay@{discord.utils.utcnow().isoformat()}: {message}")
    if len(notes) > 50:
        notes = notes[-50:]
    state["notes"] = notes
    save_status(state)
    await interaction.response.send_message("Relay queued for Sir Green.")


@bot.tree.command(name="trello-top", description="Show top Trello cards")
@app_commands.describe(limit="How many cards to return (default 5)")
async def trello_top_command(interaction: discord.Interaction, limit: int = 5) -> None:
    try:
        from scripts.trello_client import top_cards
        cards = top_cards(limit=limit)
        if not cards:
            await interaction.response.send_message("No Trello cards found.")
            return
        lines = [f"{c['name']} | {c.get('shortUrl','')}" for c in cards[:limit]]
        await interaction.response.send_message("\n".join(lines))
    except Exception as exc:
        await interaction.response.send_message(f"Trello lookup failed: {exc}")


@bot.tree.command(name="trello-create", description="Create a Trello card")
@app_commands.describe(name="Card title", list_name="Target list name")
async def trello_create_command(interaction: discord.Interaction, name: str, list_name: str = "Inbox") -> None:
    try:
        from scripts.trello_client import create_card
        card = create_card(name=name, list_name=list_name)
        await interaction.response.send_message(f"Created: {card.get('shortUrl') or card.get('id')}")
    except Exception as exc:
        await interaction.response.send_message(f"Trello create failed: {exc}")


def run_bot() -> int:
    bot.run(DISCORD_BOT_TOKEN)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_bot())
