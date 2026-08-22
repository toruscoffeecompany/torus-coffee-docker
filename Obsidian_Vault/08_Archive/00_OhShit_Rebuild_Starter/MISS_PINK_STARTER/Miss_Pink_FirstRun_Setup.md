# Miss Pink — First-Run Hermes Setup

## Step 1 — Verify vault
Open Obsidian vault at `D:\Work\Torus Coffee Company LLC`

## Step 2 — Verify plugins
Confirm 5 plugins active: Templater, Dataview, QuickAdd, Calendar, Periodic Notes

## Step 3 — Verify templates
Confirm 13 templates in `00_Inbox/07_Templates/`

## Step 4 — Verify Task Scheduler
```powershell
schtasks /query /fo LIST /v | findstr "Torus_"
```

## Step 5 — Verify Trello
Open https://trello.com/b/cZFvOC8l/torusops

## Step 6 — Verify GitHub
```powershell
cd "D:\Work\Torus Coffee Company LLC"
git remote -v
```

## Step 7 — Report
Drop report in `REPORTS/` with status of all checks.
