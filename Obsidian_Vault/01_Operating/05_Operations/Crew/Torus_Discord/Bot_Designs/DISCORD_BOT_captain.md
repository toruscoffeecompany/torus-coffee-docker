---
opsec_level: 1
status: final
title: Discord Bot Design — Captain Brewbeard Ledgerbane
crew_key: captain
---

# Discord Bot Design — Captain Brewbeard Ledgerbane (`captain`)

> **Design registry only.** This document does **not** create a Discord application and does **not** expose tokens. Real activation steps live in `../DISCORD_ACTIVATION_GUIDE.md`; icon hard-requirements live in `../DISCORD_ICON_SPECS.md`.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **Discord username** | Captain Brewbeard Ledgerbane |
| **Crew key (authoritative)** | `captain` |
| **Rank / title** | Rank 0 — Captain / Final Authority |
| **Station** | PINKCADY |
| **Runtime / model** | Hermes Agent (human account — no bot) |
| **Sync target** | Hermes on PINKCADY |
| **Color** | `#8B4513` (saddle brown — captaincy) |
| **Channel** | `#captain-dm` |
| **Discord bot** | No (human) |
| **Account type** | human |

## 2. Personality summary

Captain of Torus Coffee Company — final authority, plain-spoken, decisive. Leads the crew with strategic vision and expects execution. Speaks in orders, not suggestions. Warmth shows through action, not words.

**Sources of truth:** `Torus_Crew_Communications.md`, `MISS_PINK_ASTRO_PROFILE.md`, `chat_lines.json → captain`, and `crew_map.json → captain`.

## 3. Chat style

- Command, brevity, warmth-under-steel.
- Short, status-first phrasing; no walls of text.
- Conversational signature (from `chat_lines.json`): *"Captain. Status?"* / *"Good. Carry on."*

## 4. Icon spec

- **No bot icon required.** The Captain is a human Discord user.
- **Channel:** `#captain-dm` for direct orders.

## 5. Channel routing

| Channel | Role |
|---------|------|
| `#captain-dm` | Direct orders from Captain |
| `#crew-general` | Cross-crew broadcast |

## 6. Activation requirements

1. Captain is a human Discord user — no bot application needed.
2. Ensure Captain has access to `#captain-dm` and `#crew-general`.
3. Fill `REPLACE_WITH_CAPTAIN_DISCORD_USER_ID` in `crew_map.json` so DMs resolve.
4. All bot tokens stored locally in `.env` (never committed).
