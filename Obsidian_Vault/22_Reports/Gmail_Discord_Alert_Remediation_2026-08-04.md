# Gmail + Discord Alert Remediation — Torus Coffee Company

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Status:** Documented — human action required for final fix  

---

## Gmail — Invalid Scope / Spam Issue

### Current state
- Auth file: `C:\Users\torus\AppData\Local\hermes\google_token.json`
- Connected account: `toruscoffeecompany@gmail.com`
- Known issue: Zapier Zap is sending empty `Torus Automation Alert` emails to self
- Long-term issue: Gmail send scope missing for programmatic alerts

### Immediate fix (do now)
1. In Gmail, create filter:
   - From: `toruscoffeecompany@gmail.com`
   - Subject: `Torus Automation Alert`
   - Action: Delete / Skip Inbox / Also apply to matching conversations
2. In Zapier, disable or delete the webhook→Gmail Zap using URL `https://hooks.zapier.com/hooks/catch/28444713/4616r0w/`

### Programmatic fix (needs human browser step)
1. Open Google Cloud Console for `toruscoffeecompany@gmail.com`
2. Ensure OAuth consent screen includes `gmail.send` scope
3. Regenerate token/refresh via browser consent flow
4. Store new token path in `01_Operating/Operating Paperwork/Google Workspace Access.md`

### Vault-only fallback
- Disable email alerts entirely
- Route all alerts to `00_Inbox/01_Daily/` Obsidian notes only
- Update `zapier_credentials.json` to `"alert_mode": "vault_only"` (already set)

---

## Discord — #torus-coffee Webhook Missing

### Current state
- No `#torus-coffee` webhook URL found in vault
- Discord assets and bot designs exist under `02_Business_Operations/Communications/Discord/`
- Crew bot designs exist for Sir Green, Sir Cobalt, Sir Violet, Scarlett Coralsink, Sons PC Azure

### Steps to create webhook
1. Open Discord server → `#torus-coffee` channel
2. Channel Settings → Integrations → Webhooks → New Webhook
3. Name: `Torus Coffee Alerts`
4. Copy webhook URL
5. Store URL in approved credentials location only; do NOT commit to git

### Required follow-up
- Update `crew_map.json` with webhook URL reference
- Update `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md` with webhook routing
- Add webhook delivery path to `alert_router.py`

---

## Verification status
- [x] Gmail auth documented and existing
- [x] Spam source identified (Zapier)
- [ ] Gmail send scope regenerated — **human action required**
- [ ] Discord webhook created — **human action required**
- [ ] Webhook URL stored securely and wired into alert router
