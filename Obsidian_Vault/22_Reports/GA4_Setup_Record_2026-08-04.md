# Google Analytics (GA4) — Setup Record

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Status:** Code scaffolded, measurement ID pending  

## Current State
- GA4 script scaffold added to `06_Website/next-storefront/app/layout.tsx`.
- Measurement ID placeholder is `GA_MEASUREMENT_ID`.
- No third-party analytics enabled by default until final review.

## Action Required
1. Create GA4 property for `toruscoffeecompany.com`.
2. Replace `GA_MEASUREMENT_ID` with the real Measurement ID.
3. Verify data stream is collecting page views.

## Launch Readiness
- Deployment target: Vercel or equivalent static host.
- Free-tier compliant: GA4 free tier is sufficient.
- Post-launch verification: real-time report + 24-hour data check.

## Notes
- Do not enable advertising features until privacy policy review is complete.
- Keep tracking minimal: page views only until revenue justifies deeper event instrumentation.
