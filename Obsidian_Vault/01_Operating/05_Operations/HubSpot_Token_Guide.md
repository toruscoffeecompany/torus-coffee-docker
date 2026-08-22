# HubSpot Private App Token — Visual Guide

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Token retrieval guide

## Exact Steps With Visual Cues

### Step 1: Log Into HubSpot
1. Go to **hubspot.com**
2. Click **Log in** (top right corner)
3. Use your Torus Coffee email
4. You should see the HubSpot dashboard

### Step 2: Open Settings
1. Look at the **top navigation bar**
2. Find the **gear icon** ⚙️ (usually top right, next to your profile picture)
3. Click it

**What you should see:**
- Left sidebar with categories
- Search bar at top that says "Search settings"

### Step 3: Find Private Apps
1. In the left sidebar, scroll down
2. Look for **Integrations** (may be under "Data Management" or "Objects")
3. Click **Integrations**
4. Look for **Private Apps** in the submenu
5. Click **Private Apps**

**What you should see:**
- Page title: "Private Apps"
- Button: **"Create a private app"** (blue button, top right)

### Step 4: Create Or Find Your App
**If you already created "Torus Coffee Automation":**
1. Find it in the list
2. Click on it
3. Look for **"Access token"** section
4. Click **Show** or **Copy**

**If you haven't created it yet:**
1. Click **"Create a private app"**
2. Fill in:
   - **Name:** `Torus Coffee Automation`
   - **Description:** `Automation for Torus Coffee Company`
3. Click **Next**
4. Select scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
5. Click **Create app**

### Step 5: Copy The Token
**This is the critical part.**

After creating the app, HubSpot shows:
- **Access token** field
- Token looks like: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**To copy:**
1. Click the **Copy** button next to the token
2. Or click **Show** then highlight and copy
3. **Paste it here immediately**

## Common Issues

| Problem | Solution |
|---------|----------|
| Can't find "Private Apps" | You need admin access. Ask the account owner. |
| Token only shows once | If you lose it, click "Rotate access token" to generate new one |
| Token starts with `na2-` not `pat-` | You're looking at the wrong field. Look for "Access token" specifically |
| Getting 401 errors | Token is expired or malformed. Generate a new one. |

## What The Token Should Look Like

**Correct format:**
```
pat-na1-EXAMPLE-REPLACE-WITH-YOUR-TOKEN
```

**NOT:**
```
na2-7206-34e9-453a-91fd-7661c5b98a82  ← This is missing the "pat-" prefix and hub ID
```

## Next Step

Once you copy the correct token, paste it here. I'll test it immediately.
