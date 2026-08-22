# Payment Processor Decision — Torus Coffee Company

**Date:** 2026-08-08  
**Owner:** Miss Pink  
**Status:** CHOSEN — Square Payment Links (free tier)  
**Rule:** Free tier only until first revenue stream proves. No paid upgrades without approval.

---

## Decision Matrix

| Provider | Online Fee | Monthly Fee | API | Best For | Verdict |
|---|---|---|---|---|---|
| **Square** | 2.9% + 30¢ | **$0** | ✅ Payment Links API + Checkout API | In-person + online, free start | **✅ PRIMARY CHOICE** |
| PayPal | 2.99% + 49¢ | $0 | ✅ PayPal Checkout API | Familiar to consumers | ✅ BACKUP |
| Stripe | 2.9% + 30¢ | $0 | ✅ Checkout Sessions API | Developer-first | ✅ BACKUP (API only) |
| Shopify | 2.9% + 30¢ | $0–$29 | ✅ Shopify Payments | Full ecommerce platform | ❌ Too heavy for MVP |

## Rationale

1. **No monthly fee** — Square is $0/mo. Square Payment Links work immediately with a free Square account.
2. **Already referenced** — `Revenue_Stream_Plan.md` and `00_Vault_Home.md` both name Square as the payment processor.
3. **Simple integration** — Square Payment Links are static URLs per product. No server-side checkout needed for MVP.
4. **In-person option** — Same Square account works for farmers market card readers.
5. **Free to start** — No subscription, no setup fee, no hidden costs.

## Implementation Plan

### Phase 1: Static Payment Links (MVP — ready now)
- Use Square Payment Links dashboard to create one link per product SKU.
- Store links in `inventory_master.json` under each product's `squarePaymentLink` field.
- Update `06_Website/next-storefront/data/products.ts` with the links.
- Product detail pages already have the "Buy now" button logic (`product.squarePaymentLink`).

### Phase 2: Checkout API (post-launch)
- Build `app/api/checkout/route.ts` using Square Checkout API for full cart support.
- Add cart page + order tracking.
- Sync completed orders to `04_Products/orders.json`.

## Status

- [x] Research complete (Square, PayPal, Stripe evaluated)
- [x] Decision: Square Payment Links (primary), PayPal (backup)
- [x] Payment links will be created for all visible products in `inventory_master.json`
- [x] Website product data will be updated with links
- [ ] Square Payment Links created in Square Dashboard (requires Square account login)

## Evidence
- Vault: `03_Financials/Revenue_Stream_Plan.md` (already names Square + PayPal)
- Vault: `00_Vault_Home.md` (verified integrations: Square)
- Web: Square Payment Links page — no monthly fee, 2.9% + 30¢ per transaction
- Web: Shopify comparison — Square Free plan $0/mo vs Shopify $29+/mo

## Next Action
Wire Square payment links into the website's static product data. When Square account is available, create links per product SKU via Square Dashboard or Checkout API.
