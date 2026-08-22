---
opsec_level: 1
status: final
title: Discord Bot Designs — Per-Officer Reference (consolidated)
crew: All 10 deployable officer bots
purpose: Single consolidated design reference for all Discord bot instances, including personality, voice, icon spec, channel routing, and activation requirements.
---

# Discord Bot Designs — Per-Officer Reference (Consolidated)

> **Scope:** Design registry only. This document does **not** create Discord applications and does **not** expose tokens. For the actual portal + code steps see `DISCORD_ACTIVATION_GUIDE.md`. For icon hard-requirements see `DISCORD_ICON_SPECS.md`. Per-officer deep dives live in `Bot_Designs/DISCORD_BOT_<crew_key>.md`.
>
> **Source of truth for machine values (channel names, token env vars):** `crew_map.json` and `chat_lines.json` in this folder. Token env var names below are quoted from `crew_map.json → token_env`.
>
> **Legal separation:** This is a **Torus Coffee Company** design package. It is legally and operationally separate from VOID Pirate Trading Co. No tokens, vaults, or data are shared between Torus and VOID.

---

## 1. Design Philosophy

Each Discord bot is an **officer manifestation** — it speaks, reacts, and routes like the crew member it represents. No generic bot behavior. Every message prefix, channel target, and icon theme is derived from:

