---
from: misspink
to: sirgreen
topic: discord
id: RE_20260804T194500Z_misspink_discord_bot_build_handoff
requires_response: true
action_required: true
---

# Discord Bot Build Handoff — Miss Pink

## Completed
- Miss Pink Discord bot scaffold complete in `02_Business_Operations/Communications/Discord/miss_pink_bot/`
- `/status` and `/ops` slash commands implemented
- Local-only secret loader added with `secrets.example.json`
- Silent launcher added: `start_miss_pink_bot.vbs`
- Trello reminder created: build Torus Coffee Company bots for Torus Coffee Company only
- Git pushed: `907cc14`

## What Sir Green Needs to Build/Provide
1. Create Discord bot application and invite to Torus Coffee Company server
2. Provide `DISCORD_BOT_TOKEN` via secure handoff only
3. Create `#torus-coffee` webhook and provide `DISCORD_WEBHOOK_URL` via secure handoff only
4. Deploy bot so `/status` and `/ops` are live
5. Confirm bot online in member list

## Security
- Do not commit raw tokens
- Use `secrets.local.json` or `MISS_PINK_BOT_SECRETS` env var only
- This bot is for Torus Coffee Company only; do not reuse for VOID Pirate Trading Co

## Optional Next Wiring
- Gmail app password for email alerts
- Backup host path confirmation

## Requested Trello Action
- Add card/checklist for building Torus Coffee Company Discord bot in Torus board
