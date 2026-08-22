# Admin Runbook — Miss Pink (Torus Coffee Company)
**Date:** 2026-08-04  
**Audience:** Miss Pink (admin)  
**Purpose:** Finish remaining setup so Act phase goes live.

---

## Before You Start
1. Open `D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\` in File Explorer.
2. All three batch files below require **Administrator** privileges — right-click → *Run as administrator*.
3. Seats: `torus` user, `PINKCADY` host.

---

## Step 1 — Register 3 Scheduled Jobs
These scripts create the Task Scheduler entries that run automatically.

| Batch File | What It Does | Schedule |
|------------|-------------|----------|
| `register_pinkcady_watcher_task.bat` | Starts the Z: drive inbox watcher | Every 10 min |
| `register_misspink_auto_prompt.bat` | Generates prompts to Sir Green | Every 15 min |
| `register_sirgreen_auto_prompt.bat` | Generates prompts to Miss Pink | Every 15 min |

**Action:** Run each batch file once. If `Access Denied` appears, right-click → *Run as administrator*.  
**Verify:** Open Task Scheduler (`taskschd.msc`) and confirm tasks appear under `Pinkcady_Comms_Watcher`, `Miss_Pink_Auto_Prompt`, `Sir_Green_Auto_Prompt`.

---

## Step 2 — Run Secrets Intake
The alert router and Gmail integrations are blocked until secrets are validated.

**Action:** Open a terminal in `10_Skills_Library\05_Operations` and run:
```
python scripts\secrets_intake.py
```

**Provide:**
1. Discord webhook URL (from Server Settings → Integrations → Webhooks).
2. Gmail app password (from myaccount.google.com/apppasswords).
3. Backup path (recommended: `D:/backups` or `Z:/backups`).

**Result:** A report is saved to `10_Skills_Library\05_Operations\logs\secrets_intake_report.json`.  
- If **ALL VALID** → hand off to Captain for secure storage.  
- If **INVALID** → fix format and re-run.

OPSEC: This script never writes plaintext secrets. Only masked values and SHA-256 hashes are saved.

---

## Step 3 — Fix Failing Inventory Sync
`Torus_Inventory_Sync` returned **Last Result: 1**.

**Action:** Run the existing batch to test manually:
```
python scripts\inventory_sync.py
```
If it errors, share the log output with Sir Green. Once fixed, right-click the `Torus_Inventory_Sync` task in Task Scheduler → *Run* and confirm **Last Result: 0x0**.

---

## Step 4 — Start Docker Alert Router
The alert router container is stopped.

**Action:** In Docker Desktop, start the `torus-alert-router` container.  
If not defined, run:
```
docker compose -f "D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\docker-compose.yml" up -d
```
After startup, paste the validated webhook URL and app password into:
- `Docker/torus-alert-router/config/discord.json`
- `Docker/torus-alert-router/config/gmail.json`
Then set `"enabled": true` in both.

---

## Step 5 — Verify End-to-End
1. Send a test alert POST to `http://localhost:8000/alert` with severity `critical` and confirm Discord/Gmail fires.
2. Drop a `.msg.md` file into `Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX` and confirm the watcher replies within 10 min.
3. Confirm auto-prompt files appear in `02_Business_Operations\Communications\Outbox`.

---

## Escalation
If any step fails, update Trello card `6a71b462b21cd08f9f3f6eb9` with the error and tag Captain.
