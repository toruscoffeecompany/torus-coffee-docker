# Obsidian Plugin Deep-Dive — Implementation Plan
_Autonomous audit + execution plan for Miss Pink's vault_
Generated: 2026-08-06
Status: READY

## Plugin inventory
- calendar
- dataview
- periodic-notes
- templater-obsidian
- quickadd
- obsidian-git
- obsidian-excalidraw-plugin
- obsidian-tasks-plugin
- table-editor-obsidian
- obsidian-style-settings
- obsidian-kanban
- obsidian-icon-folder
- smart-connections
- obsidian-outliner
- obsidian-importer
- omnisearch
- obsidian-minimal-settings
- obsidian-linter
- tag-wrangler
- obsidian-livesync
- obsidian-markmind

## Completed
- Templater templates_folder: `00_Inbox/07_Templates`
- Periodic Notes daily/weekly folder: `00_Inbox/01_Daily`
- Periodic Notes templates: `Daily_Ops_Log.md`, `Weekly_Review.md`
- QuickAdd macros imported into `.obsidian/plugins/quickadd/data.json`
- All plugin directories present; no missing-install work needed

## Next actions
1. Create `00_Inbox/01_Daily/Daily_Ops_Log.md` and `Weekly_Review.md` templates if missing
2. Enable Templater startup trigger and hotkeys for daily/weekly note creation
3. Enable Periodic Notes timeline complication and startup open
4. Enable QuickAdd macro execution on file creation
5. Enable obsidian-git autocommit/autopush for vault sync
6. Enable obsidian-livesync syncOnSave and test peer pairing
7. Enable obsidian-tasks-plugin query syntax in daily ops log
8. Add periodic vault validation job via Windows Task Scheduler
9. Wire `automation_status.json` into a Dataview dashboard in `00_Inbox/Dataview_Automation_Dashboard.md`
10. Add Templater + Periodic Notes integration tests to `10_Skills_Library/05_Operations/scripts`

## Crew asks
- Sir Green: confirm dashboard server port and webhook auth path
- Sir Azure: provide peer name for Livesync test pairing