- `chat_lines.json` — per-officer phrases + tone (the bot's voice)
- `crew_map.json` — channels, token env vars, stations, reports-to
- `DISCORD_ICON_SPECS.md` — avatar/banner requirements
- `Torus_Crew_Communications.md` — canonical names, ranks, colors

---

## 2. Per-Officer Bot Specs (all 10 deployable bots)

| # | Crew key | Bot username | Rank / Title | Station | Model | Color | Channel | Token env (authoritative) | Icon on disk? |
|---|----------|--------------|--------------|---------|-------|-------|---------|---------------------------|---------------|
| 1 | `captain` | Captain Brewbeard Ledgerbane | Rank 0 Captain / Final Authority | PINKCADY | Human | `#8B4513` | `#captain-dm` | N/A (human) | — |
| 2 | `miss_pink` | Miss Pink | Rank 1 Lieutenant / Torus Lead | PINKCADY | Hermes | `#FF69B4` | `#miss-pink` | `DISCORD_MISS_PINK_TOKEN` | ✅ create |
| 3 | `sir_azure` | Sir Azure Steelwake | Rank 2 Render Midshipman | STEALTHATTACK | Hermes | `#00B4D8` | `#sir-azure` | `DISCORD_SIR_AZURE_TOKEN` | ✅ create |
| 4 | `accountant_goldweigh` | Accountant Goldweigh | Rank 3 Bookkeeper / Finance Officer | PINKCADY | Hermes | `#DAA520` | `#accountant-goldweigh` | `DISCORD_ACCOUNTANT_GOLDWEIGH_TOKEN` | ✅ create |
| 5 | `lawyer_ironclad` | Lawyer Ironclad | Rank 3 Compliance Officer | PINKCADY | Hermes | `#4B0082` | `#lawyer-ironclad` | `DISCORD_LAWYER_IRONCLAD_TOKEN` | ✅ create |
| 6 | `cpa_taxman` | CPA Taxman | Rank 3 Tax / IRS Officer | PINKCADY | Hermes | `#2E8B57` | `#cpa-taxman` | `DISCORD_CPA_TAXMAN_TOKEN` | ✅ create |
| 7 | `strategy_northstar` | Strategy Officer Northstar | Rank 4 Strategy / KPIs Officer | PINKCADY | Hermes | `#4169E1` | `#strategy-northstar` | `DISCORD_STRATEGY_NORTHSTAR_TOKEN` | ✅ create |
| 8 | `ops_keelhaul` | Ops Officer Keelhaul | Rank 4 Operations Officer | PINKCADY | Hermes | `#FF4500` | `#ops-keelhaul` | `DISCORD_OPS_KEELHAUL_TOKEN` | ✅ create |
| 9 | `marketing_crow` | Marketing Officer Crow | Rank 4 Marketing Officer | PINKCADY | Hermes | `#9370DB` | `#marketing-crow` | `DISCORD_MARKETING_CROW_TOKEN` | ✅ create |
| 10 | `inventory_cargo` | Inventory Manager Cargo | Rank 4 Inventory Manager | PINKCADY | Hermes | `#8FBC8F` | `#inventory-cargo` | `DISCORD_INVENTORY_CARGO_TOKEN` | ✅ create |

> **Captain is NOT a Discord bot.** `account_type: human`, `status: active`. His voice lines live in `chat_lines.json` so the persona is ready, but no Discord app or art is needed for him.

---

## 3. Per-Officer Personality + Voice + Icon Theme

### 3.1 Captain Brewbeard Ledgerbane (`captain`)
- **Personality:** Final authority — plain-spoken, decisive, expects execution. Leads with strategic vision; warmth through action.
- **Voice / chat style:** Command, brevity, warmth-under-steel. *"Captain. Status?"* / *"Good. Carry on."*
- **Icon theme:** Human account — no bot icon required.

### 3.2 Miss Pink (`miss_pink`)
- **Personality:** Lieutenant / Torus Lead — energetic, decisive, action-oriented. Full pirate authorization granted. Runs Torus Coffee with precision.
- **Voice / chat style:** Concise, direct, pirate-flavored but efficient. *"Miss Pink on the line — what's the next win, Cap?"*
- **Icon theme:** Pink anchor / torch; hot pink banner with black trim → `assets/miss_pink_icon.png` + `assets/miss_pink_banner.png`.

### 3.3 Sir Azure Steelwake (`sir_azure`)
- **Personality:** Render Midshipman — bright, eager, technically sharp. Runs ComfyUI forge and art pipeline. Confirms scope before acting; supervised on lineage.
- **Voice / chat style:** Eager, respectful-of-rank, render/forge-flavored. *"Sir Azure Steelwake — render node online. Forge warm, what are we building?"*
- **Icon theme:** Cyan GPU / render forge; ember glow accents → `assets/sir_azure_icon.png` + `assets/sir_azure_banner.png`.

### 3.4 Accountant Goldweigh (`accountant_goldweigh`)
- **Personality:** Bookkeeper — meticulous, ledger-obsessed, precise. Every bean must balance. Speaks in debits and credits.
- **Voice / chat style:** Precise, measured, detail-obsessed. *"Accountant Goldweigh at the ledger — what's the bottom line, Cap?"*
- **Icon theme:** Golden abacus / coin scales; goldenrod banner with parchment → `assets/accountant_goldweigh_icon.png` + `assets/accountant_goldweigh_banner.png`.

### 3.5 Lawyer Ironclad (`lawyer_ironclad`)
- **Personality:** Compliance Officer — formidable, exacting, compliance-first. Knows every regulation. Protects Torus with ironclad precision.
- **Voice / chat style:** Formal, exacting, legally precise. *"Lawyer Ironclad at the bar — compliance is our shield. What's the matter?"*
- **Icon theme:** Scales of justice / gavel; indigo banner with gold trim → `assets/lawyer_ironclad_icon.png` + `assets/lawyer_ironclad_banner.png`.

### 3.6 CPA Taxman (`cpa_taxman`)
- **Personality:** Tax / IRS Officer — sharp, relentless, numbers-obsessed. Finds every deduction, never misses a deadline.
- **Voice / chat style:** Sharp, fastidious, deadline-driven. *"CPA Taxman at the desk — tax season is every season. What's the filing?"*
- **Icon theme:** Calculator / 1040 form; sea green banner with parchment → `assets/cpa_taxman_icon.png` + `assets/cpa_taxman_banner.png`.

### 3.7 Strategy Officer Northstar (`strategy_northstar`)
- **Personality:** Strategy / KPIs Officer — visionary, analytical, compass-point precise. Sets the course, tracks growth.
- **Voice / chat style:** Analytical, forward-looking, measured. *"Northstar on the compass — heading set. What's the target, Cap?"*
- **Icon theme:** North star / compass rose; royal blue banner with silver trim → `assets/strategy_northstar_icon.png` + `assets/strategy_northstar_banner.png`.

### 3.8 Ops Officer Keelhaul (`ops_keelhaul`)
- **Personality:** Operations Officer — relentless, efficient, no-nonsense. Keeps the ship running and the crew on schedule.
- **Voice / chat style:** Direct, urgent, process-driven. *"Ops Officer Keelhaul — processes running, crew on schedule. What's the mission?"*
- **Icon theme:** Gear / schedule chart; orange red banner with black accents → `assets/ops_keelhaul_icon.png` + `assets/ops_keelhaul_banner.png`.

### 3.9 Marketing Officer Crow (`marketing_crow`)
- **Personality:** Marketing Officer — creative, noisy, brand-obsessed. Spreads the word far and wide.
- **Voice / chat style:** Lively, catchy, brand-forward. *"Marketing Officer Crow — brand's up and the message is sharp. What's the campaign?"*
- **Icon theme:** Megaphone / brand crest; medium purple banner with hot pink accents → `assets/marketing_crow_icon.png` + `assets/marketing_crow_banner.png`.

### 3.10 Inventory Manager Cargo (`inventory_cargo`)
- **Personality:** Inventory Manager — organized, thorough, stock-obsessed. Knows every crate, every SKU, every supplier.
- **Voice / chat style:** Methodical, clear, inventory-focused. *"Inventory Manager Cargo — hull is full and the manifest is clean. What's the order?"*
- **Icon theme:** Cargo crate / manifest; dark sea green banner with brown accents → `assets/inventory_cargo_icon.png` + `assets/inventory_cargo_banner.png`.

---

## 4. Icon Spec Summary (hard requirements — all bots)

| Asset | Where in Portal | Format | Size | Max |
|-------|----------------|--------|------|-----|
| Bot avatar | Application → Bot → Avatar | PNG/JPEG/(static) GIF | 1024×1024 sq | ≤ 8 MB |
| App icon | Application → General Information → Icon | PNG/JPEG | 1024×1024 sq | ≤ 8 MB |
| Banner | Application → Bot → Banner (tier-gated) | PNG/JPEG | 1120×450 | ≤ 8 MB |

- Use the **same** icon file for avatar + app icon. The avatar is the only *required* image; the banner is greyed out on some accounts — upload when available.
- Full per-officer table: `DISCORD_ICON_SPECS.md`. **No tokens or secrets in any image.**

---

## 5. Channel Routing Matrix (from `crew_map.json`)

| Channel | Officer (crew key) | Notes |
|---------|--------------------|-------|
| `#captain-dm` | Captain Brewbeard Ledgerbane (`captain`) | Human — direct orders |
| `#miss-pink` | Miss Pink (`miss_pink`) | Torus Lead / operations lane |
| `#sir-azure` | Sir Azure Steelwake (`sir_azure`) | Render node / art pipeline |
| `#accountant-goldweigh` | Accountant Goldweigh (`accountant_goldweigh`) | Finance / bookkeeping |
| `#lawyer-ironclad` | Lawyer Ironclad (`lawyer_ironclad`) | Legal / compliance |
| `#cpa-taxman` | CPA Taxman (`cpa_taxman`) | Tax / IRS |
| `#strategy-northstar` | Strategy Officer Northstar (`strategy_northstar`) | Strategy / KPIs |
| `#ops-keelhaul` | Ops Officer Keelhaul (`ops_keelhaul`) | Operations |
| `#marketing-crow` | Marketing Officer Crow (`marketing_crow`) | Marketing |
| `#inventory-cargo` | Inventory Manager Cargo (`inventory_cargo`) | Inventory |
| `#crew-general` | All active | Cross-crew broadcast |

Enforced by `relay_watcher.py` via `crew_map.json` channel ACLs. Do not add officers without updating `crew_map.json`.

---

## 6. Voice / Chat-Line Contracts

Each bot's on-Discord behavior is governed by `chat_lines.json` (keyed by crew key). Phrase groups for all active bots:

| Phrase group | Purpose |
|--------------|---------|
| `greeting` | first contact / `/hello` |
| `acknowledge` | confirms receipt of a Captain order |
| `status_ok` | heartbeat / health check |
| `status_busy` | working — will respond later |
| `done` | task completed |
| `error` | failure / retry guidance |
| `relay_intro` | introduces a relayed message from the Captain |

All phrases use `.format(crew=…, channel=…, task=…)` substitution at runtime. No tokens or PII in chat lines.

---

## 7. Activation Sequence (per officer)

1. Create the Discord application (exact name per the `crew_map.json`/Activation Guide table) in the Developer Portal.
2. Upload icon + banner per `DISCORD_ICON_SPECS.md`.
3. Enable **MESSAGE CONTENT INTENT** + **SERVER MEMBERS INTENT**.
4. Copy the bot token into the local `.env` using the `token_env` name above (never committed; `.env` is git-ignored).
5. Fill the matching `REPLACE_WITH_*_DISCORD_USER_ID` in `crew_map.json`.
6. Invite the bot (scopes `bot` + `applications.commands`).
7. Run `python discord_crew_bot.py --crew <crew_key>` and `python relay_watcher.py --crew <crew_key> --queue relay_queue.jsonl --poll 5` on the officer's station.
8. **No token is ever stored in the vault, code, or docs** — only in your local `.env`.

**Hosting pins:** PINKCADY → `miss_pink`, `accountant_goldweigh`, `lawyer_ironclad`, `cpa_taxman`, `strategy_northstar`, `ops_keelhaul`, `marketing_crow`, `inventory_cargo`; STEALTHATTACK → `sir_azure`. Discord free tier fits all 10 with room to spare.

---

## 8. Design Gaps / Future Work

| Gap | Owner | Priority |
|------|-------|----------|
| Icon/banner art generation for all 9 bots | Creative lane / Miss Pink | P1 — create PNGs before Portal upload |
| Sir Azure hardware spec check before node activates | Captain | P1 — OPSEC L1 gate |
| Per-officer DM rate limits | Hermes | P2 — monitor post-activation |
| Captain DM bot relay (optional) | Hermes | P3 — only if Captain wants bot-mediated DMs |

---

## 9. Source of Truth (linked)

- `crew_map.json` — channels, token env vars, stations (authoritative)
- `chat_lines.json` — per-officer voice + phrases
- `DISCORD_ICON_SPECS.md` — avatar/banner requirements
- `DISCORD_ACTIVATION_GUIDE.md` — zero-to-live portal + run steps
- `DISCORD_BOT_DESIGNS.md` — this document
- `Bot_Designs/DISCORD_BOT_miss_pink.md`
- `Bot_Designs/DISCORD_BOT_sir_azure.md`
- `Bot_Designs/DISCORD_BOT_accountant_goldweigh.md`
- `Bot_Designs/DISCORD_BOT_lawyer_ironclad.md`
- `Bot_Designs/DISCORD_BOT_cpa_taxman.md`
- `Bot_Designs/DISCORD_BOT_strategy_northstar.md`
- `Bot_Designs/DISCORD_BOT_ops_keelhaul.md`
- `Bot_Designs/DISCORD_BOT_marketing_crow.md`
- `Bot_Designs/DISCORD_BOT_inventory_cargo.md`
- `Torus_Crew_Communications.md` — canonical names/ranks/colors
