# Formspree Setup Guide — Torus Coffee Company Contact Form

## What This Does
Routes website contact form submissions to Gmail without backend code.

## Setup Steps

### 1. Create Formspree Account
1. Go to **https://formspree.io/**
2. Sign up with **toruscoffeecompany@gmail.com**
3. Verify email

### 2. Create New Form
1. Click **"New Form"**
2. Name: `Torus Coffee Contact Form`
3. Copy the endpoint URL (looks like: `https://formspree.io/f/abc123`)

### 3. Add to Vault Credentials
Create `10_Skills_Library/05_Operations/formspree_credentials.json`:
```json
{
  "formspree_form_id": "abc123",
  "endpoint": "https://formspree.io/f/abc123"
}
```

### 4. Add to Website `.env`
Create `06_Website/website/.env.local`:
```
CONTACT_FORMSPREE_URL=https://formspree.io/f/abc123
```

### 5. Test
1. Go to https://toruscoffeecompany.com/contact
2. Fill out form
3. Submit
4. Check Gmail for submission

## Free Tier Limits
- **50 submissions/month** — enough for launch
- **Upgrade:** $9/month for 1,000 submissions

## What Happens After Setup
1. Customer submits form on website
2. Formspree sends email to toruscoffeecompany@gmail.com
3. Zapier watches Gmail for new order emails
4. Trello card created automatically
5. Obsidian daily note updated

## Troubleshooting
- **No email received:** Check spam folder
- **Form not submitting:** Verify endpoint URL in `.env.local`
- **CORS errors:** Formspree handles this automatically

## Status
- ⏳ Awaiting Formspree account creation
- ✅ Contact API route built and ready
- ✅ Website contact page ready
