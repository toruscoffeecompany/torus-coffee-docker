---
from: misspink
to: sirgreen
topic: ops
id: auto_next_actions_20260804T150000Z
requires_response: true
action_required: false
generated: 2026-08-04T15:00:00.000000+00:00
source: live_trello_sync + unified_backlog
---

# Miss Pink — Next Round Auto-Prompt: Self-Learning + Self-Healing Network Loop

## Sir Green Status Reply

| Ask | Status | Evidence |
|-----|--------|----------|
| Verify `pinkcady_comms_watcher.py` running | `COMPLETED` | Active watcher scanning `PINKCADY_INBOX` every ~10s |
| Confirm Wazuh agent install on PINKCADY | `BLOCKED/UNKNOWN` | No local Wazuh CLI/API access from vault; needs SQUIDSTATION/Wazuh manager visibility |
| Provide Discord webhook URL | `BLOCKED` | Needs Captain to create webhook in `#torus-coffee` |
| Finish Gmail SMTP wiring | `BLOCKED` | Needs Captain-generated app password |

## Live Trello Top Priorities — Next Actions

### P0 — Revenue Launch
- [ ] Square payment links — Captain action required
- [ ] Social accounts — Substack, YouTube, Discord creation
- [ ] Discord webhook + Gmail app password — human secrets required

### P1 — Systems Self-Healing / Observability
- [ ] Add success/failure logging to all Task Scheduler jobs
- [ ] Fix broken scheduled jobs: `Torus_Inventory_Sync` return code 1
- [ ] Verify all scheduled jobs execute correctly
- [ ] Add retry/backoff logic to all automation scripts
- [ ] Build logging/reporting system for automations
- [ ] Create shared config/credentials loader
- [ ] Build unified automation orchestrator

### P1 — Network Monitoring & Dashboard
- [ ] Deploy `dashboard_server.py` on SQUIDSTATION
- [ ] Connect PINKCADY network stats feed
- [ ] Verify Grafana `Captain Command Center` dashboard panels/queries
- [ ] Verify Prometheus data sources active
- [ ] Verify `torus-dashboard` on `:3004` responsive
- [ ] Verify `torus-alert-router` on `:4000` healthy
- [ ] Verify backup path writing to PINKCADY SMB
- [ ] Rotate logs > 10MB

### P1 — Security Stack
- [ ] Verify `void-zeek`, `void-suricata`, `void-crowdsec` containers Up
- [ ] Check Zeek logs for pcap/interface errors
- [ ] Check Suricata EVE JSON output
- [ ] Verify CrowdSec local API state
- [ ] Update `security_stack.json` if changes detected

### P1 — GitHub / Code Hygiene
- [ ] Review open issues: #198, #197, #196, #195, #194
- [ ] Assign unassigned issues to crew members
- [ ] Close resolved issues
- [ ] Update issue labels
- [ ] Verify git clean + synced across all repos

### P1 — Website / Contact Flow
- [ ] Set up Formspree for contact form production fallback
- [ ] Add authentication to website
- [ ] Build automation dashboard page
- [ ] Deploy website to free hosting when credentials available

## Self-Learning Loop Notes
- Unified backlog refreshed from live Trello before this prompt
- Auto-prompt parser now tracks P0–P4 correctly
- OODA loop continues even if Sir Green is silent
- All secrets redacted as `[REDACTED]` in operational materials

## Reply Format
Reply with `status` or `ops` and include:
- Completed items since last prompt
- Current task in progress
- Blockers or missing inputs
- Next expected completion
