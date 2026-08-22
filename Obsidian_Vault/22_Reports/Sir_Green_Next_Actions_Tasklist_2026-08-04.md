# Torus Coffee Company — Sir Green Next Actions Tasklist
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** In Progress
**Waiting On:** Sir Green lane write access / human Discord setup

## Sir Green Request
- Reply location: `Miss_Pink_Bridge/MISS_PINK_REPLY.md`
- Move Trello cards to Doing
- Provide Discord webhook URL for `#torus-coffee`
- Confirm heartbeat from PINKCADY → SQUIDSTATION dashboard

## Task List

### 1) Sir Green Comms Reply
- [x] Attempted to create `Miss_Pink_Bridge/MISS_PINK_REPLY.md`
- [x] Z: drive write blocked by permission
- [ ] Fallback: write reply to local outbox and note Z: limitation
- [ ] Notify Sir Green to confirm write access or alternate path

### 2) Trello Cards → Doing
- [ ] Update Website_Rebuild cards: legal/about/products → Doing
- [ ] Update Business_Docs cards: Supplier Agreement Template → Doing
- [ ] Update Torus_Ops cards: safe Pink work → Doing
- [ ] Verify 382/382 cards status updated

### 3) Discord Webhook
- [ ] Acknowledge webhook is still blocked: requires human creation in Discord
- [ ] Document exact steps for Captain/Miss Pink to create webhook
- [ ] Placeholder config exists at `10_Skills_Library/05_Operations/Docker/torus-alert-router/config/discord.json`
- [ ] Do NOT invent webhook URL

### 4) Heartbeat PINKCADY → SQUIDSTATION
- [ ] Create local heartbeat state file: `10_Skills_Library/05_Operations/Crew/.heartbeat_pinkcady.json`
- [ ] Write heartbeat timestamp every 5 minutes
- [ ] Expose heartbeat via local API or file for Squidstation dashboard
- [ ] Document Squidstation-side heartbeat reader needs
- [ ] Note: full dashboard heartbeat requires Squidstation host decision + dashboard service

## Verification Checklist
- [ ] Local outbox contains Sir Green reply
- [ ] Trello cards moved to Doing
- [ ] Discord webhook status documented as blocked/human-required
- [ ] Heartbeat state file active
- [ ] Git commit + push
- [ ] No file mutations on shared paths
