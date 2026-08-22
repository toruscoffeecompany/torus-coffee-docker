# Full Scope Automation Build Plan — Torus Coffee Company

## Current State Summary

### What We Have ✅
- **Vault:** 4,200+ files, 19 folders, fully organized
- **Automation:** 18 Task Scheduler jobs, all passing
- **Integrations:** Buffer, Zapier, HubSpot, Trello connected
- **Test Suite:** 10/10 PASS
- **Website:** 10 pages scaffolded, contact form backend built
- **Order Management:** Built and tested
- **Inventory Sync:** Built and tested
- **Alert Router:** Critical/Warning/Info/Debug routing active
- **GitHub:** Torus_Ops repo synced, clean commits
- **Legal:** Privacy, Terms, Accessibility drafted

### What’s Missing ❌
- **Payment processor** — Square blocked, no active payment links
- **Contact form backend** — API route built, needs Formspree/Zapier endpoint
- **Product photos** — 14 placeholders, Sir Azure blocked
- **Legal review** — drafted, not signed off
- **Sir Azure** — admin lock on STEALTHATTACK
- **Discord bots** — designs ready, no apps created
- **Bank integration** — US Bank statements only, no API

---

## Free-Tier Budget Analysis

### Revenue Streams (from Revenue_Stream_Plan.md)
1. Flea Markets & Pop-Ups — $500–$800/event
2. Wholesale Accounts — $500–$2,000/month
3. Website Orders — $300–$1,500/month
4. Amazon FBA/FBM — $200–$1,000/month
5. YouTube Ad Revenue — $50–$500/month
6. Sponsorships & Brand Deals — $100–$1,000/month
7. Subscription / Club — $300–$1,000/month
8. Local Delivery — $100–$300/month

**Total potential:** $2,050–$7,100/month at full maturity

### Free Tools We Can Use Today

| Tool | Cost | Purpose |
|------|------|---------|
| Square Payment Links | Free + 2.9%/txn | Website checkout |
| Formspree | Free (50/mo) | Contact form |
| Zapier | Free (100 tasks/mo) | Webhook automation |
| HubSpot CRM | Free (1,000 contacts) | Customer tracking |
| Buffer | Free (3 channels) | Social media |
| Trello | Free (10 boards) | Project management |
| Netlify | Free (100GB/mo) | Website hosting |
| Google Workspace | Free (personal) | Email, Drive |
| Wave Accounting | Free | Bookkeeping, invoicing |
| Canva Free | Free | Social media graphics |
| GIMP | Free | Photo editing (Sir Azure alternative) |
| Inkscape | Free | Vector graphics |
| DaVinci Resolve | Free | Video editing |

**Total monthly cost: $0** (plus transaction fees only when revenue occurs)

---

## Prioritized Build Plan

### Phase 1: Launch Blockers (This Week)
**Goal:** Accept first order

1. **Set up Square Payment Links** (30 min)
   - Create Square account or verify existing
   - Link US Bank account
   - Create 10 product links
   - Add to website

2. **Set up Formspree** (15 min)
   - Sign up, create form
   - Add endpoint to `.env`
   - Test contact form

3. **Finalize legal pages** (1 hour)
   - Review Privacy Policy, Terms, Accessibility
   - Your sign-off required
   - Publish to website

4. **Finalize product data** (30 min)
   - Confirm 10 SKU names, descriptions, prices
   - Update `04_Products/Product_List_and_Prices_Master_2026.csv`
   - Update website product data

### Phase 2: Automation (Next Week)
**Goal:** Every order auto-tracks itself

1. **Zapier Zap: Order → Gmail → Trello** (1 hour)
   - Trigger: Square payment webhook
   - Action 1: Send Gmail notification
   - Action 2: Create Trello card
   - Action 3: Send Discord notification

2. **Order Manager Integration** (2 hours)
   - Wire order_manager.py to Gmail API
   - Auto-create Trello cards from order emails
   - Update inventory automatically

