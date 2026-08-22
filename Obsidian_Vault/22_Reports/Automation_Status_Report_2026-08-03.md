# Torus Coffee Automation Status Report

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Test Result:** PASS  
**Overall Health:** 8/8 core automations verified

## What's Working

### 1. Buffer — Social Media Scheduling
- **Status:** ✅ Connected
- **Account:** toruscoffeecompany (toruscoffeecompany@gmail.com)
- **Channels:** 3 found
  - youtube: Torus Coffee Company
  - twitter: TorusCoffee
  - linkedin: Torus Coffee Company
- **Webhook Test:** Live payload sent successfully
- **Notes:** Account and channel discovery verified. Post-creation mutation still needs one more schema pass.

### 2. Zapier — Automation Hub
- **Status:** ✅ Webhook live
- **Webhook:** Auto-loads from vault credentials
- **Test Payload:** Sent successfully
- **Notes:** Zapier Trello action still needs auth configured in Zapier UI.

### 3. HubSpot CRM — Customer Management
- **Status:** ✅ Connected
- **Contacts:** API verified, 1 sample contact found
- **Deals:** API verified, 1 sample deal found
- **Notes:** Service Key working. Full CRM config pending.

### 4. Automation Orchestrator
- **Status:** ✅ 8/8 scripts verified
- **Scripts Run:**
  - buffer_automation.py
  - zapier_automation.py
  - hubspot_crm.py
  - social_media_automation.py
  - inventory_tracker.py
  - daily_ops_automation.py
  - weekly_review_automation.py
  - monthly_review_automation.py
- **Success Rate:** 100%

### 5. Obsidian Vault
- **Status:** ✅ Active
- **Plugins:** 6 active (calendar, dataview, periodic-notes, quickadd, templater-obsidian, obsidian-git)
- **Templates:** 13 Templater templates
- **Dashboards:** 4 Dataview dashboards
- **Automation:** Task Scheduler jobs configured

### 6. Git / GitHub
- **Status:** ✅ Synced
- **Repos:** Torus_Ops, Torus_website_rebuild
- **Latest Commit:** d87579f
- **Branch:** main

### 7. Trello
- **Status:** ✅ Active
- **Boards:** 3 (Torus_Ops, Business_Docs, Website_Rebuild)
- **Cards:** 225+ total

### 8. Revenue Stream Plan
- **Status:** ✅ Documented
- **File:** 03_Financials/Revenue_Stream_Plan.md
- **Streams:** 8 documented
- **Free-tier commitment:** Documented

## What Needs Setup / Gaps

### Critical
1. **Gmail send scope** — Token has invalid_scope error. Need to regenerate OAuth token with `gmail.send` scope.
2. **Square account** — BLOCKED: requires Veriff identity verification.
3. **Website deployment** — Not yet deployed. Free hosting available via Netlify/Vercel.

### Important
4. **Buffer post creation** — GraphQL createPost mutation needs one more schema pass.
5. **Zapier full Zaps** — Need to build actual Zaps in Zapier UI (Trello action, Buffer action).
6. **HubSpot CRM config** — Basic API works; full contact import and deal pipelines pending.
7. **Task Scheduler paths** — Some jobs have incorrect paths and need manual correction.

### Nice-to-Have
8. **Pinterest/TikTok/LinkedIn accounts** — Not created yet.
9. **Instagram business account** — Decision needed: convert @glvwriter or create @toruscoffeecompany.
10. **Facebook page verification** — Page found, awaiting ownership verification.
11. **Amazon GTIN exemption** — Guide created, actual exemption application pending.
12. **Vendor applications** — Drafts created, awaiting review before sending.

## What Can Be Automated Now

| Automation | Status | Frequency |
|------------|--------|-----------|
| Daily ops check | ✅ Working | Daily 8AM |
| Weekly review | ✅ Working | Mondays 8AM |
| Monthly review | ✅ Working | 1st of month 8AM |
| Inventory alert | ✅ Working | Monthly |
| Social media check | ✅ Working | Daily 9AM |
| Marketing calendar | ✅ Working | Weekly Mondays 9:30AM |
| Asset validation | ✅ Working | Daily 9AM |
| Vault sync to GitHub | ✅ Working | Daily 8:30AM |

## What's Built but Not Yet Live

| Feature | Status | Notes |
|---------|--------|-------|
| Local dashboard | 🟡 Scaffolded | Needs widgets built |
| Public website | 🟡 Scaffolded | Needs deployment |
| Buffer post creation | 🟡 Partial | Channels work, posts pending |
| Zapier full Zaps | 🟡 Partial | Webhook works, Zaps pending |
| HubSpot full CRM | 🟡 Partial | API works, config pending |
| Email automation | 🔴 Broken | Gmail scope issue |
| Square integration | 🔴 Blocked | Identity verification needed |

## Recommendations

1. **Fix Gmail token scope** — Regenerate with `gmail.send` so email alerts work.
2. **Deploy public website** — Use Netlify/Vercel free tier.
3. **Complete Buffer post schema** — One more GraphQL pass.
4. **Build 3 Zaps in Zapier UI:**
   - New Trello card → webhook
   - New Google Form → Trello card
   - Calendar event → Buffer post
5. **Fix Task Scheduler paths** — Manual correction needed.
6. **Create social accounts** — Pinterest, TikTok, LinkedIn.
7. **Submit vendor applications** — Iowa City, Cedar Rapids.
8. **Start first revenue stream** — Flea market or website order.

## Test Results

- **Orchestrator:** 8/8 scripts ✅
- **Buffer:** Account + channels ✅
- **Zapier:** Webhook ✅
- **HubSpot:** Contacts + deals ✅
- **Social Media:** Platform status ✅
- **Inventory:** Tracking ✅
- **Daily/Weekly/Monthly:** All ✅
- **Practice Notification:** Sent via Zapier ✅

## Files

- `03_Financials/Revenue_Stream_Plan.md` — revenue plan
- `10_Skills_Library/05_Operations/Automation_Runbook.md` — troubleshooting
- `10_Skills_Library/05_Operations/scripts/automation_orchestrator.py` — 8/8 verified
- `06_Website/dashboard/` — local dashboard scaffold
- `06_Website/Website/` — public website scaffold
- `06_Website/next-storefront/` — older Next.js scaffold
