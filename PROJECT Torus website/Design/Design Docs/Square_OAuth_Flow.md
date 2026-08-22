# Square OAuth Flow — Free Tier Integration

**Status:** Not yet implemented  
**Date:** 2026-08-03  
**Free Tier:** Yes — Square OAuth is free

## Overview
Use Square OAuth to connect your website to Square payments. This allows customers to checkout directly on your site using Square's payment processing.

## Prerequisites
- Square Developer account (free)
- Square Sandbox account (free testing)
- Website hosted publicly (or localhost for testing)

## Step 1: Create Square Application

1. Go to https://developer.squareup.com/apps
2. Sign in with your Square account
3. Click "New Application"
4. Name: "Torus Coffee Website"
5. Select "Online Store" as application type

## Step 2: Get Credentials

From your Square Application dashboard, copy:
- **Application ID** (public)
- **Application Secret** (private)
- **Sandbox Access Token** (for testing)
- **Production Access Token** (for live)

## Step 3: Configure OAuth Settings

In Square Developer Dashboard:
1. Go to your application → OAuth settings
2. Add Redirect URL: `https://toruscoffeecompany.com/square/callback`
3. Add Redirect URL (local): `http://localhost:3000/square/callback`
4. Select permissions:
   - `PAYMENTS_READ`
   - `PAYMENTS_WRITE`
   - `ORDERS_READ`
   - `ORDERS_WRITE`
   - `INVENTORY_READ`
   - `INVENTORY_WRITE`
   - `CUSTOMERS_READ`
   - `CUSTOMERS_WRITE`

## Step 4: OAuth Flow Implementation

### Authorization URL
```
https://connect.squareup.com/oauth2/authorize?
  client_id=YOUR_APPLICATION_ID&
  redirect_uri=https://toruscoffeecompany.com/square/callback&
  scope=PAYMENTS_READ+PAYMENTS_WRITE+ORDERS_READ+INVENTORY_READ&
  state=random_state_string
```

### Token Exchange
After user authorizes, Square redirects to:
```
https://toruscoffeecompany.com/square/callback?code=AUTH_CODE&state=random_state_string
```

Exchange code for token:
```
POST https://connect.squareup.com/oauth2/token
Content-Type: application/json

{
  "client_id": "YOUR_APPLICATION_ID",
  "client_secret": "YOUR_APPLICATION_SECRET",
  "code": "AUTH_CODE",
  "grant_type": "authorization_code"
}
```

### Refresh Token
```
POST https://connect.squareup.com/oauth2/token
Content-Type: application/json

{
  "client_id": "YOUR_APPLICATION_ID",
  "client_secret": "YOUR_APPLICATION_SECRET",
  "refresh_token": "REFRESH_TOKEN",
  "grant_type": "refresh_token"
}
```

## Step 5: Environment Variables

Add to `.env`:
```
SQUARE_APPLICATION_ID=your_app_id
SQUARE_APPLICATION_SECRET=your_app_secret
SQUARE_SANDBOX_TOKEN=your_sandbox_token
SQUARE_PRODUCTION_TOKEN=your_production_token
SQUARE_ENVIRONMENT=sandbox  # or production
```

## Step 6: Test in Sandbox

1. Use Sandbox credentials
2. Create test payment
3. Verify webhook receives event
4. Check inventory updates

## Step 7: Go Live

1. Switch to Production credentials
2. Update environment variables
3. Test real payment with small amount
4. Monitor webhooks

## Free Tier Limits
- No monthly fees
- 2.9% + 10¢ per transaction
- Free hosted checkout page
- Free inventory tracking
- No API call limits for small businesses

## Security
- Never commit credentials to git
- Use environment variables only
- Rotate tokens quarterly
- Use HTTPS in production

## Next Steps
1. [ ] Create Square Developer account
2. [ ] Create application
3. [ ] Get credentials
4. [ ] Implement OAuth flow
5. [ ] Test in Sandbox
6. [ ] Deploy to production

## Related
- `06_Website/Design/Design Docs/Square_Developer_Setup_Guide.md`
- `06_Website/next-storefront/.env.example`

---
*OAuth flow doc created: 2026-08-03*
*Owner: Miss Pink — Torus Coffee Company LLC*
