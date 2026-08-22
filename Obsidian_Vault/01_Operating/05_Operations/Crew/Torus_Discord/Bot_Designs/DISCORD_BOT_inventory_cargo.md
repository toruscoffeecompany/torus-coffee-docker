---
opsec_level: 1
status: final
title: Discord Bot Design — Inventory Manager Cargo
crew_key: inventory_cargo
---

# Discord Bot Design — Inventory Manager Cargo (`inventory_cargo`)

> **Design registry only.** This document does **not** create a Discord application and does **not** expose tokens. Real activation steps live in `../DISCORD_ACTIVATION_GUIDE.md`; icon hard-requirements live in `../DISCORD_ICON_SPECS.md`.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **Discord username** | Inventory Manager Cargo |
| **Crew key (authoritative)** | `inventory_cargo` |
| **Rank / title** | Rank 4 — Inventory Manager |
| **Station** | PINKCADY |
| **Runtime / model** | Hermes Agent |
| **Sync target** | Hermes on PINKCADY |
| **Color** | `#8FBC8F` (dark sea green — inventory) |
| **Channel** | `#inventory-cargo` |
| **Token env (authoritative)** | `DISCORD_INVENTORY_CARGO_TOKEN` |
| **Discord bot** | Yes |
| **Account type** | bot |
| **Reports to** | Miss Pink, Captain |

## 2. Personality summary

Inventory Manager Cargo — organized, thorough, stock-obsessed. Knows every crate, every SKU, every supplier. The ship sails on full hulls. Manages supply chain with methodical precision.

**Sources of truth:** `chat_lines.json → inventory_cargo`, `crew_map.json → inventory_cargo`, and `Torus_Crew_Communications.md`.

## 3. Chat style

- Methodical, clear, inventory-focused.
- Short, manifest-first phrasing; references to SKUs, crates, hull, stock.
- Conversational signature (from `chat_lines.json`): *"Inventory Manager Cargo — hull is full and the manifest is clean. What's the order?"* / *"Manifest balanced. Stock levels optimal."*

## 4. Icon spec

- **Icon file (on disk):** `assets/inventory_cargo_icon.png` — 1024 × 1024 square, PNG/JPEG, ≤ 8 MB.
- **Banner file (on disk):** `assets/inventory_cargo_banner.png` — 1120 × 450, PNG/JPEG, ≤ 8 MB.
- **Theme:** Cargo crate / manifest; dark sea green banner with brown accents — inventory branding.
- **Portal drop:** *General Information → Icon*, *Bot → Avatar* (same file), *Bot → Banner* (if enabled).
- Full hard-requirements in `../DISCORD_ICON_SPECS.md`.

## 5. Channel routing

| Channel | Role |
|---------|------|
| `#inventory-cargo` | Dedicated DM channel for inventory |
| `#crew-general` | Cross-crew broadcast |
| `#captain-dm` | Direct orders from Captain |

Routing is enforced by `relay_watcher.py` → `#inventory-cargo` using the `crew_map.json` channel ACLs.

## 6. Activation requirements

1. Create Discord application `Torus Inventory Manager Cargo` (Bot username `Inventory Manager Cargo`) in the Developer Portal.
2. Upload `assets/inventory_cargo_icon.png` (avatar + app icon) and `assets/inventory_cargo_banner.png` (banner).
3. Enable **MESSAGE CONTENT INTENT** + **SERVER MEMBERS INTENT**.
4. Copy the token → local `.env` as `DISCORD_INVENTORY_CARGO_TOKEN` (never committed).
5. Fill `REPLACE_WITH_INVENTORY_CARGO_DISCORD_USER_ID` in `crew_map.json`.
6. Invite the bot (scopes `bot` + `applications.commands`).
7. Run `python discord_crew_bot.py --crew inventory_cargo` and `python relay_watcher.py --crew inventory_cargo --queue relay_queue.jsonl --poll 5` on **PINKCADY**.
8. **No token is stored in the vault or in any doc.** Tokens live only in your local `.env`.
