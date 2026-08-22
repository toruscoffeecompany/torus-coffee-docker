# Zapier/Make Integration Guide — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Ready for setup  
**Cost:** Free tier

## Recommendation

**Zapier** — easiest UI, most integrations, 5 free zaps  
**Make** — more powerful, 1,000 free operations/month

**Decision:** Start with Zapier free tier. Upgrade to Make if we need more volume.

## Free Tier Limits

### Zapier
- **5 Zaps** (automation workflows)
- **100 tasks/month** (1 task = 1 action)
- **15-minute update interval** (checks every 15 mins)
- **Single-step Zaps** only

### Make
- **1,000 operations/month**
- **5-minute update interval**
- **Multi-step scenarios**
- **More complex logic**

## Use Cases for Torus Coffee Company

### 1. Vault → Trello Sync
**Trigger:** New Trello card created  
**Action:** Create Obsidian note in `00_Inbox/04_Projects/`  
**Frequency:** Real-time via webhook

### 2. Social Media → Vault
**Trigger:** New Instagram/Twitter post  
**Action:** Save screenshot + metadata to `06_Growth_Marketing/Social_Media/`  
**Frequency:** Daily

### 3. Inventory → Social Media
**Trigger:** Inventory file updated in Google Sheets  
**Action:** Draft social media post for new product  
**Frequency:** Weekly

### 4. Vendor Application → Vault
**Trigger:** Vendor application submitted (Google Form)  
**Action:** Create note in `09_Projects/Vendor_Applications/`  
**Frequency:** Real-time

### 5. Website Form → CRM
**Trigger:** Contact form submitted on website  
**Action:** Create contact in HubSpot CRM  
**Frequency:** Real-time

### 6. Market Event → Social Media
**Trigger:** Event added to Google Calendar  
**Action:** Create social media post draft  
**Frequency:** Weekly

## Setup Steps

### Step 1: Create Zapier Account
1. Go to https://zapier.com/signup
2. Sign up with toruscoffeecompany@gmail.com
3. Verify email
4. Complete profile

### Step 2: Create First Zap
**Example: Trello → Obsidian**

1. **Trigger:** Trello
   - App: Trello
   - Trigger: New Card
   - Board: Torus_Ops
   - List: To_Do

2. **Action:** Webhooks by Zapier
   - Action: POST
   - URL: (future webhook endpoint)
   - Payload: Card name, description, URL

3. **Test:** Create test card in Trello

### Step 3: Create Obsidian Webhook Receiver
**Future:** Python script to receive webhooks and create notes

```python
# webhook_receiver.py (future)
from flask import Flask, request
import os

app = Flask(__name__)
VAULT = r"D:\Work\Torus Coffee Company LLC"

@app.route('/webhook/trello', methods=['POST'])
def trello_webhook():
    data = request.json
    card_name = data.get('name', 'Untitled')
    
    # Create Obsidian note
    note_path = os.path.join(VAULT, "00_Inbox", "04_Projects", f"{card_name}.md")
    with open(note_path, 'w') as f:
        f.write(f"# {card_name}\n\nCreated from Trello card.\n")
    
    return {'status': 'ok'}
```

### Step 4: Connect Google Services
1. **Google Drive** — auto-sync files to vault
2. **Google Sheets** — inventory, CRM, forms
3. **Google Calendar** — market events, tasks

### Step 5: Connect Social Media
1. **Instagram** — monitor posts
2. **Twitter/X** — monitor mentions
3. **YouTube** — monitor uploads
4. **Facebook** — monitor page activity

## Free Automation Recipes

### Recipe 1: Trello → Obsidian Note
- **Trigger:** New Trello card in To_Do
- **Action:** Create markdown note in vault
- **Cost:** Free

### Recipe 2: Google Form → Trello Card
- **Trigger:** New Google Form response
- **Action:** Create Trello card
- **Cost:** Free

### Recipe 3: Email → Obsidian Note
- **Trigger:** New email to admin@toruscoffeecompany.com
- **Action:** Create note in 00_Inbox
- **Cost:** Free

### Recipe 4: Calendar Event → Task
- **Trigger:** New Google Calendar event
- **Action:** Create Trello card + Obsidian note
- **Cost:** Free

### Recipe 5: Inventory Alert → Social Media Draft
- **Trigger:** Inventory item below threshold
- **Action:** Draft social media post
- **Cost:** Free

## What I Can Build

- ✅ Zapier setup guide — this file
- ✅ Make setup guide — next
- ✅ Webhook receiver script — future
- ✅ Google Form templates — ready
- ✅ Automation recipes — 5 ready
- ✅ Integration scripts — ready

## What You Need To Do

1. Create Zapier/Make account
2. Connect Google account
3. Connect Trello account
4. Test first Zap
5. Monitor usage/free tier limits

## Files

- `Zapier_Integration_Guide.md` — this file
- `Make_Integration_Guide.md` — Make alternative
- `webhook_receiver.py` — future webhook endpoint
