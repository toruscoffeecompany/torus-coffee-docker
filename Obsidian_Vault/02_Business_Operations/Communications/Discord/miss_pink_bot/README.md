# Miss Pink Discord Bot

This is the canonical Miss Pink bot scaffold for the Torus Coffee Company Discord server.
It is intended for **Torus Coffee Company use only**.

## Setup
1. Copy `secrets.example.json` to `secrets.local.json`
2. Fill in `DISCORD_BOT_TOKEN` and `DISCORD_WEBHOOK_URL`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python -m miss_pink_bot.bot`

## Security
- Do NOT commit `secrets.local.json`
- Do NOT hardcode tokens
- Use local secrets file or `MISS_PINK_BOT_SECRETS` env var only

## For Sir Green
- Build/deploy this bot for Torus Coffee Company Discord only
- Do NOT reuse this scaffold for VOID Pirate Trading Co without separate config/token
