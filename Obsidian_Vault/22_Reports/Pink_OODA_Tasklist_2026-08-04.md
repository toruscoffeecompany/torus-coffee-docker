# Torus Coffee Company — Pink OODA Loop Tasklist
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** In Progress
**Waiting On:** Sir Green coordination confirmation

## OODA Cycle: Post-SirGreen-Wait Work

### A) Contact/Wholesale Inquiry Flow — End-to-End Verification
- [ ] Verify contact form page exists at `/contact`
- [ ] Verify wholesale page exists at `/wholesale`
- [ ] Test `POST /api/inquiries` endpoint
- [ ] Verify inquiry saved to SQLite
- [ ] Verify CORS/proxy path from Next.js to FastAPI
- [ ] Verify error handling for invalid payloads
- [ ] Verify success response format

### B) Automated Backup Script
- [ ] Design backup targets: vault docs + SQLite DB + GitHub mirror
- [ ] Create `scripts/automated_backup.py`
- [ ] Backup vault docs to `D:/backups` or `Z:/backups`
- [ ] Backup SQLite DB `torus_local.db`
- [ ] Create GitHub mirror push fallback
- [ ] Add logging to `logs/backup_report.json`
- [ ] Verify backup integrity
- [ ] Add to Task Scheduler

### C) Inventory Admin Dashboard — Schema/Design Doc
- [ ] Create `09_Projects/Inventory_Admin_Dashboard_Design.md`
- [ ] Define SKU schema extensions
- [ ] Define low-stock threshold rules
- [ ] Define admin API endpoints
- [ ] Define frontend components
- [ ] Define access control

### D) Customer/Order Systems — Schema/Design Doc
- [ ] Create `09_Projects/Customer_Order_System_Design.md`
- [ ] Define customer schema
- [ ] Define order schema
- [ ] Define order states/transitions
- [ ] Define admin tools
- [ ] Define integration with contact inquiries

### E) SEO/Social Auto-Posting — Design Doc
- [ ] Create `09_Projects/SEO_Social_AutoPosting_Design.md`
- [ ] Define free-tier toolchain
- [ ] Define content calendar schema
- [ ] Define post templates
- [ ] Define platform routing rules
- [ ] Define approval workflow

### F) Product Review + Referral Tracking — Design Docs
- [ ] Create `09_Projects/Product_Review_System_Design.md`
- [ ] Define review schema/moderation
- [ ] Create `09_Projects/Referral_Affiliate_Tracking_Design.md`
- [ ] Define referral codes/rewards
- [ ] Define affiliate schema

## Coordination Notes
- **Pink-only lanes:** local vault, shared inbox/outbox, `10_Skills_Library/05_Operations/`
- **Do not touch:** `Miss_Pink_Bridge`, `09_Cosmos_Library`, `VOID Pirate Trading Co`, Squidstation vault paths
- **Lock registry:** `.file_lock_registry.json` active
- **Comms:** local outbox is canonical; Z: inbox readable but may not be writable

## Verification Checklist
- [ ] All scripts run without errors
- [ ] All docs committed to Git
- [ ] Trello status comments updated
- [ ] Sir Green notified of boundaries and progress
- [ ] No overlap with Sir Green's assigned paths
