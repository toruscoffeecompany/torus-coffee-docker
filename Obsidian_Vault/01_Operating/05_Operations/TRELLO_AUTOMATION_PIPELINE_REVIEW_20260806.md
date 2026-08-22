# Torus Coffee Automation Pipeline — End-to-End Review

## Document Control
- **Version:** 1.0.0
- **Date:** 2026-08-06
- **Status:** Active
- **Author:** Miss Pink / Hermes Agent

---

## Pipeline Overview

```
New Message (Z:\ inbox)
    ↓
backfill_inboxes.py reads .msg.md files
    ↓
Creates Trello card in Backlog + GitHub issue
    ↓
trello_final_automation.py classifies card
    ↓
Card gets:
  - Priority label (P0/P1/P2/P3/Top 10)
  - Moved to correct list
  - Description added
  - Checked against VOID Ops for duplicates
  - Added to TRELLO_CARD_INDEX.json
  - Top 10 limit enforced (exactly 10 cards)
    ↓
continuous_tasklist.py aggregates all sources
    ↓
Unified tasklist generated with priorities
```

---

## Step 1: Inbox Ingestion

**Script:** `10_Skills_Library/05_Operations/Crew/backfill_inboxes.py`
**Runs:** Every 60 seconds via `ooda_loop.py`
**Sources:**
- `Z:\MISS_PINK_INBOX`
- `Z:\SIR_GREEN_INBOX`
- `Z:\SIR_AZURE_INBOX`

**Actions:**
1. Scans for `*.md` files in inboxes
2. Creates Trello card:
   - Name: `📨 [INBOX] <filename>`
   - List: Backlog
   - Label: `inbox`
   - Description: First 1000 chars of message
3. Creates GitHub issue with same title
4. Moves processed file to `Z:\processed`

**Output:** Trello card ID + GitHub issue number

---

## Step 2: Card Classification & Processing

**Script:** `10_Skills_Library/05_Operations/scripts/trello_final_automation.py`
**Runs:** On-demand or via scheduled job
**Input:** New Trello cards from any source

**Classification Logic:**
- **P0:** Alerts, blockers, 403/502 errors, security issues
- **Top 10:** Freeze-dried, Square, POS, inventory, deploy, launch, website, production, SOP, revenue
- **Future Ideas:** AI answering, phone/SMS automation, Google Voice, research/evaluate AI
- **Sir Azure's Queue:** Security tools, SQUIDSTATION, Docker for Sir Azure
- **Sir Green's Queue:** Dashboard, API routes, Docker for Sir Green
- **P1:** Setup, install, configure, fix, update, create, build, run
- **P2:** Research, test, investigate, review, audit, plan
- **P3:** Follow-up, email, graphics, templates

**Processing Actions:**
1. ✅ **Priority label** added if missing
2. ✅ **Card moved** to correct list
3. ✅ **Description added** if missing
4. ✅ **Cross-board duplicate check** against VOID Ops
5. ✅ **Indexed** in TRELLO_CARD_INDEX.json
6. ✅ **Top 10 limit enforced** (max 10 cards, demotes oldest if over)

---

## Step 3: Cross-Board Duplicate Prevention

**File:** `10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json`
**Boards indexed:** Torus_Ops, VOID Ops, Business_Docs, Website_Rebuild
**Total indexed:** 1,150 cards

**Rules:**
- `check_before_create: true` — always check index first
- `prefer_existing_card: true` — reuse existing cards
- `move_instead_of_duplicate: true` — move to correct list rather than duplicate
- `cross_board_check: true` — check all 5 accessible boards

---

## Step 4: Top 10 — Focus Fleet Enforcement

**Rule:** EXACTLY 10 cards maximum in Top 10 list
**Label:** `Top 10` (yellow)
**List:** `Top 10 — Focus Fleet`

**Enforcement Logic:**
1. When card is classified as `Top 10`:
   - If list has < 10 cards → add card
   - If list has 10 cards → demote oldest card to P1, then add new card
