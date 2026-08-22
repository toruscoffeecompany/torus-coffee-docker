# Square Payment Setup — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Ready for setup  
**Recommendation:** Start with Square (free), upgrade later when revenue justifies it

## Recommendation

**Why Square for Torus Coffee Company:**
- $0 monthly fee
- 2.6% + $0.15 per transaction
- Simple setup for markets and online
- Hardware optional (phone/tablet works)
- Payment links work without coding
- Can upgrade to Square Online for free website hosting

**Alternatives considered:**
- Stripe: developer-friendly, same pricing, more complex
- Helcim: interchange-plus, no monthly fee, less brand recognition
- PayPal: widely trusted, higher fees for small transactions

**Decision:** Start with Square free tier. Migrate later if volume justifies lower rates.

## Setup Checklist

### Phase 1: Account Setup
- [ ] Create Square Developer account at https://developer.squareup.com
- [ ] Create Square Seller account at https://squareup.com/signup
- [ ] Verify business email: toruscoffeecompany@gmail.com
- [ ] Link bank account for deposits
- [ ] Complete identity verification

### Phase 2: Payment Links (Easiest)
- [ ] Login to Square Dashboard
- [ ] Go to "Online Checkout" → "Payment Links"
- [ ] Create payment link for each product:
  - Aurora Bites — $6.99
  - Sour Aurora Bites — $6.99
  - Cosmic Bananas — $7.99
  - Apple Zephyr Chips — $6.49
  - Apple Cinnamon Comets — $7.49
  - Aurora Berryalis — $7.99
  - Star-Dusted Banana Crunch — $7.49
  - Solar Strawberries — $7.99
  - Neapolitan Orbit Cream Crunch — $8.99
  - Orbit Cream Crunch — $8.99
- [ ] Copy payment link URLs to vault

### Phase 3: Square Online (Free Website)
- [ ] Create Square Online store at https://squareup.com/online-store
- [ ] Import product list from vault
- [ ] Set shipping rates
- [ ] Connect custom domain (toruscoffeecompany.com)
- [ ] Test checkout flow

### Phase 4: In-Person Payments (Markets)
- [ ] Download Square Point of Sale app
- [ ] Use phone/tablet as card reader
- [ ] OR order Square card reader ($49)
- [ ] Test at market booth
- [ ] Print receipts

### Phase 5: API Integration (Website)
- [ ] Get Square Application ID and Access Token
- [ ] Add payment processing to Next.js website
- [ ] Test sandbox transactions
- [ ] Go live

## Costs

- **Square Account:** Free
- **Payment Links:** Free
- **Square Online:** Free
- **Card Reader:** $49 optional
- **Transaction Fees:** 2.6% + $0.15 per transaction
- **Monthly Fees:** $0

## Next Steps

1. Create Square accounts (need user approval/credentials)
2. Create payment links for all 10 products
3. Test payment flow
4. Add links to website
5. Train for market booth usage

## Files

- `Square_Developer_Setup_Guide.md` — detailed technical setup
- `Square_OAuth_Flow.md` — OAuth integration guide
- `Square_Payment_Links_Setup.md` — this file
