# Torus Coffee Company — Sir Green Support Tasklist
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** In Progress
**Waiting On:** Sir Green for `MISS_PINK_*` file locations + Wazuh installer run

## Source of Truth
- Local Obsidian vault: `D:/Work/Torus Coffee Company LLC`
- Trello: 382 cards across Torus_Ops / Business_Docs / Website_Rebuild
- Git: `main` branch at `33efcf4`
- Comms: local outbox canonical; shared bus at `02_Business_Operations/Communications/Outbox/SHARED_COMMS_BUS.json`

## Sir Green Requested Items

### 1. Monitor and Archive Processed Auto-Prompt Messages
- [x] Watcher processes running and processing inboxes
- [x] Replies writing to local outbox
- [x] Shared comms bus updated
- [x] Z: archive failures tolerated
- [ ] Deduplicate old auto-prompt replies in outbox
- [ ] Archive processed auto-prompt messages to local archive

### 2. Human Action: Run Wazuh Windows Installer on SQUIDSTATION
- [x] Wazuh manager endpoint not yet available
- [x] Documented in `08_Reports/Gordon_Docker_Verification_Status_2026-08-04.md`
- [ ] Sir Green to run Wazuh Windows installer on SQUIDSTATION
- [ ] Verify Wazuh agent enrollment
- [ ] Test alert flow from Wazuh → Grafana

### 3. Once Wazuh Is Live: Integrate Alerts into Grafana
- [ ] Create Grafana dashboard for Wazuh alerts
- [ ] Configure Wazuh → Grafana data source
- [ ] Add Torus Coffee alert rules
- [ ] Test alert routing: Critical → email, Warning → Obsidian, Info → log

### 4. Keep Sir Green Automations Healthy; Avoid Overlapping Miss Pink's Active Cosmos Lanes
- [x] Confirmed Pink lanes: local vault, shared comms, Pink scripts/state
- [x] Not touching `09_Cosmos_Library`, `VOID Pirate Trading Co`, Squidstation vault paths
- [x] Using `.file_lock_registry.json` to avoid concurrent edits
- [x] Watcher avoids archiving Green inbox messages
- [ ] Confirm Sir Green is not editing Pink's active Cosmos lanes
- [ ] Monitor file mutations and resolve if detected

## Pink-Safe Work While Sir Green Works

### A) Monitor and Clean Up Auto-Prompt Messages
- [ ] Deduplicate outbox auto-cycle replies
- [ ] Archive processed messages to local archive
- [ ] Verify no file mutations from watcher

### B) Advance Website_Rebuild
- [ ] Add legal pages with real content
- [ ] Add about page with brand story
- [ ] Add products page with live SKU data

### C) Advance Business_Docs
- [ ] Create Supplier Agreement Template
- [ ] Draft vendor applications — Iowa City + Cedar Rapids
- [ ] Write SOP — Espresso Pull Procedure

### D) Financials
- [ ] Update `Revenue_Stream_Plan.md` from live Trello cards

### E) Verification
- [ ] Verify Docker connectivity to SQUIDSTATION
- [ ] Verify inquiry endpoint end-to-end
- [ ] Verify backup script + integrity
- [ ] Verify local ops monitor health checks
- [ ] Verify git status clean

## Blockers
- `MISS_PINK_PROMPT.md`, `MISS_PINK_STATUS.md`, `MISS_PINK_REPLY.md` locations unknown
- Wazuh Windows installer requires human action on SQUIDSTATION
- Grafana integration blocked until Wazuh is live

## Notes
- Sir Green's latest message: `20260804T144500Z_sirgreen_cosmos_ooda_001.msg.md`
- No new Sir Green messages since then
- Auto-prompt loops running
- Git: `33efcf4` pushed
