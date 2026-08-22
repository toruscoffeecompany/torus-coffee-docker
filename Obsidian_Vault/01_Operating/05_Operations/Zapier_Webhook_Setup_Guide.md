# Zapier Webhook Setup Guide — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Ready to follow step-by-step  
**Cost:** Free tier (5 Zaps, 100 tasks/month)

## What Is A Zapier Webhook?

A webhook is a URL that Zapier gives you. When something sends data to that URL, Zapier catches it and runs your automation. Think of it as a digital mailbox: you drop data in, Zapier picks it up and does work with it.

## Step-by-Step: Create Your First Zapier Webhook

### Step 1: Log Into Zapier
1. Go to **zapier.com**
2. Click **Sign in** (top right)
3. Use **toruscoffeecompany@gmail.com**
4. Enter password
5. Click **Sign in**

**Expected result:** You see your Zapier dashboard with "My Zaps" on the left.

---

### Step 2: Create A New Zap
1. Click the big **+ Create** button (top left)
2. Click **Zaps** from the dropdown
3. You should now see "1. Trigger" and "2. Action"

**Expected result:** A blank Zap editor with "Trigger" selected.

---

### Step 3: Choose Webhook As Trigger
1. In the search bar under "Trigger", type: **Webhooks**
2. Look for **"Webhooks by Zapier"** (official, by Zapier)
3. Click it
4. Under "Event", select **"Catch Hook"**
5. Click **Continue**

**Expected result:** Zapier shows you a webhook URL that looks like:
`https://hooks.zapier.com/hooks/catch/1234567/abcdefg/`

---

### Step 4: Copy The Webhook URL
1. Look for the field labeled **"Webhook URL"**
2. It will be a long URL starting with `https://hooks.zapier.com/...`
3. Click **Copy** button next to it
4. **Paste it somewhere safe** (text file, notepad, etc.)

**This URL is your webhook.** Give this to me and I'll wire it into the automation.

---

### Step 5: Test The Webhook (Optional But Recommended)
1. Open a new browser tab
2. Go to: **webhook.site** (free tool)
3. Copy the temporary URL it gives you
4. Go back to Zapier
5. In the "Test" section, paste the webhook.site URL
6. Click **Test trigger**
7. Go back to webhook.site — you should see the test data arrive

**This confirms your webhook works before we use it in production.**

---

### Step 6: Add An Action (For Testing)
1. Click **"+" to add an Action step**
2. Search for any app you use (e.g., **Gmail**, **Slack**, **Trello**)
3. Choose an action (e.g., **"Send Email"** for Gmail)
4. Connect the account
5. Configure the action to use data from the webhook
6. Click **Continue**
7. Click **Test step**

**Expected result:** The action runs successfully with test data.

---

### Step 7: Name And Turn On Your Zap
1. Click the **Untitled Zap** name at the top
2. Rename it to: **"Torus Coffee — Webhook Test"**
3. Click the toggle at the bottom to turn it **ON** (should turn green)
4. Click **"X"** to exit

**Expected result:** Zap is live and listening for webhook requests.

---

## What To Do Next

1. **Copy the webhook URL** from Step 4
2. **Paste it here** in chat
3. I'll wire it into `zapier_automation.py`
4. I'll test it by sending a test payload
5. We'll update Trello and commit to git

## Common Issues

| Problem | Solution |
|---------|----------|
| Can't find "Catch Hook" | Search "Webhooks by Zapier" — it's the official Zapier app |
| Webhook URL not showing | You may need to click "Continue" after selecting "Catch Hook" |
| Test fails with 401/403 | The webhook URL is wrong — regenerate it |
| Zap won't turn on | You need at least 1 action step configured |

## Files

- `Zapier_Webhook_Setup_Guide.md` — this file
- `zapier_automation.py` — automation script
- `Zapier_Integration_Guide.md` — full Zapier integration guide

---

## Next Step

**Paste your webhook URL here** and I'll take it from there.
