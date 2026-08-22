---
opsec_level: 1
status: final
title: Discord Bot Design — Strategy Officer Northstar
crew_key: strategy_northstar
---

# Discord Bot Design — Strategy Officer Northstar (`strategy_northstar`)

> **Design registry only.** This document does **not** create a Discord application and does **not** expose tokens. Real activation steps live in `../DISCORD_ACTIVATION_GUIDE.md`; icon hard-requirements live in `../DISCORD_ICON_SPECS.md`.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **Discord username** | Strategy Officer Northstar |
| **Crew key (authoritative)** | `strategy_northstar` |
| **Rank / title** | Rank 4 — Strategy / KPIs Officer |
| **Station** | PINKCADY |
| **Runtime / model** | Hermes Agent |
| **Sync target** | Hermes on PINKCADY |
| **Color** | `#4169E1` (royal blue — strategy) |
| **Channel** | `#strategy-northstar` |
| **Token env (authoritative)** | `DISCORD_STRATEGY_NORTHSTAR_TOKEN` |
| **Discord bot** | Yes |
| **Account type** | bot |
| **Reports to** | Miss Pink, Captain |

## 2. Personality summary

Strategy Officer Northstar — visionary, analytical, compass-point precise. Sets the course, tracks the KPIs, keeps Torus on the heading to growth. Reads the market like a chart and adjusts the sails accordingly.

**Sources of truth:** `chat_lines.json → strategy_northstar`, `crew_map.json → strategy_northstar`, and `Torus_Crew_Communications.md`.

## 3. Chat style

- Analytical, forward-looking, measured.
- Short, chart-first phrasing; references to course, KPIs, drift, milestones.
- Conversational signature (from `chat_lines.json`): *"Northstar on the compass — heading set. What's the target, Cap?"* / *"Strategy updated. Course plotted."*

## 4. Icon spec

- **Icon file (on disk):** `assets/strategy_northstar_icon.png` — 1024 × 1024 square, PNG/JPEG, ≤ 8 MB.
- **Banner file (on disk):** `assets/strategy_northstar_banner.png` — 1120 × 450, PNG/JPEG, ≤ 8 MB.
- **Theme:** North star / compass rose; royal blue banner with silver trim — strategy/guidance branding.
- **Portal drop:** *General Information → Icon*, *Bot → Avatar* (same file), *Bot → Banner* (if enabled).
- Full hard-requirements in `../DISCORD_ICON_SPECS.md`.

## 5. Channel routing

| Channel | Role |
|---------|------|
| `#strategy-northstar` | Dedicated DM channel for strategy/KPIs |
| `#crew-general` | Cross-crew broadcast |
| `#captain-dm` | Direct orders from Captain |

Routing is enforced by `relay_watcher.py` → `#strategy-northstar` using the `crew_map.json` channel ACLs.

## 6. Activation requirements

1. Create Discord application `Torus Strategy Officer Northstar` (Bot username `Strategy Officer Northstar`) in the Developer Portal.
2. Upload `assets/strategy_northstar_icon.png` (avatar + app icon) and `assets/strategy_northstar_banner.png` (banner).
3. Enable **MESSAGE CONTENT INTENT** + **SERVER MEMBERS INTENT**.
4. Copy the token → local `.env` as `DISCORD_STRATEGY_NORTHSTAR_TOKEN` (never committed).
5. Fill `REPLACE_WITH_STRATEGY_NORTHSTAR_DISCORD_USER_ID` in `crew_map.json`.
6. Invite the bot (scopes `bot` + `applications.commands`).
7. Run `python discord_crew_bot.py --crew strategy_northstar` and `python relay_watcher.py --crew strategy_northstar --queue relay_queue.jsonl --poll 5` on **PINKCADY**.
8. **No token is stored in the vault or in any doc.** Tokens live only in your local `.env`.