3. **Inventory → Website Sync** (1 hour)
   - inventory_sync.py already built
   - Wire to website build process
   - Hide out-of-stock products

4. **Social Media Automation** (1 hour)
   - Buffer API connected, create content queue
   - Schedule weekly posts
   - Track engagement in Trello

### Phase 3: Growth (Week 3-4)
**Goal:** Scale without manual work

1. **HubSpot CRM Setup** (2 hours)
   - Import contacts from Gmail
   - Set up deal stages
   - Create email sequences

2. **Customer Loyalty System** (3 hours)
   - Points tracking in HubSpot
   - Referral code system
   - Email list building

3. **Blog/Content Section** (4 hours)
   - Add blog to website
   - Connect Substack
   - YouTube embeds

4. **Amazon GTIN Exemption** (2 hours)
   - Already documented
   - Apply for exemption
   - List first products

### Phase 4: Advanced (Month 2+)
**Goal:** Full crew automation

1. **Sir Azure unblock** (needs Captain/Sir Green)
   - Fix admin lock on STEALTHATTACK
   - Install ComfyUI + SDXL
   - Create Discord bot
   - Generate product photos

2. **Discord bots** (needs Captain)
   - Create Discord server
   - Create 5 bot applications
   - Test all bots
   - Activate relay queue

3. **Local Network Dashboard** (needs Sir Green)
   - Deploy dashboard_server.py on SQUIDSTATION
   - Connect PINKCADY stats
   - Test defense/monitoring tools

4. **Bank Integration** (low priority)
   - Manual CSV export from US Bank
   - Import to Wave Accounting
   - Reconcile monthly
   - Full API integration: not free, requires US Bank developer account

---

## What We Can Build RIGHT NOW (No Blockers)

### Today
1. **Square Payment Links** — create account, link US Bank, generate links
2. **Formspree Contact Form** — sign up, add endpoint, test
3. **Legal Page Review** — review drafted docs, sign off
4. **Product Data Finalization** — confirm 10 SKUs, update CSV

### This Week
5. **Zapier Order Automation** — build Zap: Square → Gmail → Trello
6. **Inventory Sync** — test inventory_sync.py with real data
7. **Social Media Calendar** — schedule first month of posts
8. **Test Suite Expansion** — add payment and contact form tests

### Next Week
9. **HubSpot CRM** — import contacts, set up deals
10. **Customer Email Sequences** — welcome, abandoned cart, re-engagement
11. **Blog Section** — add to website, write first 3 posts
12. **Amazon GTIN Exemption** — apply, list products

---

## Free-Tier Limits to Watch

| Tool | Free Limit | When It Hits |
|------|-----------|--------------|
| Formspree | 50 submissions/mo | ~50 customer inquiries |
| Zapier | 100 tasks/mo | ~100 webhook calls |
| HubSpot | 1,000 contacts | ~1,000 customers |
| Buffer | 3 social channels | Already at limit |
| Netlify | 100GB bandwidth/mo | ~10,000 page views |
| Trello | 10 boards | Already at 3 boards |
| Square | No monthly fee | Unlimited transactions |

**Upgrade triggers:** When Formspree/Zapier limits hit, move to paid tiers ($9–$20/mo each)

---

## Immediate Next Steps (Your Action Required)

1. **Square account** — create or verify existing, link US Bank
2. **Formspree account** — create, get endpoint URL
3. **Legal review** — read Privacy Policy, Terms, Accessibility
4. **Product pricing** — confirm 10 SKU prices
5. **Sir Azure** — work with Sir Green to fix admin lock

**My next action:** Build Zapier Zap for order automation and create Square payment link placeholders in website.

Which do you want me to tackle first?
- **A)** Square payment links + website integration
- **B)** Formspree contact form + Zapier automation
- **C)** Legal page review + finalization
- **D)** All of the above in parallel
