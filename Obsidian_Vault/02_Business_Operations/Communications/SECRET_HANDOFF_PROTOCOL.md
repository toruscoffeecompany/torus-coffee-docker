# Secure Secret Handoff Protocol — Torus Coffee Company

**Date:** 2026-08-04  
**Status:** Required before live alert router activation  
**Policy:** No plaintext secrets in comms, git, or logs  

---

## Required Secrets
1. Discord webhook URL for #torus-coffee
2. Gmail app password for toruscoffeecompany@gmail.com
3. Confirmed backup host path: D:/backups or Z:/backups

## Handoff Rules
- Do not transmit secrets via plaintext email, chat, or `.msg.md` files.
- Use one of the approved methods below.
- Rotate immediately if a secret is exposed.

## Approved Handoff Methods

### A. Captain Physical Passoff
- Handoff in person or via encrypted USB.
- Store in approved credentials file only.
- Files are redacted from git via `.gitignore`.

### B. Password Manager Share
- Use 1Password/Bitwarden family/team vault.
- Share with `misspink` and `sirgreen` crew identities only.
- Record share confirmation in `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md`.

### C. Encrypted File on Vault Root
- Create `10_Skills_Library/05_Operations/secrets.enc`.
- Encrypt with GPG or AES-256.
- Share decryption key via method A or B.

## Once Received
1. Store secrets in approved credentials file.
2. Update `alert_router.py` or equivalent config.
3. Test alert delivery end-to-end.
4. Commit config changes (never the secrets themselves).
5. Update Trello card `6a71b462b21cd08f9f3f6eb9` status.

## Failure Path
- If no secure handoff is available within 24 hours, escalate to Captain.
- Do not use fallback plaintext methods.
