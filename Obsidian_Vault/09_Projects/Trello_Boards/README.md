# Trello Boards — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Active — 3 real Trello boards

## Board URLs

- **Torus_Ops:** https://trello.com/b/cZFvOC8l/torusops
- **Business_Docs:** https://trello.com/b/JmUh5kJA/businessdocs
- **Website_Rebuild:** https://trello.com/b/orPSpaRA/websiterebuild

## API Integration

- Credentials: `01_Operating/Operating Paperwork/Trello_API_Credentials.md`
- Board IDs documented in credentials file
- API key + OAuth token configured

## Usage

- All project tracking done in Trello
- Cards synced to vault markdown via automation
- Updates via Trello API in automation scripts

## Automation

- `trello_sync.py` — syncs boards to markdown
- Task Scheduler: daily at 8:30 AM
