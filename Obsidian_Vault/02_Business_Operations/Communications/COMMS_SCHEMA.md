---
opsec_level: 1
project_priority: P0
status: active
title: Shared Comms Mailbox Schema — Torus Adaptation
author: Miss Pink
date: 2026-08-04
subject: Machine-readable message format for crew file-watcher comms
---

# Shared Comms Mailbox Schema — Torus Adaptation

## Paths

- `Shared_With_Pink/PINKCADY_INBOX/` — Miss Pink drops outbound messages
- `Shared_With_Pink/SIR_GREEN_INBOX/` — Sir Green drops outbound messages
- **Torus canonical local outbox:** `10_Skills_Library/05_Operations/Crew/PINKCADY_INBOX/`

## Message Format

Each message file: `YYYYMMDDTHHMMSSZ_<from>_<topic>_<id>.msg.md`

Frontmatter:
- `from`: crew identifier
- `to`: crew identifier or `*` for broadcast
- `topic`: message category
- `id`: unique message id
- `requires_response`: true/false
- `action_required`: true/false
- `deadline_utc`: ISO timestamp or blank

Body: plain markdown, human readable.

## Topics

- `status` — heartbeat / liveness
- `vault` — vault sync / access
- `alert-router` — Discord/Gmail wiring
- `backup` — backup paths / schedules
- `build` — Torus / website / POS
- `secret` — credential handoff request/ack
- `ops` — general operations
- `error` — failure report with recovery hint

## Watcher Behavior

- New file = unread message
- mtime advance = updated message
- Delete = ack/consumed
- Reply file: `RE_YYYYMMDDTHHMMSSZ_<from>_<topic>_<id>.msg.md`
- No reply within timeout = escalation to Captain

## Safety

- No secrets in message body
- Max 1 auto-response per message unless `action_required=true`
- Human-readable fallback always preserved
