# ALERT ROUTER WEBHOOK RETRY PLAN
## Goal
Activate alert-router webhook path and retry dashboard automation reporting.

## Current state
- torus-alert-router container up, `/health` returns 200
- Core functionality implemented: Discord webhook, SMTP, Obsidian integration
- Blocked on env vars: `DISCORD_WEBHOOK`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `OBSIDIAN_VAULT`
- Dashboard post fails: no listener on localhost:8080

## Plan
1. PATCH `docker-compose.torus.fleet.yml` to mount `.env` into alert-router
2. PATCH `alert_router.py` to read env vars on startup and validate required fields
3. Add `/webhook` route to alert-router for Prometheus Alertmanager
4. Add fallback write to `automation_status.json` if dashboard unreachable
5. Send Sir Green/Sir Azure concrete asks for missing secrets and dashboard route

## Crew asks
- Sir Green: dashboard port/route confirmation
- Sir Azure: Livesync peer name + Docker overlay preference
- Captain/Miss Gordon: Discord webhook URL, Gmail SMTP [REDACTED], Obsidian vault path
