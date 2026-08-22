# Torus Coffee Company — Crew Communications System

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Classification:** Torus-only — legal separation from VOID Pirate Trading Co

---

## Overview

This document defines how the Torus Coffee Company AI crew communicates.  
All crew members work **exclusively for Torus Coffee Company** under Miss Pink’s command.

**Legal separation rule:**  
Torus crew, vaults, automations, and secrets are completely separate from VOID Pirate Trading Co.  
Only shared infrastructure (SQUIDSTATION Docker, Z: drive bridge) is common.

---

## Crew Roster (Torus Only)

| Rank | Name | Role | Station | Reports To |
|------|------|------|---------|------------|
| 0 | Captain Brewbeard Ledgerbane | Captain / Final Authority | PINKCADY | — |
| 1 | Miss Pink | Operations / Torus Lead | PINKCADY | Captain |
| 2 | Sir Azure Steelwake | Render Midshipman | STEALTHATTACK | Miss Pink |
| 3 | Accountant Goldweigh | Bookkeeper | PINKCADY | Miss Pink |
| 3 | Lawyer Ironclad | Compliance | PINKCADY | Miss Pink |
| 3 | CPA Taxman | Tax / IRS | PINKCADY | Miss Pink |
| 4 | Strategy Officer Northstar | Strategy / KPIs | PINKCADY | Miss Pink |
| 4 | Ops Officer Keelhaul | Operations | PINKCADY | Miss Pink |
| 4 | Marketing Officer Crow | Marketing | PINKCADY | Miss Pink |
| 4 | Inventory Manager Cargo | Inventory | PINKCADY | Miss Pink |

---

## Communication Channels

### Discord (Primary)
- Server: `Torus Coffee Company Crew`
- Channels: `#captain-dm`, `#ops-general`, `#finance`, `#marketing`, `#legal`, `#inventory`, `#render`
- Each crew member has own bot instance

### Obsidian Vault (Source of Truth)
- Local vault: `D:\Work\Torus Coffee Company LLC`
- Crew folder: `10_Skills_Library/05_Operations/Crew/`
- Comms logs: `10_Skills_Library/05_Operations/Crew/comms_log.jsonl`

### Relay Queue (Cross-Station)
- File: `Z:\Developer_Brain\Shared_With_Pink\relay_queue.jsonl`
- Format: JSONL, one message per line
- Shared with SQUIDSTATION read-only

### Gmail (External)
- toruscoffeecompany@gmail.com
- Alert router: Critical → email, Warning → Obsidian, Info → log

---

## Message Flow

```
Crew member sends message
    ↓
Discord bot / script
    ↓
Alert router (severity-based)
    ↓
├─ Critical → Gmail + daily note
├─ Warning → Obsidian daily note
├─ Info → log file
└─ Debug → console
    ↓
Relay queue (for cross-station)
    ↓
Trello card (if action item)
```

---

## Legal Separation Rules

1. **Vault separation:** Torus vault on PINKCADY, VOID vault on SQUIDSTATION
2. **Crew separation:** Torus crew bots never access VOID data
3. **Secret separation:** Torus credentials in Torus vault only, never in VOID
4. **Git separation:** Torus repos vs VOID repos, never mixed
5. **Docker separation:** Torus containers use `torus-*` prefix
6. **Communication separation:** Torus Discord server vs VOID Discord server

---

## Activation Sequence

1. [ ] Create Torus Discord server
2. [ ] Create bot applications for each crew member
3. [ ] Upload icons/banners
4. [ ] Add tokens to local `.env` (never committed)
5. [ ] Test all bots
6. [ ] Verify relay queue communication
7. [ ] Notify Sir Green: Torus crew is live, legal separation confirmed

---

## Status

- ✅ Crew personas created
- ✅ Discord bot designs created
- ✅ Communications protocol documented
- ⏳ Awaiting Discord server creation + bot activation

---

## Next Steps

1. **Miss Pink:** Create Torus Discord server
2. **Miss Pink:** Create bot applications, upload assets
3. **Sir Green:** Receive notification of Torus crew roster
4. **All crew:** Test communication channels
