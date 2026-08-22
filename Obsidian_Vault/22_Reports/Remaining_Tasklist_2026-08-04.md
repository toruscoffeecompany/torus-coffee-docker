# Torus Coffee Company — Remaining Execution Tasklist

**Date:** 2026-08-04  
**Status:** Auto-prompt loop active; full-stack build in progress  
**Vault:** `D:\Work\Torus Coffee Company LLC`

## Live / Verified ✅
- Local SQLite DB: `10_Skills_Library/05_Operations/data/torus_local.db`
- Website product sync: `06_Website/next-storefront/data/products.ts`
- Website build: `06_Website/next-storefront` exports 27/27 static pages
- Watcher: running (`proc_15f557d8a298`), scanning `PINKCADY_INBOX`
- Auto-prompt generators: both producing outbound messages this session
- Git sync: pushed to `Torus_Ops` (`e29834d`)

## Immediate Next Steps
1. Fix `06_Website/Website` case collision / consolidate duplicate build
2. Decide canonical website path: `06_Website/Website` vs `06_Website/next-storefront`
3. Deploy `next-storefront` to free hosting
4. Wire Discord webhook + Gmail app password + backup path
5. Decide Supabase vs static phase
6. Complete Zapier/Buffer/HubSpot live wiring
7. Create Task Scheduler jobs (requires admin)
8. End-to-end verification of live alerts
