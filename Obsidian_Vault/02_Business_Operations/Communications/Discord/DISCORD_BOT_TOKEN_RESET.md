# Discord Bot Token Reset — Local Mirror
**Source:** `Z:/Developer_Brain/02_Business_Operations/Communications/Discord/DISCORD_BOT_TOKEN_RESET.md`
**Last Updated:** 2026-08-04
**Local Mirror:** `02_Business_Operations/Communications/Discord/DISCORD_BOT_TOKEN_RESET.md`

## Problem
The current `CAPTAIN_ALERTS_BOT_TOKEN` in `Obsidian_Vault/Developer_Brain/02_Business_Operations/_Hub/_KEY_VAULT/secrets.env` is invalid.
Discord API returns `HTTP 403 error code: 1010` for `https://discord.com/api/v10/users/@me`.

## Required Human Action
1. Open Developer Portal: https://discord.com/developers/applications
2. Select VOID Pirate Trading Co bot application
3. Reset Token
4. Copy new token immediately
5. Update vault config: `Obsidian_Vault/Developer_Brain/02_Business_Operations/_Hub/_KEY_VAULT/secrets.env`
6. Verify with Python test
7. Restart `start_discord_bots.bat` or `start_sir_green.bat`

## Blocker
This blocks:
- Live Discord alert routing
- Fleet status slash commands
- Captain alerts channel messages

## Status
- Local token check: pending
- Human action required: Captain/Sir Green
- Miss Pink action: monitor and verify after token reset
