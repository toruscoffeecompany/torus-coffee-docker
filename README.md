# Torus Coffee Company - Docker Guide

## Free Tier Constraints
- **SQUIDSTATION:** Primary Docker host
- **PINKCADY:** Docker Desktop for local development
- **STEALTHATTACK:** No Docker (blocked)

## Services
- `torus-dashboard` — Local dashboard on port 3001
- `torus-bot` — Discord bot placeholder

## Commands
```bash
# Start dashboard locally
docker compose --profile local up -d

# Start all bots
docker compose --profile bots up -d

# Stop all
docker compose down

# View logs
docker compose logs -f
```

## Notes
- All containers use free-tier images
- No paid Docker subscriptions required
- SQUIDSTATION is production Docker host
