# Pre-Website Local Automation Checklist

**Owner:** Miss Pink  
**Date:** 2026-08-03  
**Goal:** Complete all local automation BEFORE moving to website design

## Current State Audit
- ✅ Task Scheduler: 21 jobs
- ✅ Test suite: 10/10 PASS
- ✅ Git: clean (9 uncommitted files)
- ✅ Trello: 356 cards
- ✅ Crew: 8 personas + 10 Discord bots
- ✅ Scripts: 38 files in scripts/

## Remaining Automation Work

### 1. Git Sync
- [ ] Commit 9 uncommitted files
- [ ] Push to Torus_Ops
- [ ] Verify vault_sync_to_github.py runs cleanly
- [ ] Set up automatic git sync (Obsidian Git plugin + Task Scheduler)

### 2. Vault Cleanup
- [ ] Test vault_cleanup.py manually
- [ ] Schedule monthly vault cleanup job
- [ ] Verify __pycache__ removal works

### 3. Order Management
- [ ] Test order_manager.py with test Gmail message
- [ ] Verify Obsidian order note creation
- [ ] Verify Trello card creation for orders
- [ ] Schedule every 15 min Task Scheduler job

### 4. Inventory Sync
- [ ] Test inventory_sync.py with current inventory_master.json
- [ ] Verify website product data updates
- [ ] Schedule every 4 hours Task Scheduler job

### 5. Social Media Automation
- [ ] Test Buffer post creation (currently schema-blocked)
- [ ] Verify social_media_automation.py runs
- [ ] Schedule daily/weekly social media checks

### 6. HubSpot CRM
- [ ] Test HubSpot contact creation
- [ ] Test deal pipeline creation
- [ ] Verify hubspot_crm.py integration

### 7. Trello Sync
- [ ] Test trello_sync.py
- [ ] Schedule automatic Trello sync
- [ ] Verify all 356 cards are current

### 8. Daily Ops Automation
- [ ] Test daily_ops_automation.py
- [ ] Verify git status + alert routing
- [ ] Schedule daily 8 AM job

### 9. Marketing Automation
- [ ] Test marketing_officer.py
- [ ] Add campaign data to campaign_queue.json
- [ ] Schedule weekly marketing check

### 10. Product Photo Tracker
- [ ] Test Torus_Photo_Tracker.py
- [ ] Verify photo tracking for all 14 products
- [ ] Schedule weekly photo tracker job

### 11. Asset Validator
- [ ] Test asset_validator.py
- [ ] Verify asset validation logic
- [ ] Schedule daily asset validation

### 12. Alert Router Integration
- [ ] Verify all scripts use alert_router.py
- [ ] Test critical/warning/info routing
- [ ] Verify Gmail alerts for critical items

### 13. Bank Reconciliation
- [ ] Test bank_reconciler.py with real CSV
- [ ] Verify expense categorization
- [ ] Schedule monthly reconciliation

### 14. Dashboard Launcher
- [ ] Verify dashboard_launcher.py works
- [ ] Test Windows startup shortcut
- [ ] Verify dashboard loads on boot

### 15. Formspree Live Test
- [ ] Submit test message via contact form
- [ ] Verify email received at toruscoffeecompany@gmail.com
- [ ] Verify spam filter doesn't catch it

### 16. Website Build Verification
- [ ] Fix Next.js build error
- [ ] Verify all pages build successfully
- [ ] Test contact form end-to-end

## Verification Checklist
- [ ] All scripts tested and passing
- [ ] All Task Scheduler jobs running
- [ ] Git clean and pushed
- [ ] Trello synced
- [ ] No secrets in git
- [ ] No VOID files modified
- [ ] All integrations verified
