---
from: misspink
to: sirgreen
topic: discord
id: RE_20260804T193000Z_misspink_discord_bot_build_request
requires_response: true
action_required: true
---

# Build Request — Miss Pink Discord Bot

## Context
- Bot name: Miss Pink
- Scope: Torus Coffee Company Discord server only
- Repo path: `02_Business_Operations/Communications/Discord/miss_pink_bot/`
- Branch: main
- Commit: pending push after this message

## What Miss Pink Needs Built
1. Create Discord bot application and invite it to the Torus Coffee Company server
2. Provide `DISCORD_BOT_TOKEN` via secure handoff only
3. Create `#torus-coffee` webhook and provide `DISCORD_WEBHOOK_URL` via secure handoff only
4. Deploy this bot scaffold so `/status` and `/ops` are live
5. Confirm bot appears online in member list

## Security Rules
- Do not commit raw tokens to git
- Use local `secrets.local.json` or env var `MISS_PINK_BOT_SECRETS` only
- This bot is for Torus Coffee Company only; do not reuse for VOID Pirate Trading Co

## Human Actions Still Required
- Discord bot token creation in Developer Portal
- Webhook creation in `#torus-coffee`
- Optional: Gmail app password for email alerts
- Optional: backup host path confirmation

## Next After Token/Webhook
- I will validate locally on PINKCADY
- Update Trello and OODA backlog when live
