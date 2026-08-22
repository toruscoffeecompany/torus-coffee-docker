# DISCORD ACTIVATION GUIDE — Torus Coffee Company Crew Fleet

**Goal:** Take the Torus Discord bot infrastructure from "designed" to "running" in one sitting.
**Time:** ~15–20 minutes. **Cost:** $0 (Discord free tier).
**Security rule:** This guide creates NO Discord applications and stores NO tokens. You paste your own tokens into a local `.env` file that is git-ignored. Tokens never touch the vault or this guide.

> **Legal separation:** Torus Coffee Company Discord infrastructure is completely separate from VOID Pirate Trading Co. This is a Torus-only package.

---

## 0. What you are building

10 Discord **bot users**, one per officer (Captain Brewbeard Ledgerbane is human; the other 9 are bots). Each officer has:
- a distinct **personality / chat voice** (`chat_lines.json`)
- a dedicated **channel** (`crew_map.json` → `channel`)
- a **relay watcher** that posts Captain messages into their channel in-character (`relay_watcher.py`)
- an **icon + banner** to upload during activation

```
Captain (human, own Discord account)
   │  DMs a bot  ──►  discord_crew_bot.py --crew <officer>
   │  (or drops a relay item) ──► relay_watcher.py --crew <officer> --queue relay_queue.jsonl
   ▼
Officer bot posts into #<officer-channel>  →  sync target (Hermes / Claude / Codex on its station)
```

**Files in this folder (all present):**

| File | Purpose |
|------|---------|
| `crew_map.json` | Crew registry: IDs, roles, channels, `token_env` per officer |
| `chat_lines.json` | Per-officer voice: greetings, ack, status, errors, relay intros |
| `crew_common.py` | Shared loader: reads crew_map + chat_lines, resolves tokens (dotenv) |
| `discord_crew_bot.py` | The interactive bot (slash commands) per officer |
| `relay_watcher.py` | Watches the queue, forwards to the right channel in-character |
| `requirements.txt` | `discord.py`, `python-dotenv` |
| `.env.example` | Template for your tokens (copy → `.env`) |
| `assets/` | PNGs per officer: icon + banner |
| `DISCORD_BOT_DESIGNS.md` | Consolidated design reference |
| `Bot_Designs/` | Per-officer deep dive design docs |

---

## 1. Prerequisites

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Discord account + a server already created (**Torus Coffee Company Crew**)
- [ ] Dependency install (one time):
  ```bash
  cd "D:/Work/Torus Coffee Company LLC/10_Skills_Library/05_Operations/Crew/Torus_Discord"
  pip install -r requirements.txt
  ```

---

## 2. Create the 9 bot applications (Developer Portal)

> Do this in a browser. No code, no tokens committed.

1. Open **https://discord.com/developers/applications** and log in.
2. Click **New Application** (top-right) → name it → **Create**. Repeat 9× with these exact names.

| # | Application Name | Bot Username | Channel | Host station |
|---|------------------|--------------|---------|--------------|
| 1 | `Torus Miss Pink` | `Miss Pink` | `#miss-pink` | PINKCADY |
| 2 | `Torus Sir Azure Steelwake` | `Sir Azure Steelwake` | `#sir-azure` | STEALTHATTACK |
| 3 | `Torus Accountant Goldweigh` | `Accountant Goldweigh` | `#accountant-goldweigh` | PINKCADY |
| 4 | `Torus Lawyer Ironclad` | `Lawyer Ironclad` | `#lawyer-ironclad` | PINKCADY |
| 5 | `Torus CPA Taxman` | `CPA Taxman` | `#cpa-taxman` | PINKCADY |
| 6 | `Torus Strategy Officer Northstar` | `Strategy Officer Northstar` | `#strategy-northstar` | PINKCADY |
| 7 | `Torus Ops Officer Keelhaul` | `Ops Officer Keelhaul` | `#ops-keelhaul` | PINKCADY |
| 8 | `Torus Marketing Officer Crow` | `Marketing Officer Crow` | `#marketing-crow` | PINKCADY |
| 9 | `Torus Inventory Manager Cargo` | `Inventory Manager Cargo` | `#inventory-cargo` | PINKCADY |

