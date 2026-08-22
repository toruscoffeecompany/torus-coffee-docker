# Google Analytics Setup — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Guide ready — implement after website deployment

## Overview

Google Analytics 4 (GA4) is free and provides:
- Website traffic monitoring
- User behavior tracking
- Conversion goals
- Ecommerce tracking
- Marketing attribution

## Setup Steps

### 1. Create GA4 Property
1. Go to https://analytics.google.com
2. Click "Start measuring"
3. Account name: Torus Coffee Company
4. Property name: Torus Coffee Company Website
5. Reporting time zone: (GMT-06:00) Central Time
6. Currency: USD
7. Click "Next"

### 2. Business Information
- Industry category: Shopping / Retail
- Business size: Small (1-10 employees)
- Objectives: Generate leads, Drive online sales
- Click "Create"

### 3. Get Measurement ID
- After creation, go to Admin → Data Streams
- Click "Web" platform
- Enter URL: toruscoffeecompany.com
- Stream name: Website
- Click "Create stream"
- Copy **Measurement ID** (format: G-XXXXXXXXXX)

### 4. Add to Website
1. Open `06_Website/next-storefront/app/layout.tsx`
2. Add GA4 script in `<head>`:

```tsx
<script
  async
  src={`https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX`}
/>
<script
  dangerouslySetInnerHTML={{
    __html: `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    `,
  }}
/>
```

### 5. Configure Goals
- **Page views** — track all page views
- **Product views** — track product page visits
- **Add to cart** — track cart actions
- **Checkout** — track purchase flow
- **Purchase** — track completed orders

### 6. Enhanced Ecommerce
- Enable in GA4 settings
- Track product impressions
- Track product clicks
- Track add to cart
- Track checkout steps
- Track purchases

### 7. Link to Google Services
- Link Google Search Console
- Link Google Ads (if used)
- Link Google Business Profile

## Free Tier Limits

- **Events:** 500+ per day free
- **Custom dimensions:** 50 free
- **Custom metrics:** 50 free
- **Data retention:** 14 months free
- **BigQuery export:** Free

## Next Steps

1. Create GA4 property after website deployment
2. Add measurement ID to website
3. Configure goals
4. Test tracking in real-time
5. Create dashboards in GA4

## Files

- `Google_Analytics_Setup_Guide.md` — this file
- `Google_Workspace_Access.md` — existing Google setup
