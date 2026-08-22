# Square Developer Setup Guide (Free Tier)

**Status:** Not yet configured  
**Date:** 2026-08-03  
**Free Tier:** Yes — Square free tier includes in-person + online payments

## What You Need to Do

### 1. Create Square Account
1. Go to https://squareup.com/signup
2. Sign up as "Torus Coffee Company LLC"
3. Use business email: toruscoffeecompany@gmail.com
4. Verify email

### 2. Enable Square Online
1. In Square Dashboard → Settings → Business
2. Enable "Online Store" (free)
3. This gives you a free hosted checkout page

### 3. Get API Credentials
1. Go to https://developer.squareup.com/apps
2. Create new application: "Torus Coffee Website"
3. Select "Sandbox" for testing (free)
4. Copy these values:
   - Application ID
   - Application Secret
   - Sandbox Access Token

### 4. Free Tier Limits
- In-person payments: 2.9% + 10¢ per transaction
- Online payments: 2.9% + 10¢ per transaction
- No monthly fees
- Free hosted checkout page
- Free inventory tracking

### 5. Integration Options (Free)
- **Option A: Square Payment Links** — Easiest, no coding
  - Create payment link in Square Dashboard
  - Add link to website "Buy" buttons
  - No API needed
  
- **Option B: Square Checkout API** — More control
  - Use Square Checkout API (free)
  - Requires backend endpoint
  - Can use Vercel serverless functions

### 6. What Miss Pink Needs From You
1. Square account login (or create one)
2. Confirm business address for GTIN
3. Confirm bank account for deposits
4. Approve which products to list first

### 7. Next Steps
1. [ ] Create Square account
2. [ ] Enable Online Store
3. [ ] Get Sandbox credentials
4. [ ] Test payment flow
5. [ ] Switch to Production credentials
6. [ ] Update website with Square links

## Security Notes
- Store credentials in `.env` only, never commit
- Use Sandbox for testing, Production for live
- Rotate tokens quarterly

## Related
- `06_Website/Design/Design Docs/04 Checkout Shipping Customer Accounts and Orders v1.txt`
- `06_Website/next-storefront/.env.example`
