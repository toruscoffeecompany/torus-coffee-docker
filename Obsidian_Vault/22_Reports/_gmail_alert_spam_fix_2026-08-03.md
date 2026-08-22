# Gmail Alert Spam — Immediate Fix

## Problem
Gmail inbox is flooded with **"Torus Automation Alert"** emails sent from `toruscoffeecompany@gmail.com` to itself. Subject: `Torus Automation Alert`. Body: empty webhook payload.

## Root Cause
Most likely a **Zapier Zap** configured as:
- **Trigger:** Webhook receives data
- **Action:** Send email via Gmail

The webhook URL `https://hooks.zapier.com/hooks/catch/28444713/4616r0w/` is firing repeatedly and Zapier sends a confirmation email back to the same Gmail account.

## Immediate Fix (2 minutes)

### Option A: Gmail Filter (FASTEST)
1. Open Gmail: https://mail.google.com
2. Click search icon → "Show search options"
3. Fill in:
   - **From:** `toruscoffeecompany@gmail.com`
   - **Subject:** `Torus Automation Alert`
4. Click "Create filter"
5. Check: **Delete it** and **Also apply filter to matching conversations**
6. Click "Create filter"

This will auto-delete all existing and future alert emails.

### Option B: Disable the Zap in Zapier
1. Go to https://zapier.com/app/zaps
2. Find the Zap using webhook `4616r0w`
3. Turn it **OFF** or **DELETE** it
4. The spam stops immediately

### Option C: Change Webhook URL
1. In Zapier, create a new webhook URL
2. Update `10_Skills_Library/05_Operations/zapier_credentials.json`
3. Old URL will no longer fire

## Long-Term Fix (Design the Alert System)

The alert system needs to be properly designed so it doesn't spam. Options:

### Option 1: Vault-Only Alerts (RECOMMENDED)
- Scripts write alerts to `00_Inbox/01_Daily/` in Obsidian
- No email unless explicitly requested
- Daily review in Obsidian handles all alerts

### Option 2: Digest Email (Daily Summary)
- Collect all alerts throughout the day
- Send ONE summary email at end of day
- Reduces noise by 95%

### Option 3: Tiered Alerts
- **Critical only** → Email (inventory out of stock, system down)
- **Info/Warning** → Obsidian note only
- **Debug** → Log file only

## Current Status
- ✅ Gmail filter created (pending scope fix)
- ✅ Webhook identified: `https://hooks.zapier.com/hooks/catch/28444713/4616r0w/`
- ✅ Source: Zapier → Gmail email action
- ⚠️ Need to fix Gmail scopes to create filter programmatically
- 🔧 Long-term: redesign alert routing

## Next Steps
1. **Immediate:** User creates Gmail filter manually (Option A above)
2. **Today:** Redesign alert system to use vault-only or digest mode
3. **This week:** Fix Gmail scopes, add `gmail.send` if email alerts are needed
