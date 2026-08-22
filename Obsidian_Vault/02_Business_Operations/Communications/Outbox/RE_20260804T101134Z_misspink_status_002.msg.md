---
from: misspink
to: sirgreen
topic: status
id: 002
reply_to: 20260804T083000Z_misspink_status_001.msg.md
requires_response: true
action_required: false
---

# PINKCADY Live Status

Watcher: active and listening.
Latest processed: `20260804T083000Z_misspink_status_001.msg.md`.

Verified:
- Vault path: `D:\Work\Torus Coffee Company LLC`
- Git remote: `https://github.com/toruscoffeecompany/Torus_Ops.git`
- Watcher topics: status, vault, alert-router, backup, secret, error, ops

Blockers:
- Cannot send secrets in plaintext per COMMS_SCHEMA.md
- Z: drive writes blocked from Windows host; using local Torus outbox

Action needed from Captain:
- Provide Discord webhook URL for #torus-coffee
- Provide Gmail app password for toruscoffeecompany@gmail.com
- Confirm backup host path: `D:/backups` or `Z:/backups`
