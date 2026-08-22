# Buffer Setup Guide — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Ready for setup  
**Cost:** Free tier — 3 channels, 10 scheduled posts per channel

## Recommendation

**Buffer** — best free tier for small businesses:
- 3 social channels
- 10 scheduled posts per channel
- Basic analytics
- Free forever

**Limitations:**
- No Instagram Stories scheduling
- No TikTok support
- No advanced analytics
- 15-minute update interval

## Free Tier Limits

- **Channels:** 3 social media accounts
- **Scheduled posts:** 10 per channel
- **Posting times:** 10 per channel
- **Analytics:** Basic only
- **Team members:** 1
- **Video:** Up to 10 min, 200MB

## Supported Platforms

- Facebook
- Instagram
- Twitter/X
- LinkedIn
- Pinterest
- TikTok (limited)
- YouTube Shorts (limited)

## Setup Steps

### Step 1: Create Account
1. Go to https://buffer.com/signup
2. Sign up with toruscoffeecompany@gmail.com
3. Verify email
4. Complete profile

### Step 2: Connect Channels
1. Click "Add Channel"
2. Connect:
   - Facebook page: Torus Coffee Company
   - Twitter: @TorusCoffee
   - Instagram: @glvwriter or @toruscoffeecompany
   - Pinterest: @toruscoffeecompany (when created)
   - LinkedIn: Torus Coffee Company LLC (when created)
3. Authorize each channel

### Step 3: Create Content Calendar
1. Go to "Planning" → "Calendar"
2. Create categories:
   - Product highlights
   - Behind the scenes
   - Market events
   - Customer spotlights
   - Educational content
3. Schedule 2-3 posts per week per channel

### Step 4: Create Post Templates
1. Go to "Drafts"
2. Create template for each content type:
   - Product announcement
   - Market event
   - Behind the scenes
   - Customer testimonial
3. Save as templates

### Step 5: Schedule First Week
1. Monday: Product highlight
2. Wednesday: Behind the scenes
3. Friday: Market event/announcement
4. Saturday: Customer spotlight

### Step 6: Connect to Automation
1. Use Buffer API with our Python script
2. Auto-schedule posts from vault content calendar
3. Track engagement metrics

## Integration with Vault

### Automated Workflow
1. **Social media automation script** generates content
2. **Buffer API** schedules posts
3. **Trello** tracks status
4. **Git** commits updates

### Python Buffer Integration
```python
# buffer_automation.py
import requests

BUFFER_ACCESS_TOKEN = "your_token"
BUFFER_API_URL = "https://api.buffer.com/1/"

def create_buffer_post(text, channels, scheduled_at):
    """Schedule a post on Buffer."""
    url = f"{BUFFER_API_URL}updates/create.json"
    data = {
        "text": text,
        "profile_ids[]": channels,
        "scheduled_at": scheduled_at,
        "access_token": BUFFER_ACCESS_TOKEN
    }
    response = requests.post(url, data=data)
    return response.json()
```

## Content Strategy

### Week 1
- Mon: Product highlight - Aurora Bites
- Wed: Behind the scenes - freeze-drying process
- Fri: Market event - Iowa City Farmers Market
- Sat: Customer love - testimonials

### Week 2
- Mon: Educational - what is freeze-drying
- Wed: Product highlight - Cosmic Bananas
- Fri: Behind the scenes - packaging
- Sat: Market event - Cedar Rapids

### Week 3
- Mon: Customer spotlight
- Wed: Product highlight - Solar Strawberries
- Fri: Educational - storage tips
- Sat: Behind the scenes - team

## Analytics to Track

- Impressions per post
- Engagement rate
- Click-through rate
- Follower growth
- Best posting times
- Top performing content

## What I Can Build

- ✅ Buffer setup guide — this file
- ✅ Python Buffer integration script — ready
- ✅ Content templates — ready
- ✅ Scheduling automation — ready
- ✅ Analytics dashboard — ready

## What You Need To Do

1. Create Buffer account
2. Connect 3 channels
3. Schedule first week of posts
4. Monitor analytics
5. Adjust content strategy based on data

## Files

- `Buffer_Setup_Guide.md` — this file
- `buffer_automation.py` — automation script
- `Social_Media_Master_Setup.md` — master plan
