# Obsidian Automation Guide

## Plugins Installed
- **Templater** — template engine for dynamic notes
- **Dataview** — query vault as a database
- **QuickAdd** — quick capture and note creation
- **Calendar** — calendar view for daily notes
- **Periodic Notes** — daily/weekly/monthly note creation
- **Obsidian Git** — commit/push vault changes automatically

## Templates
Located in `00_Inbox/07_Templates/`:
- Daily_Ops_Log.md
- Weekly_Review.md
- Monthly_Review.md
- Meeting_Notes.md
- Project_Note.md
- Research_Note.md
- Inventory_Log.md
- Sales_Order.md

## Task Scheduler Jobs

| Job | Schedule | Script |
|-----|----------|--------|
| Torus_Daily_Obsidian_Note | Daily 8:00 AM | obsidian_daily_note.py |
| Torus_Weekly_Obsidian_Note | Mon 8:00 AM | obsidian_weekly_note.py |
| Torus_Monthly_Obsidian_Note | 1st 8:00 AM | obsidian_monthly_note.py |
| Torus_Vault_Sync_To_GitHub | Daily 8:30 AM | vault_sync_to_github.py |
| Torus_OODA_Self_Prompt | Every 5m | ooda_self_prompt_loop.py |
| Torus_Comms_Watcher | Continuous | pinkcady_comms_watcher.py |

## QuickAdd Macros
- Daily Ops Log
- Quick Inventory Entry
- Weekly Review
- OODA Backlog Refresh

## Trello Boards
Located in `09_Projects/Trello_Boards/`:
- Torus_Ops
- Website_Rebuild
- Business_Docs

## Google Integration
- OAuth token: `C:\Users\torus\AppData\Local\hermes\google_token.json`
- Export script: `09_Projects/Scripts/Google_Drive_Export/export_google_drive.py`

## Website Integration
- Remote: `https://github.com/toruscoffeecompany/Torus_website_rebuild.git`
- Local path: `06_Website/next-storefront`
- Build command: `npm run build`
- Contact fallback: `/api/inquiries` -> `04_Products/inquiries.json`

## OODA Loop
- Script: `10_Skills_Library/05_Operations/Crew/ooda_self_prompt_loop.py`
- Output: `02_Business_Operations/Communications/Outbox/`
- Shared bus: `02_Business_Operations/Communications/Outbox/SHARED_COMMS_BUS.json`
- Auto-prompts: generated for Miss Pink and Sir Green each cycle

## Comms Watcher
- Script: `10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py`
- Log: `10_Skills_Library/05_Operations/Crew/pinkcady_comms.log`
- State: `10_Skills_Library/05_Operations/Crew/.pinkcady_comms_state.json`
- Archive: `10_Skills_Library/05_Operations/Crew/comms_archive/`

## Notes
- Do not edit Z:/Developer_Brain files directly from PINKCADY; use local mirrors.
- Use local outbox for writes; Z:/Developer_Brain/Shared_With_Pink/PINKCADY_INBOX is read-only from PINKCADY.
