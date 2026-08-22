# TRELLO TOP 10 AUTOMATION PLAN — 2026-08-06
Generated: 2026-08-06T07:30:00.000000+00:00
Status: DESIGN

## Concept
Maintain a rolling "Top 10 Priority" Trello list for Torus_Ops board.
When a card is completed or demoted, the next highest-priority card auto-enters the list.
Automation rules:
- Any card labeled P1 + active not in Top 10 -> move to Top 10
- Any card completed in Top 10 -> archive + promote next P1/P2
- Duplicate titles/URLs -> merge + keep higher-priority card
- Stale cards >14 days with no comments -> label stale + notify crew

## Implementation
- Local file: `10_Skills_Library/05_Operations/TRELLO_TOP10.json`
- Script: `scripts/trello_top10_sync.py`
- Cron: every 15m via `ooda_loop.py` or standalone
- Crew notification: write to `/z/MISS_PINK_INBOX` if action needed

## Board metadata to mirror from Sir Green's VOID Ops
- Lists: Backlog, Top 10, In Progress, Review, Done
- Labels: P1, P2, P3, ops, automation, crew, docker, dashboard, plugin, k8s, alert, blocker
- Custom fields: owner, target_host, status, last_updated

## Notes
- Trello API returning 401 invalid key — needs refresh from `01_Operating/Operating Paperwork/Trello_API_Credentials.md`
- Apply same structure to Torus_Ops board once auth restored