3. For **each** application:
   - **Bot tab → Add Bot → Yes, do it!**
   - **Reset Token → Copy** the token. (You will paste it into `.env` in Step 4.)
   - **Upload icon:** `assets/<key>_icon.png` (1024×1024). Upload banner: `assets/<key>_banner.png` (1120×450).
   - **Privileged Gateway Intents:** enable **MESSAGE CONTENT INTENT** and **SERVER MEMBERS INTENT**.
   - **OAuth2 → URL Generator:** Scopes = `bot` + `applications.commands`.
     Bot Permissions = Send Messages, Read Message History, Send Messages in Threads,
     Use Slash Commands, Read Messages/View Channels, Embed Links, Attach Files,
     Mention Everyone/Here, Manage Messages, Add Reactions.
   - **Copy the generated invite URL.**

> Icon/banner asset reference (create before Portal upload):
> - `assets/miss_pink_icon.png`, `assets/miss_pink_banner.png`
> - `assets/sir_azure_icon.png`, `assets/sir_azure_banner.png`
> - `assets/accountant_goldweigh_icon.png`, `assets/accountant_goldweigh_banner.png`
> - `assets/lawyer_ironclad_icon.png`, `assets/lawyer_ironclad_banner.png`
> - `assets/cpa_taxman_icon.png`, `assets/cpa_taxman_banner.png`
> - `assets/strategy_northstar_icon.png`, `assets/strategy_northstar_banner.png`
> - `assets/ops_keelhaul_icon.png`, `assets/ops_keelhaul_banner.png`
> - `assets/marketing_crow_icon.png`, `assets/marketing_crow_banner.png`
> - `assets/inventory_cargo_icon.png`, `assets/inventory_cargo_banner.png`

---

## 3. Invite each bot to your server

1. Open each copied invite URL from Step 2.
2. Select your **Torus Coffee Company Crew** server → **Authorize**.
3. Complete the CAPTCHA if asked.
4. Confirm all 9 bots appear in the server member list.

Optional channels to create in the server (bot posts here via the relay watcher):
`#miss-pink`, `#sir-azure`, `#accountant-goldweigh`, `#lawyer-ironclad`, `#cpa-taxman`, `#strategy-northstar`, `#ops-keelhaul`, `#marketing-crow`, `#inventory-cargo`, plus `#crew-general`.

---

## 4. Store the tokens locally (no commit, no vault)

1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and paste each token after the `=`:
   ```dotenv
   DISCORD_MISS_PINK_TOKEN=MTxx...your_real_token_here
   DISCORD_SIR_AZURE_TOKEN=MTxx...
   DISCORD_ACCOUNTANT_GOLDWEIGH_TOKEN=MTxx...
   DISCORD_LAWYER_IRONCLAD_TOKEN=MTxx...
   DISCORD_CPA_TAXMAN_TOKEN=MTxx...
   DISCORD_STRATEGY_NORTHSTAR_TOKEN=MTxx...
   DISCORD_OPS_KEELHAUL_TOKEN=MTxx...
   DISCORD_MARKETING_CROW_TOKEN=MTxx...
   DISCORD_INVENTORY_CARGO_TOKEN=MTxx...
   ```
3. The env var **names are authoritative** — `crew_common.py` reads them straight from
   `crew_map.json` → `token_env`. Do not rename them.
4. `.env` is already covered by `.gitignore`. If you keep this folder under git, confirm
   `.env` and `*.env` are ignored so tokens never get committed.

> If you prefer OS-level env vars instead of `.env`, set the names above in
> Windows "Edit environment variables for your account". Both work; `.env` is simpler.

---

## 5. Fill in crew Discord User IDs (so DMs resolve)

