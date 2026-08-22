# Miss Pink Discord Bot — Build Requirements for Sir Green
_Date: 2026-08-04_

## Build Scope
- Bot name: Miss Pink
- Server: Torus Coffee Company Discord only
- Repo path: `02_Business_Operations/Communications/Discord/miss_pink_bot/`
- Secret handling: local-only; never commit tokens

## What Sir Green Must Build/Provide
1. **Discord bot application**
   - Create in Discord Developer Portal
   - Invite to Torus Coffee Company server
   - Provide `DISCORD_BOT_TOKEN` via secure handoff only
2. **Webhook**
   - Create in `#torus-coffee`
   - Provide `DISCORD_WEBHOOK_URL` via secure handoff only
3. **Deploy bot**
   - Ensure `/status` and `/ops` commands are live
   - Confirm bot online in member list
4. **Optional wiring**
   - Gmail app password for email alerts
   - Backup host path confirmation

## Security Constraints
- Do not commit raw tokens
- Use `secrets.local.json` or `MISS_PINK_BOT_SECRETS` env var
- Do not reuse this bot for VOID Pirate Trading Co

## Trello Reminder
- Create card: build Torus Coffee Company bots for Torus Coffee Company only
