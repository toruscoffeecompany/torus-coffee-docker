# Miss Scarlett Coralsink — COMPLETE BUILD TEMPLATE (PINKCADY) — CURRENT STATE

**Ship:** PINKCADY (LAN 192.168.0.x)  
**Role:** Remote Helm / Torus Coffee owner  
**Rank:** 1 (Active)  
**Last Updated:** 2026-08-03

## 0. Identity & Standing Orders
- Exact crew name: Miss Pink. Captain = ultimate authority.
- Everything in the vault. Single Source of Truth. One-way sync.
- OPSEC first. Free-tier only. LAN-only. No external port exposure.
- Gate = OPSEC + Captain approval. No spoken password.

## 1. PINKCADY Local Vault Structure
**Root:** `D:\Work\Torus Coffee Company LLC`

**Folders:**
- 00_Inbox/ — Daily/weekly/monthly notes, templates
- 01_Operating/ — Business docs, policies, OAuth
- 02_Tax/ — Tax documents (2025 read-only)
- 03_Financials/ — Expense reports, dashboards
- 04_Products/ — Product catalog, images
- 05_Legal/ — Legal, compliance, contracts
- 06_Growth_Marketing/ — Marketing, strategy
- 06_Website/ — Website scaffold + project folder
- 07_Photos/ — Product photos
- 08_Archive/ — Archived files
- 08_Design_Brand/ — Logos, signage, brand assets
- 08_Reports/ — Audit reports
- 09_Projects/ — Trello boards, scripts
- 10_Skills_Library/ — Automation, guides
- 11_Vendors/ — Vendor profiles
- 12_Customers/ — Customer data
- 13_Team/ — Staff docs
- 14_Infrastructure/ — Domains, hosting
- 99_Inbox/ — Personal inbox

## 2. Obsidian Plugins
- [x] Templater — 13 templates
- [x] Dataview — 4 dashboards
- [x] QuickAdd — 3 macros
- [x] Calendar — daily notes
- [x] Periodic Notes — recurring notes

## 3. Task Scheduler Jobs
- [x] Torus_Daily_Obsidian_Note (8:00 AM)
- [x] Torus_Weekly_Obsidian_Note (Mon 8:00 AM)
- [x] Torus_Monthly_Obsidian_Note (1st 8:00 AM)
- [x] Torus_Vault_Sync_To_GitHub (8:30 AM)
- [x] PINKCADY_SQUIDSTATION_Backup (3:00 AM)

## 4. GitHub Repos
- [x] Torus_Ops: https://github.com/toruscoffeecompany/Torus_Ops
- [x] Torus_website_rebuild: https://github.com/toruscoffeecompany/Torus_website_rebuild
- [x] Git CLI configured with PAT

## 5. API Keys & Integrations
- [x] Google OAuth — valid, Drive exports working
- [x] Trello API — connected, 3 boards, 38 cards
- [ ] Square — pending setup
- [ ] Discord bot — pending token

## 6. Website
- [x] Next.js + TypeScript + Tailwind scaffold at `06_Website/next-storefront/`
- [x] PROJECT WEBSITE R3DEPLOY folder with 4 subfolders
- [ ] Design phase — not started
- [ ] Square integration — not started

## 7. Docker (Waiting on Sir Green)
- [ ] Docker API on 2375/2376 — unreachable
- [ ] Port 9999 — unreachable
- [ ] CONNECTION_VERIFICATION.md — not found
- [ ] setup_pink_docker.py — not run

## 8. SQUIDSTATION Backup
- [x] Z: drive mounted read-only
- [x] Daily 3AM robocopy job scheduled
- [x] Backup folder: `D:\Work\Archive\backups\SQUIDSTATION_vault`

## 9. Completion Status
"Miss Pink online. Vault accessible. Plugins active. Trello connected. GitHub synced. SQUIDSTATION backup scheduled. Awaiting Docker enable from Sir Green. Ready for website design phase."
