# AUTOMATION DEEP DIVE — MISS PINK / TORUS COFFEE / VOID PIRATE
**Date:** 2026-08-06  
**Status:** Gap analysis and implementation plan

---

## EXECUTIVE SUMMARY
We have strong foundations: inbox → Trello/GitHub → classification → indexing → weekly scheduler.  
What’s missing is the full content production pipeline, multi-company crew scheduling, and Obsidian-vault-driven automation.

---

## WHAT WE HAVE AUTOMATED
- ✅ Inbox ingestion from Z:\ drives → Trello cards + GitHub issues
- ✅ Priority classification with skewed taxonomy (P0 → P6, Future Ideas)
- ✅ Top 10 enforcement (exactly 10 cards)
- ✅ Due dates, follow-ups, checklists, member assignment
- ✅ Weekly scheduler with day assignments
- ✅ Calendar sync scaffold
- ✅ End-to-end test alert created in Trello/GitHub
- ✅ GitHub label pagination fixed, labels synced
- ✅ VOID Pirate issue tracker scaffold
- ✅ Social media config and basic template generator

---

## WHAT’S NOT AUTOMATED — GAPS

### 1. OBSIDIAN → TRELLO/GITHUB SYNC
- **Current:** Vault is read-only source of truth, but changes don’t create cards/issues
- **Needed:** Watchers on:
  - `00_Inbox/01_Daily/*.md` → auto-create P0/P1 ops alerts
  - `06_Growth_Marketing/Social_Content_Queue_*.md` → create scheduled content cards
  - `06_Growth_Marketing/YouTube_Content_Plan.md` → create video production cards
  - `10_Skills_Library/05_Operations/CONTINUOUS_TASKLIST.md` → auto-update status

### 2. CONTENT PRODUCTION PIPELINE
- **Substack:** No automation for post creation, scheduling, or publishing
- **X/Twitter:** No actual posting automation, only templates
- **AI Images:** No integration with image generation tools
- **AI Videos:** No integration with video generation tools
- **YouTube:** Plan exists but no production/upload automation

### 3. MULTI-COMPANY SCHEDULING
- **Current:** Separate queues for Torus Coffee, Sir Green, Sir Azure
- **Needed:** Unified weekly calendar that respects:
  - Miss Pink’s limited hours
  - Sir Green’s Docker/infrastructure work
  - Sir Azure’s security/AI pipeline work
  - VOID Pirate Trading Co schedule

### 4. CREW HOUR ALLOCATION
- **Constraint:** One human captain, limited weekly hours
- **Needed:** Capacity-aware scheduling:
  - P0/P1: Captain + Sir Green/Sir Azure as needed
  - P2: Captain primary, crew support
  - P3+: Batch/delegate where possible
  - Max 40 hrs/week for Miss Pink

### 5. CRITICAL ALERT ROUTING
- **Current:** Alerts go to inbox → Trello/GitHub
- **Needed:** Smart routing:
  - Dashboard 502 → Sir Green
  - Low stock → Miss Pink
  - Security issue → Sir Azure
  - Revenue opportunity → Top 10

---

## PROPOSED AUTOMATION ARCHITECTURE

```
┌─────────────────────────────────────────┐
│         OBSIDIAN VAULT                  │
│  (Source of Truth)                      │
└──────────────┬──────────────────────────┘
               │ file watchers
               ▼
┌─────────────────────────────────────────┐
│      OBSIDIAN WATCHER DAEMON            │
│  - Detects new/modified files           │
│  - Classifies by path/type              │
│  - Creates Trello cards/GitHub issues   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      TRELLO FINAL AUTOMATION            │
│  - Classify → P0/P1/P2/P3/P4/P5/P6    │
│  - Label, move, index                   │
│  - Due dates, follow-ups, checklists    │
│  - Enforce Top 10 limit                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      WEEKLY SCHEDULER                   │
│  - Capacity-aware day assignments       │
│  - Crew-specific schedules              │
│  - Google Calendar sync                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      CONTENT PIPELINE                   │
│  - Substack post generator              │
│  - X/Twitter poster                      │
│  - AI image generator                    │
│  - AI video generator                    │
│  - YouTube upload automation             │
└─────────────────────────────────────────┘
```

---

## CREW SCHEDULE PROPOSAL

### MISS PINK — 40 hrs/week
- **Mon-Wed-Fri:** Content production (Substack, X, AI assets)
- **Tue-Thu:** Operations (Torus Coffee orders, inventory, market prep)
- **Sat:** Market day / customer engagement
- **Sun:** Planning, review, OODA

### SIR GREEN — 40 hrs/week
- **Mon-Wed-Fri:** Infrastructure (Docker, dashboard, APIs, fleet)
- **Tue-Thu:** Code review, security patches, monitoring
- **Sat:** Deployment windows, maintenance
- **Sun:** On-call only

### SIR AZURE — 10 hrs/week (limited)
- **Mon-Wed:** Security tools, AI pipeline, monitoring
- **Fri:** Reporting, documentation
- **Rest:** Async/batched work

### VOID PIRATE TRADING CO
- **Async:** GitHub issues → Trello cards in VOID Ops
- **Weekly sync:** Friday 2pm with Sir Green
- **Batched:** All non-critical work queued for weekly review

---

## IMMEDIATE NEXT STEPS

1. **Create Trello cards/GitHub issues** for all gaps above
2. **Build Obsidian watcher daemon** (`obsidian_watcher.py`)
3. **Build content pipeline** (`content_pipeline.py`)
4. **Build crew scheduler** (`crew_scheduler.py`)
5. **Wire Google Calendar sync** end-to-end
6. **Test end-to-end** with sample alerts/content
7. **Send crew instructions** for future workflows

---

*Plan created: 2026-08-06*  
*Owner: Miss Pink / Hermes Agent*
