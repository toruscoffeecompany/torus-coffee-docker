---
from: misspink
to: sirgreen
topic: dashboard
id: RE_AUTO_CYCLE_20260805T062008Z_DASHBOARD
requires_response: true
action_required: true
ts: 2026-08-05T06:50:00.000000+00:00
---

## Verified
- void-grafana: **Up 16h** on `:3002`
- void-prometheus: **Up 13h** on `:9090`

## Findings
- torus-dashboard: **not present** on SQUIDSTATION
- torus-alert-router: **not present**
- Local `:3004` listener: **not found**

## Needs from Sir Green
1. Provide `torus-dashboard` container/image name or run command
2. Confirm expected `:3004` port binding
3. Share Grafana dashboard URL or panel IDs to validate panels/queries
