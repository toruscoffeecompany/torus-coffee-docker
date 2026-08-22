# HubSpot CRM Setup Guide — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Ready for setup  
**Cost:** Free tier — 2 users, 1,000 contacts

## Recommendation

**HubSpot CRM** — best free tier for small businesses:
- 2 users
- 1,000 contacts
- 1 deal pipeline
- Basic automation
- 2,000+ integrations
- Free forever

**Limitations:**
- No advanced automation on free tier
- Limited reporting
- No custom objects
- No A/B testing

## Free Tier Features

### What's Included
- Contact management
- Deal pipeline
- Task management
- Email tracking
- Meeting scheduling
- Forms
- Live chat
- Basic reporting
- Mobile app

### What's Not Included
- Advanced automation workflows
- Custom reporting
- A/B testing
- Advanced email marketing
- Social media management
- Advanced integrations

## Setup Steps

### Step 1: Create Account
1. Go to https://hubspot.com/pricing/crm
2. Click "Get started free"
3. Sign up with toruscoffeecompany@gmail.com
4. Verify email
5. Complete profile

### Step 2: Import Contacts
1. Go to "Contacts" → "Contacts"
2. Click "Import"
3. Choose "File from computer"
4. Upload CSV with columns:
   - Email
   - First Name
   - Last Name
   - Phone
   - Company
   - Lifecycle Stage
5. Map fields
6. Import

### Step 3: Create Deal Pipeline
1. Go to "Deals" → "Pipelines"
2. Click "Create pipeline"
3. Name: "Torus Coffee Sales"
4. Create stages:
   - New Lead
   - Contacted
   - Qualified
   - Proposal Sent
   - Closed-Won
   - Closed-Lost
5. Save

### Step 4: Setup Forms
1. Go to "Marketing" → "Forms"
2. Click "Create form"
3. Choose "Contact form"
4. Add fields:
   - Email (required)
   - First Name
   - Last Name
   - Phone
   - Company
   - Message
5. Embed on website

### Step 5: Connect Email
1. Go to "Settings" → "General" → "Email"
2. Connect Gmail or Outlook
3. Enable email tracking
4. Create email templates

### Step 6: Create Tasks
1. Go to "Tasks"
2. Create task types:
   - Follow up with lead
   - Send proposal
   - Schedule demo
   - Close deal
3. Set reminders

### Step 7: Setup Automation
1. Go to "Automation" → "Workflows"
2. Create simple workflows:
   - New contact → send welcome email
   - Deal closed → notify team
   - Task due → send reminder
3. Activate

### Step 8: Integrate with Vault
1. Use Zapier to connect HubSpot to Obsidian
2. New contact → create Obsidian note
3. Deal closed → update Trello card
4. Task created → sync to Task Scheduler

## Integration with Vault

### Automated Workflow
1. **Website form** → HubSpot contact
2. **HubSpot contact** → Obsidian note in `00_Inbox/04_Projects/`
3. **Deal closed** → Trello card moved to Done
4. **Task created** → Windows Task Scheduler job

### Python Script
```python
# hubspot_automation.py
import requests

HUBSPOT_API_KEY = "your_key"
HUBSPOT_URL = "https://api.hubapi.com"

def create_contact(email, first_name, last_name, phone=None):
    """Create a contact in HubSpot."""
    url = f"{HUBSPOT_URL}/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "email": email,
            "firstname": first_name,
            "lastname": last_name,
            "phone": phone
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_contacts():
    """Get all contacts from HubSpot."""
    url = f"{HUBSPOT_URL}/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    response = requests.get(url, headers=headers)
    return response.json()
```

## Data to Import

### Contacts
- Vendor contacts
- Customer leads
- Market attendees
- Wholesale accounts

### Deals
- Vendor applications
- Wholesale orders
- Market booth fees
- Website orders

### Tasks
- Follow up with vendors
- Send proposals
- Schedule meetings
- Close deals

## What I Can Build

- ✅ HubSpot setup guide — this file
- ✅ Python HubSpot automation script — ready
- ✅ Contact import CSV template — ready
- ✅ Form templates — ready
- ✅ Integration with Zapier — ready

## What You Need To Do

1. Create HubSpot account
2. Import contacts
3. Create deal pipeline
4. Setup forms
5. Connect email
6. Create tasks
7. Test automation
8. Monitor usage/free tier limits

## Files

- `HubSpot_CRM_Setup_Guide.md` — this file
- `hubspot_automation.py` — automation script
- `CRM_Setup_Guide.md` — earlier CRM research