1. Discord → Settings → Advanced → enable **Developer Mode**.
2. Right-click each person/bot → **Copy User ID**.
3. Edit `crew_map.json` and replace each `REPLACE_WITH_*_DISCORD_USER_ID` with the real ID
   (Captain = your own ID; the 9 officers = each bot user's ID).

---

## 6. Run the bots (one process per officer)

Open a terminal per officer (or a process manager / Hermes cron on each station).

```bash
cd "D:/Work/Torus Coffee Company LLC/10_Skills_Library/05_Operations/Crew/Torus_Discord"

python discord_crew_bot.py --crew miss_pink              # PINKCADY
python discord_crew_bot.py --crew sir_azure              # STEALTHATTACK
python discord_crew_bot.py --crew accountant_goldweigh   # PINKCADY
python discord_crew_bot.py --crew lawyer_ironclad        # PINKCADY
python discord_crew_bot.py --crew cpa_taxman             # PINKCADY
python discord_crew_bot.py --crew strategy_northstar     # PINKCADY
python discord_crew_bot.py --crew ops_keelhaul           # PINKCADY
python discord_crew_bot.py --crew marketing_crow         # PINKCADY
python discord_crew_bot.py --crew inventory_cargo        # PINKCADY
```

Each should print:
```
[READY] <Officer Name> bot logged in as <botuser> (id=...)
[SYNC] Slash commands synced: N
```

> `--crew` choices are derived from `crew_map.json` automatically.

---

## 7. Run the relay watcher (Captain → officer channel, in character)

The watcher polls `relay_queue.jsonl` and posts any item addressed to its officer into that
officer's channel, prefixed with the officer's name and a relay intro line from `chat_lines.json`.

```bash
# PINKCADY (8 watchers) + STEALTHATTACK (1 watcher)
python relay_watcher.py --crew miss_pink --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew sir_azure --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew accountant_goldweigh --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew lawyer_ironclad --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew cpa_taxman --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew strategy_northstar --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew ops_keelhaul --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew marketing_crow --queue relay_queue.jsonl --poll 5
python relay_watcher.py --crew inventory_cargo --queue relay_queue.jsonl --poll 5
```

**Queue item format** (one JSON object per line in `relay_queue.jsonl`):
```json
{"officer": "miss_pink", "from": "captain", "task": "torus_operations", "message": "Patch staging and report when tests are green."}
```
- `officer` (or `channel`) decides which watcher handles it.
- Sent items are removed from the `.jsonl`; directory-mode items are moved to `relay_queue/done`.

**Dry run (no token, no Discord):**
```bash
python relay_watcher.py --crew miss_pink --queue relay_queue.jsonl --dry-run
```
Prints exactly what each officer *would* say, without connecting.

---

## 8. Verify slash commands

In Discord, type `/` in any channel. You should see:
- `/crew-dm` — DM a crew member (Captain relay)
- `/crew-list` — list configured crew
- `/crew-status` — this officer's status + voice
- `/say` — speak a line in this officer's character (`context`: greeting/acknowledge/done/error/…)
- `/relay` — post a Captain relay into this officer's channel

Slash commands can take 5–10 min to propagate after first login; restart the bot if they don't appear.

---

## 9. Keep them alive (24/7)

On **PINKCADY**:
- `miss_pink`, `accountant_goldweigh`, `lawyer_ironclad`, `cpa_taxman`, `strategy_northstar`, `ops_keelhaul`, `marketing_crow`, `inventory_cargo` (8 processes)

On **STEALTHATTACK**:
- `sir_azure` (1 process)

Use Windows Task Scheduler, a process manager, or Hermes cron to keep them alive. Each process
is cheap on the free tier. Monitor with `/crew-status` from any officer channel.

---

## 10. Security checklist

- [ ] All tokens stored in local `.env` (never committed to git)
- [ ] `.env` listed in `.gitignore`
- [ ] No tokens appear in `crew_map.json`, `chat_lines.json`, or any markdown
- [ ] No VOID Pirate Trading Co tokens or data in this folder
- [ ] Captain has confirmed legal separation from VOID before go-live

---

## 11. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Bot shows offline | Check `.env` token; verify bot is invited to server; check intents enabled |
| Slash commands missing | Wait 5–10 min after first login; restart bot; check scopes in Developer Portal |
| Relay not posting | Verify `relay_queue.jsonl` has items addressed to the right `officer`; check watcher is running |
| DM not sending | Verify `discord_user_id` in `crew_map.json` is filled; check bot has DM permissions |
| Wrong voice | Verify `crew_key` matches `chat_lines.json` and `crew_map.json` exactly |

---

## 12. Next steps after activation

1. Test all `/say` contexts for each bot to confirm voice matches `chat_lines.json`.
2. Verify relay queue end-to-end: Captain drops item → officer posts in-channel.
3. Confirm Captain DM routing works for all 9 bots.
4. Notify Sir Green (VOID infrastructure lead) that Torus crew is live and legal separation is confirmed.
5. Set up monitoring / uptime checks for all 9 bots.
