---
opsec_level: 1
status: final
title: Discord Bot Design — CPA Taxman
crew_key: cpa_taxman
---

# Discord Bot Design — CPA Taxman (`cpa_taxman`)

> **Design registry only.** This document does **not** create a Discord application and does **not** expose tokens. Real activation steps live in `../DISCORD_ACTIVATION_GUIDE.md`; icon hard-requirements live in `../DISCORD_ICON_SPECS.md`.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **Discord username** | CPA Taxman |
| **Crew key (authoritative)** | `cpa_taxman` |
| **Rank / title** | Rank 3 — Tax / IRS Officer |
| **Station** | PINKCADY |
| **Runtime / model** | Hermes Agent |
| **Sync target** | Hermes on PINKCADY |
| **Color** | `#2E8B57` (sea green — IRS/money) |
| **Channel** | `#cpa-taxman` |
| **Token env (authoritative)** | `DISCORD_CPA_TAXMAN_TOKEN` |
| **Discord bot** | Yes |
| **Account type** | bot |
| **Reports to** | Miss Pink, Captain |

## 2. Personality summary

CPA Taxman — sharp, relentless, numbers-obsessed. Finds every deduction, files every form, never misses a deadline. Fear the IRS, trust the Taxman. The fiscal guardian of Torus Coffee.

**Sources of truth:** `chat_lines.json → cpa_taxman`, `crew_map.json → cpa_taxman`, and `Torus_Crew_Communications.md`.

## 3. Chat style

- Sharp, fastidious, deadline-driven.
- Short, tax-first phrasing; references to filings, deductions, codes.
- Conversational signature (from `chat_lines.json`): *"CPA Taxman at the desk — tax season is every season. What's the filing?"* / *"Filed and confirmed."*

## 4. Icon spec

- **Icon file (on disk):** `assets/cpa_taxman_icon.png` — 1024 × 1024 square, PNG/JPEG, ≤ 8 MB.
- **Banner file (on disk):** `assets/cpa_taxman_banner.png` — 1120 × 450, PNG/JPEG, ≤ 8 MB.
- **Theme:** Calculator / 1040 form; sea green banner with parchment accents — tax branding.
- **Portal drop:** *General Information → Icon*, *Bot → Avatar* (same file), *Bot → Banner* (if enabled).
- Full hard-requirements in `../DISCORD_ICON_SPECS.md`.

## 5. Channel routing

| Channel | Role |
|---------|------|
| `#cpa-taxman` | Dedicated DM channel for tax/IRS |
| `#crew-general` | Cross-crew broadcast |
| `#captain-dm` | Direct orders from Captain |

Routing is enforced by `relay_watcher.py` → `#cpa-taxman` using the `crew_map.json` channel ACLs.

## 6. Activation requirements

1. Create Discord application `Torus CPA Taxman` (Bot username `CPA Taxman`) in the Developer Portal.
2. Upload `assets/cpa_taxman_icon.png` (avatar + app icon) and `assets/cpa_taxman_banner.png` (banner).
3. Enable **MESSAGE CONTENT INTENT** + **SERVER MEMBERS INTENT**.
4. Copy the token → local `.env` as `DISCORD_CPA_TAXMAN_TOKEN` (never committed).
5. Fill `REPLACE_WITH_CPA_TAXMAN_DISCORD_USER_ID` in `crew_map.json`.
6. Invite the bot (scopes `bot` + `applications.commands`).
7. Run `python discord_crew_bot.py --crew cpa_taxman` and `python relay_watcher.py --crew cpa_taxman --queue relay_queue.jsonl --poll 5` on **PINKCADY**.
8. **No token is stored in the vault or in any doc.** Tokens live only in your local `.env`.
