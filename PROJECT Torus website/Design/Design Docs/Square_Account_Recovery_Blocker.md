# Square Account Recovery Blocker

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** BLOCKED — awaiting identity verification  
**Priority:** P2

## Issue

Square requires identity verification via Veriff to recover/access account. This blocks both Square Developer and Square Seller account setup.

## What Square Requires

### Step 1: Photo Identification
- Physical government-issued photo ID required (copies won't work)
- Valid documents:
  - ID Card
  - Passport
  - Residence Permit
  - Driver's License

### Step 2: Biometric Verification
- Take a selfie using phone or webcam
- Take photos of front and back of document
- Face must be well lit
- Consent to ID scan and biometric data processing by Veriff
- Veriff retains biometric data for maximum 120 days

## Impact

- **Square Developer Account:** Cannot create without verification
- **Square Seller Account:** Cannot create without verification
- **Payment Links:** Blocked until account created
- **Square Point of Sale:** Blocked until account created
- **Website Payment Integration:** Blocked until account created

## Alternatives While Blocked

1. **PayPal** — no identity verification for basic account
2. **Stripe** — similar verification requirements
3. **Cash/QR payments** — manual market booth option
4. **Square competitor** — Helcim, no monthly fee, but still requires verification

## Next Steps

1. Obtain physical government-issued ID
2. Complete Veriff verification when ready
3. Re-run Square setup guide after verification
4. Test payment links in sandbox mode

## Reference

- Square Setup Guide: `06_Website/Design/Design Docs/Square_Payment_Links_Setup.md`
- Square Developer Setup: `06_Website/Design/Design Docs/Square_Developer_Setup_Guide.md`
- Square OAuth Flow: `06_Website/Design/Design Docs/Square_OAuth_Flow.md`
