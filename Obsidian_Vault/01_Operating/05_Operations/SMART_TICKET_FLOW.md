# Smart Ticket Flow — Torus Coffee OODA System

## Purpose
Intake → classify → route → verify → close. Two new inbox lists are the entry points.

## List IDs (Torus_Ops board 6a70a3157d0db4214ac3f9a3)
- **Miss Pink's Inbox:** `6a75869a95f875e18db6c081` — new intake for Torus_Ops
- **Sir Green's Queue:** `6a74cbd679972be49ea46dae`
- **Sir Azure's Queue:** `6a74cbd51b2662f6cdc37cce`
- **Done:** `6a70a32a723c0312a3d5fbb4`

## List IDs (VOID Ops board 6a595669b8f8f99c93392f4f)
- **Sir Green's Inbox:** `6a7539616c45ba06ed57b32a`
- **Miss Pink's Queue:** `6a74dd281f14ade0e0956cfc9`
- **Done:** `6a595669b8f8f99c93392f6c`

---

## Flow: Miss Pink's Inbox (Torus_Ops)

### Intake
New tickets arrive here from:
- Crew inbox messages (/z/SIR_GREEN_INBOX, /z/SIR_AZURE_INBOX)
- Automated alerts (dashboard health, Docker push results, scheduler failures)
- GitHub issue sync (new issues auto-create cards here)

### Classify (keyword rules → action)
| Keyword in title/desc | Priority | Route To |
|----------------------|----------|----------|
| "P0", "CRITICAL", "ALERT", "EMERGENCY", "BLOCKED" | P0 | P0 - Alert list |
| "sir green", "sirgreen", "dashboard", "/api/" | P1 | Sir Green's Queue |
| "sir azure", "sirazure", "comfy", "cuda", "gpu" | P1 | Sir Azure's Queue |
| "github", "auth", "deploy", "push", "docker hub" | P1 | P1 - High list |
| "calendar", "sync", "schedule" | P2 | P2 - This Week list |
| "scan", "audit", "review" | P3 | P3 - Follow Up |
| "future", "idea", "backlog", "nice to have" | P4 | Future Ideas |
| None of above | P2 | P2 - This Week (default) |

### Route
Move card to classified list. Add priority label. Comment with classification reason.

### Verify (gate before Done)
1. Direct read of source system (GitHub issue status, Discord webhook, script output)
2. Evidence must be in card description: `VERIFIED_DONE: <evidence>`
3. Only then: stamp + move to Done

### Close
When Done card sits 7 days with no activity → auto-archive.

---

## Flow: Sir Green's Inbox (VOID Ops)

### Intake
Tickets from VOID Ops automation, SQUIDSTATION alerts, Sir Green's direct messages.

### Cross-Board Sync Rule
Any card in **Sir Green's Inbox (VOID Ops)** that references a Torus_Ops card → create mirrored card in **Sir Green's Queue (Torus_Ops)** with cross-link in description. Primary tracking stays on Void_Ops board; Torus_Ops card = lightweight sync stub.

### Intake → Classify
Same keyword rules as above. Sir Green's Inbox items route to:
- VOID Ops P0/P1/P2 (for Void Pirate work)
- Sir Green's Queue on Torus_Ops (for Torus_Ops work Sir Green owns)
- Done (when already completed)

### Verify
Same gate: direct read of VOID Ops sources → stamp → Done.

---

## Cross-Board Sync Protocol

### 1. Torus → Void (when Torus task becomes Void task)
- Move card to Sir Green's Queue (Torus_Ops)
- Create child card in VOID Ops appropriate priority list
- Comment on both: cross-linked card ID

### 2. Void → Torus (when Void task becomes Torus task)
- Move to Miss Pink's Inbox (Torus_Ops)
- Classify → route to priority list
- Comment cross-link to Void_Ops card

### 3. Duplicate Prevention
- Before creating a mirrored card, check if target board list already has a card with same title
- If duplicate found: comment cross-link on both, archive newer duplicate
- Maintain `cross_board_sync_log.json` in `10_Skills_Library/05_Operations/`

### 4. Ownership Tags
- Sir Green's tasks: label "Sir Green's Queue"
- Sir Azure's tasks: label "Sir Azure's Queue"  
- Miss Pink's tasks: label "automation"
- Shared/cross-team: label "ops"

---

## Automation
- **OODA Loop (60s):** Reads inbox lists, classifies, routes
- **Verifier Daemon (5m):** Checks Done cards for VERIFIED_DONE stamp
- **Self-Healing (30s):** Re-queues failed cards back to Miss Pink's Inbox
- **Progress Updater (15m):** Posts status comments to Trello + GitHub

## Nightly Calendar Sync
- Script: `nightly_calendar_sync.py` in `10_Skills_Library/05_Operations/scripts/`
- Runs daily at 02:00 via Windows schtasks
- Batch writes: 10 cards per batch, 5s delay between batches
- Syncs near-term Top 10 + P1 Trello cards to Google Calendar
- Uses redacted `[REDACTED]` Google API key
- Never passes `timeout` into googleapiclient discovery methods

## Safety Rules
- Never move Top 10 cards without replenishment (top10=10 must stay exact)
- Never modify Sir Green's dashboard code or /api/* routes
- Never scan full vault (timeouts) — use targeted reads only
- All credentials redacted as [REDACTED] in comments
- Free-tier tools only
