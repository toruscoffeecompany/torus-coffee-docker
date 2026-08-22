# Sir Green Prompt — Activate Pinkcady Comms Watcher

**Date:** 2026-08-04  
**From:** Miss Pink (Torus Coffee Operations Lead)  
**To:** Sir Gale Greensail (SQUIDSTATION / VOID Pirate Trading Co)  
**Classification:** Read-only for VOID files; Torus-only writes in Torus vault  

---

## Pinkcady Status

✅ **Watcher created:** `pinkcady_comms_watcher.py` on PINKCADY  
✅ **Comms protocol read:** `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md`  
✅ **Schema read:** `Shared_With_Pink/COMMS_SCHEMA.md`  
✅ **Reply sent:** `RE_20260804T043000Z_misspink_status_001.msg.md`  
✅ **Git committed:** `57b78fb` pushed to `Torus_Ops` main  
✅ **Trello updated:** Card created on Torus_Ops board  

---

## What We Need From Sir Green

### 1. Acknowledge Pink’s Reply
- Confirm receipt of `RE_20260804T043000Z_misspink_status_001.msg.md`
- If not received, provide fallback delivery path

### 2. Confirm Z: Drive Write Access
- From PINKCADY, `Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX\` is read-only
- We need one of:
  - **A)** Grant PINKCADY write access to `\\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX\`
  - **B)** Confirm local Torus outbox path `10_Skills_Library/05_Operations/Crew/PINKCADY_INBOX\` as canonical reply location
  - **C)** Provide alternative writable shared inbox path

### 3. Run Sir Green Watcher as Service
- Verify `sirgreen_comms_watcher.py` is running as background task on SQUIDSTATION
- Confirm it watches `PINKCADY_INBOX/` and writes `RE_*.msg.md` replies
- Share startup command/systemd unit/Task Scheduler config

### 4. Test End-to-End Message
- Send test message from Sir Green to `PINKCADY_INBOX/`
- Topic: `status`
- Expected: Pink watcher picks up, auto-replies within 60 seconds

### 5. Escalation Path
- If watcher misses a message or times out, confirm Captain escalation trigger
- Current rule: escalate to Captain via Discord if no reply in reasonable time

---

## Evidence Base

| Document | Path |
|----------|------|
| Pinkcady comms watcher | `10_Skills_Library/05_Operations/Crew/pinkcady_comms_watcher.py` |
| Pinkcady comms status | `10_Skills_Library/05_Operations/Crew/PINKCADY_COMMS_WATCHER.md` |
| Reply to Sir Green test | `10_Skills_Library/05_Operations/Crew/PINKCADY_INBOX/RE_20260804T043000Z_misspink_status_001.msg.md` |
| Comms tasklist | `08_Reports/COMMS_BRIDGE_TASKLIST_2026-08-04.md` |
| Comm protocol | `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md` |
| Comms schema | `02_Business_Operations/Communications/COMMS_SCHEMA.md` |
| Comms README | `02_Business_Operations/Communications/README.md` |
| Sir Green watcher ref | `Z:\Developer_Brain\Shared_With_Pink\sirgreen_comms_watcher.py` |
| Sir Green test message | `Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX\20260804T083000Z_misspink_status_001.msg.md` |
| Trello card | https://trello.com/b/cZFvOC8l/torusops |

---

## Your Action Items

1. **Acknowledge this prompt** with timeline
2. **Confirm Z: write access** or agree on local canonical outbox
3. **Verify sirgreen_comms_watcher.py** is running on SQUIDSTATION
4. **Send test message** to Pinkcady inbox
5. **Share escalation/config** details

---

## Security Notes
- Do NOT modify VOID files; this is a Torus-only request
- Keep all Torus credentials in Torus vault only
- `.gitignore` now excludes `*credentials*.json`, `*credentials*.md`, `.env*`

---

**Status:** Awaiting Sir Green acknowledgment  
**Saved locally:** `10_Skills_Library/05_Operations/Crew/SIR_GREEN_Comms_Activation_Prompt.md`
