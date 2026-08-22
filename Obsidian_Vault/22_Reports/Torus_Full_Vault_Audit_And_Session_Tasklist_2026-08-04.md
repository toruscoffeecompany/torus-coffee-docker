# Torus Coffee Company — Full Vault Audit & Session Tasklist

**Date:** 2026-08-04  
**Auditor:** Miss Pink / Hermes Agent  
**Vault:** `D:\Work\Torus Coffee Company LLC`  
**Alt Vault Reference:** `D:\Work\Hermes Alt Obsidian Vault Skills` (read-only)  
**Mode:** Read-only audit + actionable tasklist  

---

## 1. Comms Protocol Check (Sir Green Order)

- **Expected file:** `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md`  
- **Status:** ❌ Not found in vault or anywhere under `D:\Work\`  
- **Vault access path:** Confirmed. Read/write access to `D:\Work\Torus Coffee Company LLC`  
- **#torus-coffee Discord webhook:** Not located in audited files  
- **Gmail app password:** Not located in audited files  
- **Action:** Create the comms protocol file, webhook config, and credential storage plan before next ops session  

---

## 2. Last Session Completion Audit

### ✅ Completed / Verified

| Area | Evidence | Status |
|------|----------|--------|
| Vault structure | 14 numbered folders + `.obsidian`, `.git` present | ✅ Complete |
| Core Obsidian config | `.obsidian/community-plugins.json`, `workspace.json`, `graph.json`, `core-plugins.json` present | ✅ Complete |
| Plugins active | 6 plugins listed: calendar, dataview, periodic-notes, templater-obsidian, quickadd, obsidian-git | ✅ Complete |
| Broken Templater dir | `.obsidian/plugins/Templater/` exists without manifest/main.js | ⚠️ Needs cleanup |
| Git remote | `origin https://github.com/toruscoffeecompany/Torus_Ops.git` | ✅ Configured |
| Recent commits | 12 commits visible; latest `3a15e9a` on `main` | ✅ Healthy |
| GitHub sync script | `vault_sync_to_github.py` present; scheduled daily 08:30 | ✅ Present |
| Task Scheduler jobs | 18 Torus jobs reported in `VAULT_AUDIT_2026-08-04.md`; all last result `0` | ✅ Verified |
| Automation orchestrator | `automation_orchestrator.py` present; 8/8 scripts in sequence | ✅ Present |
| Crew profiles | 7 Torus-only astro profiles present under `10_Skills_Library/05_Operations/Crew/Torus_Crew/` | ✅ Complete |
| Discord package | `crew_map.json`, `chat_lines.json`, `DISCORD_ACTIVATION_GUIDE.md`, `DISCORD_BOT_DESIGNS.md`, per-officer bot design docs present | ✅ Present |
| Sir Green notification | `Torus_Crew_Roster_Notification.md` present; awaits acknowledgment | ⏳ Pending reply |
| Revenue plan | `03_Financials/Revenue_Stream_Plan.md` with 8 streams + free-tier stack | ✅ Documented |
| Social media setup | Master setup, content queue, Substack/YouTube plans present | ✅ Documented |
| Website scaffolds | `06_Website/next-storefront/`, `06_Website/Website/`, `06_Website/dashboard/`, `08_Design_Brand/` all present | ✅ Built |
| Products | 10-product catalog populated; inventory master + JSON present | ✅ Complete |
| Trello boards | 3 boards synced to markdown under `09_Projects/Trello_Boards/` | ✅ Active |
| Daily ops logs | 2026-08-03 and 2026-08-04 daily notes present with alerts/orders | ✅ Active |

### ⚠️ Partial / Needs Work

