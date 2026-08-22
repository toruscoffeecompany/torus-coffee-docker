# 08 — Trello Key Rotation Runbook (COMPLETE)

## Status: ✅ ROTATED AND CONNECTED

The old Trello key/token were exposed in git history commit `070e90e`. We generated a new OAuth token and connected successfully.

## What We Did
1. Generated new Trello OAuth token via https://trello.com/power-ups/admin
2. Saved new key/token to `01_Operating/Operating Paperwork/Trello_API_Credentials.md`
3. Created 3 real Trello boards via API:
   - **Torus_Ops:** https://trello.com/b/cZFvOC8l/torusops (26 cards)
   - **Business_Docs:** https://trello.com/b/JmUh5kJA/businessdocs (11 cards)
   - **Website_Rebuild:** https://trello.com/b/orPSpaRA/websiterebuild (1 card)
4. Synced all cards from vault markdown files to live Trello

## Rotation Checklist
- [x] New key+token generated
- [x] Old pair burned (no longer used)
- [ ] History scrub (if commit 070e90e is in a repo we push)

## Future Rotations
1. Go to https://trello.com/power-ups/admin
2. Open your Power-Up
3. Generate new token
4. Update `Trello_API_Credentials.md`
5. Re-sync boards
