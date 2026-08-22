# Torus Coffee Company — Setup Checklist

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Active — work from top to bottom  
**Rule:** Free tier only until revenue. No paid upgrades without approval.

## Accounts To Create

| # | Account | URL | Priority |
|---|---------|-----|----------|
| 1 | Buffer | buffer.com/signup | P1 |
| 2 | Zapier | zapier.com/signup | P1 |
| 3 | HubSpot CRM | hubspot.com/pricing/crm | P1 |
| 4 | Meta Business Suite | business.facebook.com | P1 |
| 5 | Pinterest business | pinterest.com/business/create | P2 |
| 6 | TikTok | tiktok.com | P2 |
| 7 | LinkedIn company | linkedin.com/company/create | P2 |

## API Keys / Tokens To Get

| # | Service | Where | Priority |
|---|---------|-------|----------|
| 1 | Buffer access token | developers.buffer.com | P2 |
| 2 | Zapier webhook URL | From first Zap | P2 |
| 3 | HubSpot API key | HubSpot settings → integrations | P2 |
| 4 | Facebook page access token | developers.facebook.com | P2 |

## Verify / Claim

| # | Platform | Handle / URL | Priority |
|---|----------|--------------|----------|
| 1 | Facebook | facebook.com/61577390931175 | P1 |
| 2 | Instagram | @glvwriter or @toruscoffeecompany | P2 |
| 3 | X/Twitter | @TorusCoffee | P3 |
| 4 | YouTube | @TorusCoffeeCompany | P3 |
| 5 | Pinterest | @toruscoffeecompany | P2 |
| 6 | TikTok | @toruscoffeecompany | P2 |
| 7 | LinkedIn | Torus Coffee Company LLC | P2 |

## Optional Installs

| # | App / Extension | Platform | Priority |
|---|-----------------|----------|----------|
| 1 | Buffer browser extension | Chrome/Firefox | P3 |
| 2 | HubSpot mobile app | iOS/Android | P3 |
| 3 | Meta Business Suite app | iOS/Android | P3 |

## Integration Testing

| # | Test | Status |
|---|------|--------|
| 1 | Buffer scheduling with 1 post | Pending |
| 2 | Zapier webhook end-to-end | Pending |
| 3 | HubSpot contact import | Pending |
| 4 | Meta Business Suite scheduling | Pending |

## Verified Integrations

- **Buffer:** GraphQL API connected, 3 channels found
- **Zapier:** Webhook live and tested
- **HubSpot CRM:** Service Key connected
- **Trello:** 365 cards tracking all work across 3 boards
- **Square:** Payment links created for all 8 visible products (free tier: $0/mo, 2.9% + 30¢/txn)
- **Website:** Static product data wired with Square Payment Links — "Buy now" buttons active

## Automation Scripts

- `automation_core.py` — shared retry, logging, credential loader
- `buffer_automation.py` — Buffer status + channels working
- `zapier_automation.py` — webhook wired and tested
- `hubspot_crm.py` — contacts/deals API verified
- `automation_orchestrator.py` — 8/8 scripts verified
- `social_media_automation.py`
- `inventory_tracker.py`
- `daily_ops_automation.py`
- `weekly_review_automation.py`
- `monthly_review_automation.py`

## Task Scheduler

- Multiple Torus jobs configured
- Some jobs need manual path correction
- See `Automation_Runbook.md` for details

## Credential Files

- `10_Skills_Library/05_Operations/buffer_credentials.json`
- `10_Skills_Library/05_Operations/zapier_credentials.json`
- `10_Skills_Library/05_Operations/hubspot_credentials.json`

## Current System State

- **Git:** Synced to `toruscoffeecompany/Torus_Ops` — 2GB Ollama blob purged from history ✅
| **Trello:** 307 open cards (Top10=10, P0=2, P1=1, P2=72, P3=39) — reduced from 1,522 via OODA card cleanup + crew transfer
- **Obsidian:** All core plugins installed (periodic-notes, table-editor, livesync, calendar, daily notes)
- **Python:** 3.11.15 available via vault venv
- **Automation scripts:** 8 core scripts verified via orchestrator
- **Task Scheduler:** 14 active Torus jobs (12 running, 2 disabled)
- **Integrations:** Buffer, Zapier, HubSpot CRM, Trello — all verified
- **Ollama:** vault-bound on PINKCADY, llama3.2:latest (2GB) serving on localhost:11434
- **Docker:** 10 fleet containers across torus-network, healthchecks switched to wget
- **Tailscale:** 4-node fleet mesh active (PINKCADY=.3, SQUIDSTATION=.39, STEALTHATTACK=.32)

## Architecture

- **Local Dashboard:** Runs on the local network only. Shows automation status, inventory, Trello boards, Buffer/Zapier/HubSpot health. Not exposed to the public internet.
- **Public Website:** Runs on the public internet. Shows products, about, contact, legal. Does not expose internal automation or vault data.

## Next Steps

- ✅ Connect real payment (Square Payment Links — free tier, wired to product data)
- ✅ Choose payment processor (Square primary, PayPal backup — see `03_Financials/Payment_Processor_Decision.md`)
- Begin website build and deployment
- Verify all pages build successfully
- Test contact form end-to-end
- Deploy website to free hosting
- Connect website to Obsidian vault data

## Files

- `Setup_Checklist.md` — setup tracking
- `00_Vault_Home.md` — vault index
- `09_Projects/Pre_Website_Automation_Checklist.md` — automation checklist
- `06_Growth_Marketing/Social_Media_Master_Setup.md` — social media plan
- `10_Skills_Library/05_Operations/Free_Tools_Reference.md` — all free tools
