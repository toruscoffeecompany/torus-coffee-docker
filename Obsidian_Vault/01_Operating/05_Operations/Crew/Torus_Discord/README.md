# Torus Discord Bot Design Package

**Classification:** Torus Coffee Company — internal only.
**Legal separation:** This package is legally and operationally separate from VOID Pirate Trading Co. No tokens, vaults, or data are shared.

---

## What's in this folder

| File / Folder | Purpose |
|---------------|---------|
| `crew_map.json` | Authoritative crew registry: IDs, channels, token env vars, stations |
| `chat_lines.json` | Per-officer voice: greetings, ack, status, errors, relay intros |
| `.env.example` | Template for local token storage (copy → `.env`; never commit) |
| `DISCORD_BOT_DESIGNS.md` | Consolidated design reference for all 10 crew members |
| `DISCORD_ACTIVATION_GUIDE.md` | Zero-to-live portal + run steps |
| `Bot_Designs/` | Per-officer deep dive design docs (10 docs) |

---

## Crew (Torus Coffee Company)

1. **Captain Brewbeard Ledgerbane** — Captain / Final Authority (human)
2. **Miss Pink** — Lieutenant / Torus Lead (Hermes, PINKCADY)
3. **Sir Azure Steelwake** — Render Midshipman (Hermes, STEALTHATTACK)
4. **Accountant Goldweigh** — Bookkeeper / Finance Officer (Hermes, PINKCADY)
5. **Lawyer Ironclad** — Compliance Officer (Hermes, PINKCADY)
6. **CPA Taxman** — Tax / IRS Officer (Hermes, PINKCADY)
7. **Strategy Officer Northstar** — Strategy / KPIs Officer (Hermes, PINKCADY)
8. **Ops Officer Keelhaul** — Operations Officer (Hermes, PINKCADY)
9. **Marketing Officer Crow** — Marketing Officer (Hermes, PINKCADY)
10. **Inventory Manager Cargo** — Inventory Manager (Hermes, PINKCADY)

---

## Quick start

1. Read `DISCORD_BOT_DESIGNS.md` for personality, voice, and icon themes.
2. Follow `DISCORD_ACTIVATION_GUIDE.md` to create bots and get them running.
3. Copy `.env.example` → `.env` and paste your tokens (never commit).
4. Run `python discord_crew_bot.py --crew <crew_key>` per officer.
5. Run `python relay_watcher.py --crew <crew_key> --queue relay_queue.jsonl --poll 5` per officer.

---

## Legal separation rules

1. **Vault separation:** Torus vault on PINKCADY, VOID vault on SQUIDSTATION
2. **Crew separation:** Torus crew bots never access VOID data
3. **Secret separation:** Torus credentials in Torus vault only, never in VOID
4. **Git separation:** Torus repos vs VOID repos, never mixed
5. **Docker separation:** Torus containers use `torus-*` prefix
6. **Communication separation:** Torus Discord server vs VOID Discord server

---

## Status

- ✅ Crew personas designed
- ✅ Bot design docs created (10 docs)
- ✅ Design registry completed
- ✅ Activation guide written
- ⏳ Awaiting Discord server creation + bot activation

---

**Next steps:**
1. Create Torus Discord server (`Torus Coffee Company Crew`)
2. Create bot applications per `DISCORD_ACTIVATION_GUIDE.md`
3. Upload icons/banners per `DISCORD_ICON_SPECS.md`
4. Test all bots and relay watchers
5. Confirm legal separation with Captain before go-live