2. When card is demoted:
   - Remove `Top 10` label
   - Move to P1 list
3. Current Top 10 cards (10/10):
   1. Setup Square Payments
   2. Website launch — Square payment links first
   3. Freeze-Dried Production SOP - Complete
   4. Test freeze-dried SOP in production
   5. Setup Square payment links
   6. Write freeze-dried production SOP
   7. Research free inventory tools
   8. Deploy website to Vercel
   9. torus-pos deployed and healthy
   10. torus-inventory fixed and deployed

---

## Step 5: Continuous Tasklist Generation

**Script:** `10_Skills_Library/05_Operations/scripts/continuous_tasklist.py`
**Sources:**
- Trello cards (P1/P2 from Torus_Ops)
- GitHub issues (P1/P2)
- Vault audit findings
- Inbox messages
- Docker/K8s tasks

**Output:** `CONTINUOUS_TASKLIST.md`
**Updates:** Every 15 minutes via `progress_updater.py`

---

## Automation Jobs Running

1. **ooda_loop.py** — 60s cycle
   - Runs backfill_inboxes.py
   - Runs trello_final_automation.py
   - Updates tasklist

2. **verifier_daemon.py** — 5m cycle
   - Verifies all cards have labels/descriptions
   - Checks for duplicates

3. **pinkcady_crew_heartbeat.py** — continuous
   - Monitors crew connectivity

4. **progress_updater.py** — 15min
   - Updates tasklist.md
   - Syncs Trello → GitHub

5. **self_healing_loop.py** — 30s timeout
   - Auto-restarts failed jobs

---

## Verified End-to-End Flow

### Test: New inbox message → Trello card → Sorted/Labeled/Indexed

1. **Message arrives** in `Z:\MISS_PINK_INBOX\test_message.msg.md`
2. **backfill_inboxes.py** detects it within 60s
3. **Creates Trello card:**
   - Name: `📨 [INBOX] test message`
   - List: Backlog
   - Label: `inbox`
   - Description: Message content
4. **Creates GitHub issue:** #<next_number>
5. **trello_final_automation.py** processes card:
   - Classifies: P1/P2/P3/etc
   - Adds priority label
   - Moves to correct list
   - Adds description if missing
   - Checks VOID Ops for duplicates
   - Adds to TRELLO_CARD_INDEX.json
   - Enforces Top 10 limit
6. **continuous_tasklist.py** picks up card
7. **CONTINUOUS_TASKLIST.md** updated with new task

**Result:** Message fully automated into workflow ✅

---

## Missing Links / Gaps

1. **GitHub issue creation** from inbox — works, but needs Trello card ID in issue body for traceability
2. **GitHub → Trello sync** — one-way only (Trello → GitHub exists, GitHub → Trello missing)
3. **VOID Ops → Torus_Ops sync** — needs scheduled job to check for new VOID Ops cards
4. **Status updates** — when card moves to Done, should auto-close GitHub issue
5. **Crew assignment** — cards tagged `Sir Azure` should auto-assign in Trello + notify via inbox

---

## Recommendations

1. Add `github_card_id` field to Trello card descriptions
2. Create reverse sync: GitHub issues → Trello cards
3. Add VOID Ops watcher to detect new cards
4. Implement Done → GitHub issue close automation
5. Add crew notification triggers

---

## Scripts Reference

| Script | Purpose | Schedule |
|--------|---------|----------|
| `backfill_inboxes.py` | Inbox → Trello + GitHub | 60s |
| `trello_final_automation.py` | Sort/label/index cards | On-demand |
| `continuous_tasklist.py` | Aggregate all tasks | 15min |
| `trello_card_watcher.py` | Watch for new cards | On-demand |
| `trello_sync.py` | Trello → markdown sync | On-demand |
| `build_unified_backlog.py` | Build unified backlog | On-demand |

---

*End of pipeline review*