| Area | Evidence | Status |
|------|----------|--------|
| Buffer post creation | Channels verified; createPost mutation still needs schema pass | ⚠️ Partial |
| Zapier full Zaps | Webhook live; actual Zaps still need UI build | ⏳ Pending |
| HubSpot CRM | Contacts/deals API verified; full pipeline config pending | ⚠️ Partial |
| Square integration | Blocked by Veriff identity verification | 🔴 Blocked |
| Gmail send scope | Token has invalid_scope error | 🔴 Broken |
| Website deployment | Scaffolded; not yet deployed to free hosting | ⏳ Pending |
| Social accounts | X/Twitter, YouTube exist; Facebook page found but unverified; Instagram/Pinterest/TikTok/LinkedIn not created | ⏳ Pending |
| Product photos | 14 products; many placeholders; Sir Azure unblock pending | ⏳ Pending |
| Legal pages | Privacy, Terms, Accessibility drafted; not signed off | ⏳ Pending |
| Test suite | Last report said 10/10 PASS; current test scripts not visible in current scan | ⚠️ Needs rerun |
| Dashboard widgets | Scaffolded; widgets not built | ⏳ Pending |

### 🔴 Critical Issues

| Issue | Source | Severity |
|-------|--------|----------|
| Trello API key + token hardcoded in 3 scripts | `VAULT_AUDIT_2026-08-04.md` §6.2 | **High** |
| Credential files not in `.gitignore` | `.gitignore` missing credential rules | **High** |
| `08_Design_Brand/.env.example.bin` unverified binary | Vault audit §6.3 | **High** |
| Missing comms protocol + webhook + Gmail app password | Sir Green order + this audit | **High** |

---

## 3. Cross-Matrix Audit Summary

### 3.1 Vault Structure vs Documentation

- **Actual:** 14 canonical numbered folders present  
- **Collision:** `06_Growth_Marketing` and `06_Website` share `06_` prefix; `08_Archive`, `08_Design_Brand`, `08_Reports` share `08_`  
- **Impact:** Automation paths are still correct because full paths are used, but human navigation and future scripts can be ambiguous  

### 3.2 Plugin/Automation Health

- **Plugins:** 6 active; 1 broken empty dir (`Templater/`)  
- **Templates:** 13 templates present in `00_Inbox/07_Templates/`  
- **Dashboards:** 4 Dataview dashboards; all source files resolve  
- **Task Scheduler:** 18 Torus jobs; scripts exist; last run results `0`  

### 3.3 Content Quality

- **Trello cards:** 337 total across 3 boards  
- **Broken wikilinks:** 36 in Trello board list files (`[[Card_*]]` missing list subfolder)  
- **Duplicates:** 296 duplicate filenames, 297 case collisions, 35 duplicate image pairs  
- **Obsolete code:** `test_integrations.py`, `test_suite.py` still present  

### 3.4 OPSEC / Secrets

- **Hardcoded secrets:** Trello key+token in `trello_sync.py`, `trello_audit.py`, `generate_asset_request.py`  
- **Credential files:** `buffer_credentials.json`, `hubspot_credentials.json`, `zapier_credentials.json`, `Trello_API_Credentials.md`  
- **Git exposure risk:** `.gitignore` does not exclude credential files  

### 3.5 GitHub Sync Readiness

- **Remote:** `toruscoffeecompany/Torus_Ops`  
- **Branch:** `main`  
- **Status:** Local dirty: `.obsidian/workspace.json`, daily note, `orders.json`, backup script, `alerts.json`, plus untracked `VAULT_AUDIT_2026-08-04.md`  
- **Push readiness:** Needs commit + push; credential files must be gitignored first  

---

## 4. Detailed Tasklist

### P0 — Do Today

1. **Create `02_Business_Operations/Communications/MISS_PINK_COMMUNICATION_PROTOCOL.md`**  
   - Define comms path, webhook routing, credential storage rules, alert routing

2. **Locate or create #torus-coffee Discord webhook config**  
   - Store webhook URL in approved credentials location only  
   - Add to `crew_map.json` / comms protocol if needed

3. **Locate or rotate Gmail app password**  
   - Fix `invalid_scope` by regenerating OAuth token with `gmail.send`  
   - Document in `01_Operating/Operating Paperwork/Google Workspace Access.md`

