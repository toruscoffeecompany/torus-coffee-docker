# Torus Coffee Company — Product Review System Design
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** Draft

## Goal
Enable product reviews with moderation until higher-volume tools are justified.

## Review Schema
- `review_id`: integer PK
- `product_sku`: text FK to products
- `customer_name`: text
- `rating`: integer 1-5
- `body`: text
- `status`: enum: `pending`, `approved`, `rejected`
- `created_at`: ISO timestamp

## Moderation
- Admin can approve/reject reviews
- Public site shows only approved reviews
- Admin API required for moderation actions

## Frontend
- Product page review form
- Approved reviews list with rating summary
- No login required for submission

## Free-Tier Hosting
- Reviews stored in SQLite
- Moderation via local admin UI only

---

# Torus Coffee Company — Referral/Affiliate Tracking Design
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** Draft

## Goal
Track referrals and affiliates with simple code-based attribution.

## Referral Schema
- `referral_code`: text unique
- `source`: enum: `customer`, `partner`, `social`
- `uses`: integer default 0
- `reward_type`: enum: `percent`, `fixed`
- `reward_value`: numeric
- `created_at`: ISO timestamp

## Affiliate Schema
- `affiliate_id`: integer PK
- `name`: text
- `email`: text
- `code`: text unique
- `rate_percent`: numeric
- `total_referrals`: integer
- `total_payouts`: numeric
- `created_at`: ISO timestamp

## Attribution
- Capture `?ref=CODE` on site
- Write referral event on inquiry/order creation
- Admin dashboard shows usage counts

## Admin Tools
- Create/manage referral codes
- Create/manage affiliates
- View referral attribution logs

## Payout Policy
- Manual payout until revenue threshold met
- Export CSV for accounting

## Free-Tier Constraints
- No paid affiliate network until revenue
- Local admin UI only
