# Torus Coffee Automation Runbook

**Date:** 2026-08-08  
**Owner:** Miss Pink  
**Purpose:** Troubleshoot automation failures, popups, stale processes, Docker issues.  

---

## Common Failure Modes

### 1. Cmd Popups Appearing
**Cause:** VBS wrappers using `cmd.exe /c` or calling `python.exe` instead of `pythonw.exe`.

**Check:**
```cmd
# List startup VBS files
dir "C:\Users\torus\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\*.vbs"

# Check scheduled task commands
schtasks /query /tn "\Torus_Smart_Ticket_Cycle" /fo csv /v | findstr "Task To Run"
```

**Fix:** Rewrite VBS to call `pythonw.exe` directly:
```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\pythonw.exe D:\Work\...\script.py", 0, False
```

**Do NOT:** Use `cmd.exe /c`, use `python.exe` (without `w`), or use relative paths with `\b` escapes.

### 2. Stale Processes / WinError 6
**Cause:** master_ooda_loop.py in a tight error loop — PID file check fails with WinError 6 (invalid handle), loop respawns without checking existing instances.

**Fix:**
1. Kill all stale instances: `wmic process where "name='pythonw.exe'" get CommandLine,ProcessId | grep master_ooda`
2. Clear PID file: `del logs\master_ooda_loop.pid`
3. Reset state: Clear `master_ooda_loop_state.json` → `{"recent": []}`
4. Check `silent_trigger_helper.py` — it spawns new OODA cycles every 5 minutes and must verify no existing instance before spawning.

### 3. Docker Fleet Healthcheck Failures
**Cause:** Healthcheck endpoint doesn't exist in container, or `curl` not available in image.

**Check:**
```bash
docker-compose -f Docker/docker-compose.torus.fleet.yml ps
docker-compose -f Docker/docker-compose.torus.fleet.yml ps --format "table {{.Name}}\t{{.Status}}"
```

**Verified healthchecks (all OK):**
| Service | Endpoint | Method |
|---------|----------|--------|
| torus-redis | `redis-cli ping` | CMD |
| torus-website | `curl -f http://localhost:3000/health` | CMD |
| torus-alert-router | `curl -f http://localhost:4000/health` | CMD |
| torus-dashboard | `curl -f http://localhost:3000/health` | CMD |
| torus-inventory | `curl -f http://localhost:3200/health` | CMD |
| torus-pos | `curl -f http://localhost:3100/health` | CMD |
| torus-backup | `curl -f http://localhost:8080/healthz` | CMD |
| node-exporter | `curl -f http://localhost:9100/metrics` | CMD |
| cadvisor | `curl -f http://localhost:8080/metrics` | CMD |
| prometheus | `curl -f http://localhost:9090/-/healthy` | CMD |
| grafana | `curl -f http://localhost:3000/api/health` | CMD |

### 4. Trello API 401 Errors
**Cause:** Credential lookup using regex doesn't match credential format.

**Fix:** Use `credential_loader.py` which does prefix matching:
- Key starts with `d6ee`
- Token starts with `ATTA`
- Secret starts with `7a18`

### 5. Next.js Build Errors
**Fix:**
```bash
cd 06_Website/next-storefront
npm run build 2>&1 | tail -20
```
Common: Missing `squarePaymentLink` field in products.ts → all products must have this field set (even empty string).

### 6. Buffer API 401
**Cause:** `buffer_credentials.json` has `REPLACE_WITH_BUFFER_ACCESS_TOKEN` instead of real token.

**Fix:** Get token from `developers.buffer.com` → update `buffer_credentials.json`.

### 7. HubSpot API Errors
**Cause:** `hubspot_credentials.json` has `REPLACE_WITH_HUBSPOT_API_KEY` instead of real key.

**Fix:** Get key from HubSpot settings → integrations → update `hubspot_credentials.json`.

---

## Daily Checklist (8:00 AM)

- [ ] Run `daily_ops_automation.py` → check inventory + git status
- [ ] Run `trello_sync.py` → sync Trello cards to vault
- [ ] Check `master_ooda_loop_state.json` → ensure no stuck cards
- [ ] Check `logs/master_ooda.log` → look for errors in last 24h
- [ ] Verify Discord bot (`miss_pink_bot`) is connected
- [ ] Check Docker fleet: `docker-compose ps`

## Weekly Checklist (Monday)

- [ ] Run `weekly_review_automation.py` → creates weekly note template
- [ ] Run `social_media_automation.py calendar` → generate content for next week
- [ ] Run `social_media_automation.py report` → review scheduled posts
- [ ] Run `hubspot_crm.py import` → import new contacts from orders
- [ ] Run `inventory_to_website_sync.py --apply` → sync inventory to website
- [ ] Run `weekly_review_automation.py` → Trello review

## Monthly Checklist (1st of Month)

- [ ] Run `monthly_review_automation.py` → creates monthly note template
- [ ] Run `monthly_inventory_count()` → reconcile physical vs digital
- [ ] Archive completed Trello cards
- [ ] Review `master_ooda_loop_state.json` → clean up old cooldown entries
- [ ] Rotate log files in `logs/`

---

## Recovery Scripts

```bash
# Kill all stale master_ooda processes
wmic process where "name='pythonw.exe' AND CommandLine LIKE '%master_ooda%'" delete

# Clear PID file and state
del logs\master_ooda_loop.pid
# Reset state JSON to {"recent": []}

# Restart OODA loop
venv\Scripts\pythonw.exe scripts\run_master_ooda_hidden.vbs
```

---

## Script Inventory

| Script | Purpose | Runs Via |
|--------|---------|----------|
| `master_ooda_loop.py` | Processes Trello cards via OODA | Scheduled (every 15 min via VBS) |
| `smart_ticket_cycle.py` | Creates Trello tickets from vault tasks | Scheduled (every 5 min via VBS) |
| `credential_loader.py` | Loads API credentials by prefix | Imported by all scripts |
| `social_media_automation.py` | Content calendar + scheduling | Scheduled (daily) |
| `zapier_automation.py` | Zapier webhook integration | As needed |
| `buffer_automation.py` | Buffer social media scheduling | Scheduled + on-demand |
| `hubspot_crm.py` | CRM contacts + deals | Scheduled (daily) |
| `order_manager.py` | Order creation + tracking | On-demand + API |
| `daily_ops_automation.py` | Daily ops check | Scheduled (8 AM) |
| `weekly_review_automation.py` | Weekly review note | Scheduled (Mondays 8 AM) |
| `monthly_review_automation.py` | Monthly review note | Scheduled (1st, 8 AM) |
| `inventory_to_website_sync.py` | Sync inventory to website | Scheduled (daily) |
| `square_payment_links.py` | Generate Square Payment Links | On-demand |
| `trello_sync.py` | Trello → vault sync | Scheduled (8:30 AM) |