4. **Rotate Trello API key + token**  
   - Rotate at trello.com/app-key  
   - Update `Trello_API_Credentials.md`  
   - Patch `trello_sync.py`, `trello_audit.py`, `generate_asset_request.py` to read from credential file

5. **Update `.gitignore`**  
   - Add credential patterns: `*credentials*.json`, `*credentials*.md`, `.env.local`, `.env`  
   - Add `**/node_modules/`, website build artifacts if missing

6. **Commit + push current vault changes**  
   - Review dirty files  
   - Commit with descriptive message  
   - Push to `Torus_Ops` only after `.gitignore` is updated

### P1 — This Week

7. **Remove broken `.obsidian/plugins/Templater/` directory**  
   - Active Templater is `templater-obsidian/`; remove empty/broken dir

8. **Fix 36 broken Trello wikilinks**  
   - Update `09_Projects/Trello_Boards/*.md` list files to use `[[List/Card_*]]` paths

9. **Delete 35 duplicate image pairs in `08_Design_Brand/`**  
   - Keep canonical copies in primary subfolders

10. **Inspect `08_Design_Brand/.env.example.bin`**  
    - Determine if real `.env` misnamed  
    - Move secrets to approved credentials location if needed  
    - Add to `.gitignore`

11. **Rerun full test suite**  
    - Verify 10/10 PASS still holds after recent changes

12. **Verify Task Scheduler paths**  
    - Confirm all 18 jobs point to existing scripts with correct interpreter paths

### P2 — Next Week

13. **Delete obsolete scripts**  
    - Move `test_integrations.py`, `test_suite.py` to `08_Archive/`

14. **Fix website build/case-collision issue**  
    - Ensure canonical lowercase folder is used; remove duplicate if present

15. **Deploy website to free hosting**  
    - Netlify/Vercel free tier  
    - Connect Square Payment Links or Formspree

16. **Create missing social accounts**  
    - Pinterest, TikTok, LinkedIn  
    - Convert Instagram or create new business account

17. **Complete Buffer post schema**  
    - Finish GraphQL `createPost` mutation pass

18. **Build 3 Zapier Zaps in UI**  
    - Trello card → webhook  
    - Google Form → Trello card  
    - Calendar event → Buffer post

### P3 — Ongoing / Nice-to-Have

19. **Finalize legal page sign-off**  
    - Privacy, Terms, Accessibility review

20. **Complete product photos**  
    - Strategy for non-Sir-Azure photo completion

21. **HubSpot full CRM config**  
    - Import contacts, set deal pipelines

22. **Add website → Obsidian data connection**  
    - Inventory sync, dynamic product data

23. **Resolve prefix collisions in vault root**  
    - Consider renaming `06_Growth_Marketing` → `06a_Growth_Marketing` or similar  
    - Consider renaming duplicate `08_*` folders

24. **Acknowledge Sir Green crew roster notification**  
    - Confirm Docker readiness, Tailscale connectivity, Shared_With_Pink bridge access

---

## 5. Verification Checklist

- [ ] Comms protocol file created and reviewed
- [ ] Webhook URL stored securely, not in git
- [ ] Gmail send scope fixed and tested
- [ ] Trello API credentials rotated and no longer hardcoded
- [ ] `.gitignore` updated and verified
- [ ] Vault committed and pushed to `Torus_Ops`
- [ ] Broken `Templater/` plugin dir removed
- [ ] Trello wikilinks fixed
- [ ] Duplicate images removed
- [ ] `.env.example.bin` inspected/secured
- [ ] Test suite rerun and passing
- [ ] Task Scheduler paths verified
- [ ] Website deployed
- [ ] Social accounts created
- [ ] Buffer post schema complete
- [ ] Zapier Zaps built
- [ ] Legal pages signed off
- [ ] Sir Green notification acknowledged

---

*Audit generated by Hermes Agent — Torus Coffee Company vault audit, 2026-08-04.*
