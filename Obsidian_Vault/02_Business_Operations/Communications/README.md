# Shared Bridge — Crew Comms Protocol — Torus Adaptation

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Classification:** Torus-only  

## Purpose

Automated learning comms between Miss Pink and Sir Green via local network file shares.

## How It Works

1. Miss Pink writes `.msg.md` files into `PINKCADY_INBOX/`
2. Sir Green's watcher picks them up, acts, and writes `RE_*.msg.md` into `PINKCADY_INBOX/`
3. Miss Pink's watcher picks replies up and can continue the thread
4. Captain can read both inboxes at any time

## File Format

See `COMMS_SCHEMA.md` for exact format.

Quick example filename:
`20260804T083000Z_misspink_status_001.msg.md`

## Torus Local Paths

Because Z: write access from PINKCADY may be restricted, Torus uses:

- **Local outbox/inbox:** `10_Skills_Library/05_Operations/Crew/PINKCADY_INBOX/`
- **Shared bridge:** `Z:\Developer_Brain\Shared_With_Pink\` (read-only from PINKCADY unless write access is granted)

## Automation

- `pinkcady_comms_watcher.py` — Pink watcher
- `sirgreen_comms_watcher.py` — Sir Green watcher
- Both should run as background services / scheduled tasks

## Crew Contacts

- Sir Green: SQUIDSTATION `192.168.0.39`
- Miss Pink: PINKCADY `192.168.0.3`
- Shared vault path: `\\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink\`

## Rules

- No secrets in message bodies
- Keep messages actionable
- If no reply in reasonable time, escalate to Captain via Discord
