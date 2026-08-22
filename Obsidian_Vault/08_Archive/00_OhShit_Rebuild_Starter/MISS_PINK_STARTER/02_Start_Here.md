# 02 — Start Here (Miss Pink Activation Sequence)

## STEP 1 — Read the laws
- `00_Pirate_Rules.md` — identity, chain of command, OPSEC.
- `01_Biz_Docs_Index.md` — current state of all Torus systems.
- `DEV_MODE_SETUP.md` — local toolchain requirements.

## STEP 2 — Verify vault is accessible
```powershell
# Open Obsidian vault
explorer "D:\Work\Torus Coffee Company LLC"
```

## STEP 3 — Verify plugins are active
Open Obsidian → Settings → Community Plugins. Confirm:
- [x] Templater
- [x] Dataview
- [x] QuickAdd
- [x] Calendar
- [x] Periodic Notes

## STEP 4 — Verify Task Scheduler jobs
```powershell
schtasks /query /fo LIST /v | findstr "Torus_"
```
Expected: 5 jobs (Daily, Weekly, Monthly, GitHub Sync, SQUIDSTATION Backup)

## STEP 5 — Verify Trello boards
Open in browser:
- https://trello.com/b/cZFvOC8l/torusops
- https://trello.com/b/JmUh5kJA/businessdocs
- https://trello.com/b/orPSpaRA/websiterebuild

## STEP 6 — Report status
Drop a report in `REPORTS/` with:
- Vault accessible? Yes/No
- Plugins active? Yes/No
- Trello connected? Yes/No
- Blockers? List any
