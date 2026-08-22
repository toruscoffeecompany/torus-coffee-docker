# Vault Audit Report
**Date:** 2026-08-04  
**Vault:** `D:\Work\Torus Coffee Company LLC`  
**Auditor:** Hermes Agent (automated)  
**Files audited:** ~45,490 (excluding system directories)  
**Top-level folders:** 22 (including .git, .obsidian)

---

## Executive Summary

| Category | Finding | Severity |
|----------|---------|----------|
| Duplicates | 296 duplicate names, 297 case collisions, 35 duplicate images | Medium |
| Obsolete code | 2 test scripts, broken Templater plugin, 31 node_modules | Low |
| Task Scheduler | 18/18 Torus jobs present, all scripts exist, all returning Last Result 0 | OK |
| Broken paths | 36 broken wikilinks in Trello boards (wrong relative paths) | Medium |
| Dataview | 11 dashboard files; all source files exist | OK |
| Secrets | **CRITICAL:** Hardcoded Trello API key+token in 3 scripts; real creds not in .gitignore | **High** |

**Overall health:** Moderate. Automation is healthy, but secrets management and duplicate cleanup need immediate action.

---

## 1. Duplicate Files

### 1.1 Duplicate Names (296 files)
Most duplicates are expected framework artifacts:
- **Next.js build output:** `page.tsx` (41x), `page.js` (27x), `page.ts` (25x), `0.pack`/`1.pack`/`2.pack`, `index.html`, `globals.css`, `next-env.d.ts`, `tsconfig.json` across `06_Website/next-storefront/`, `06_Website/Website/`, `06_Website/Design/Website/`, `06_Website/dashboard/`, `08_Design_Brand/`
- **Folder index files:** `index.md` (20x) and `_INDEX.md` (8x) — intentional per-folder navigation files
- **README.md** (19x) — normal across sub-projects
- **Dockerfile** (6x) — normal across Docker services
- **Product photos:** `ANMP0001.jpg` through `ANMP0012.jpg` duplicated across `04_Products/`, `06_Growth_Marketing/`, and `07_Photos/`
- **Social media templates:** `instagram-1080x1080-v1.png` (8x) — one per category in `08_Design_Brand/Social_Media_Templates/`

**Action:** No action needed for framework artifacts and folder indexes. Consolidate product photos into single source of truth per SKU; consider linking instead of copying.

### 1.2 Case Collisions (297 name variants)
Nearly all case collisions are the same Next.js build artifacts listed above. Windows filesystem is case-insensitive, so these don't cause runtime errors within Windows but cause issues on case-sensitive systems (WSL, Linux, CI/CD).

**Action:** None urgent for local Windows use. Consider cleanup if repo is ever used on Linux.

### 1.3 Duplicate Images with Identical Content (35 pairs)
Found 35 image files with exact same MD5 hash stored in two locations:
- **Website backgrounds:** 7 pairs between `06_Website/Design/` and `06_Website/Website/`
- **Signage designs:** 24 pairs between `08_Design_Brand/` root and `08_Design_Brand/Signage/<Product>/`
- **Logos/watermarks:** 4 pairs between `08_Design_Brand/` root and `Logos/` or `Watermarks/` subfolders

**Action:** Delete the duplicate copies. Keep files in their primary subfolder location.

---

## 2. Obsolete / Unused Code

| File | Status | Recommendation |
|------|--------|----------------|
| `10_Skills_Library\05_Operations\scripts\test_integrations.py` | Obsolete test script | Delete or move to `08_Archive` |
| `10_Skills_Library\05_Operations\scripts\test_suite.py` | Obsolete test script | Delete or move to `08_Archive` |
| `.obsidian/plugins/Templater/` | **Broken install** (no manifest.json, no main.js) | Remove directory; the active Templater is in `templater-obsidian/` |
| `06_Website/` node_modules (31 directories) | Next.js dependencies | Already partially in `.gitignore`; consider adding `**/node_modules/` to root `.gitignore` if not present |

**Note:** The 12 "unknown" scripts outside `10_Skills_Library\05_Operations\scripts\` are Docker service entrypoints (`alert_router.py`, `dashboard_app.py`, `inventory_api.py`, etc.) and AI media pipeline utilities — these are **in use** and should not be removed.

---

## 3. Task Scheduler Verification

### 3.1 Torus Jobs (18 total)

| Task Name | Schedule | Script | Last Result | Notes |
|-----------|----------|--------|-------------|-------|
| Torus_Asset_Validator | Daily 09:00 | asset_validator.py | 0 | OK |
| Torus_Daily_Obsidian_Note | Daily 08:00 | obsidian_daily_note.py | 0 | OK |
| Torus_Daily_Ops_Check | Daily 08:00 | daily_ops_automation.py | 0 | OK |
| Torus_Inventory_Alert | Daily 07:00 | inventory_alert.py | 0 | OK |
| Torus_Inventory_Sync | Hourly | inventory_sync.py | 0 | OK |
| Torus_Marketing_Campaign_Check | Weekly | Torus_Campaign_Scheduler.py | 0 | OK |
| Torus_Monthly_Inventory_Count | Monthly | inventory_tracker.py | 0 | OK |
| Torus_Monthly_Obsidian_Note | Monthly | obsidian_monthly_note.py | 0 | OK |
| Torus_Monthly_Ops_Review | Monthly | monthly_review_automation.py | 0 | OK |
| Torus_Order_Manager | Every 5 min | order_manager.py | 0 | OK |
| Torus_Product_Photo_Tracker | Weekly | Torus_Photo_Tracker.py | 0 | OK |
| Torus_Social_Media_Calendar | Weekly | social_media_automation.py | 0 | OK |
| Torus_Social_Media_Check | Daily 09:00 | social_media_automation.py | 0 | OK |
| Torus_Trello_Sync | Daily 08:30 | trello_sync.py | 0 | OK |
| Torus_Vault_Cleanup | Weekly | vault_cleanup.py | 0 | OK |
| Torus_Vault_Sync_To_GitHub | Daily 08:30 | vault_sync_to_github.py | 0 | OK |
| Torus_Weekly_Obsidian_Note | Weekly | obsidian_weekly_note.py | 0 | OK |
| Torus_Weekly_Ops_Review | Weekly | weekly_review_automation.py | 0 | OK |

**Status:** ✅ All 18 Torus tasks have corresponding scripts and all scripts exist on disk. All returned Last Result 0 on last run.

### 3.2 Non-Torus Jobs of Note
- `PINKCADY_SQUIDSTATION_Backup`: Last Result **16** (partial success) — review backup log
- `Torus_Order_Manager`: Schedule type shows "On demand only, Minute" but listed as every 5 min — verify trigger is correct

---

## 4. Missing Dependencies & Broken Paths

### 4.1 Internal Vault Paths
- **Trello board wikilinks:** 36 broken links in `09_Projects/Trello_Boards/*.md` — `[[Card_*]]` links omit the list subfolder (e.g., should be `[[Backlog/Card_*]]`). The target files do exist in `Backlog/`, `Done/`, `In_Progress/`, etc.
- **Docker container paths:** `/health`, `/inventory`, `/vault`, `/backups`, `/alert` in Docker scripts are **expected** (run inside containers, not host).
- **Dataview sources:** `inventory_master.json` exists; all `FROM "03_Financials"`, `FROM "09_Projects"`, etc. resolve to real folders.

### 4.2 Python Scripts
- `ops_officer.py` references `/query` — container or API path, acceptable.
- No missing Python imports detected in audit.

---

## 5. Dataview Query Verification

| Dashboard File | Queries | Source Status |
|----------------|---------|---------------|
| `00_Inbox\Dataview_Financials_Dashboard.md` | FROM `03_Financials` | ✅ |
| `00_Inbox\Dataview_Projects_Dashboard.md` | FROM `09_Projects` | ✅ |
| `00_Inbox\04_Projects\Dataview_Projects_Dashboard.md` | FROM `09_Projects` | ✅ |
| `03_Financials\Dataview_Financials_Dashboard.md` | FROM `03_Financials`, `inventory_master.json` | ✅ |
| `04_Products\Dataview_Products_Dashboard.md` | FROM `04_Products` | ✅ |
| `08_Design_Brand\Dataview_Dashboard_Template.md` | FROM `04_Products`, `03_Financials`, `09_Projects`, `10_Skills_Library`, `08_Design_Brand` | ✅ |
| `08_Reports\Dataview_Brand_Dashboard.md` | FROM `04_Products/inventory_master.json`, `03_Financials`, `09_Projects`, `10_Skills_Library` | ✅ |

**Status:** ✅ All Dataview queries reference real files/folders.

---

## 6. Hardcoded Secrets & Credentials

### 6.1 Approved Credential Files
These contain real secrets and are **not** in `.gitignore`:

| File | Service | Secret Type | In .gitignore? |
|------|---------|-------------|----------------|
| `10_Skills_Library\05_Operations\buffer_credentials.json` | Buffer | API key | ❌ **NO** |
| `10_Skills_Library\05_Operations\hubspot_credentials.json` | HubSpot | Token | ❌ **NO** |
| `10_Skills_Library\05_Operations\zapier_credentials.json` | Zapier | Webhook URL | ❌ **NO** |
| `01_Operating\Operating Paperwork\Trello_API_Credentials.md` | Trello | API key + token | ❌ **NO** |
| `06_Website\dashboard\.env.local` | Dashboard | `localhost:3001` only | N/A (non-sensitive) |

### 6.2 Hardcoded Secrets in Scripts (NOT Approved)
**CRITICAL:** Real Trello API key and token are hardcoded in plaintext in 3 Python scripts:

| File | Lines | Value |
|------|-------|-------|
| `10_Skills_Library\05_Operations\scripts\trello_sync.py` | 11-12 | `API_KEY = "d6ee11ff..."`, `TOKEN = "ATTA5fa83..."` |
| `10_Skills_Library\05_Operations\scripts\trello_audit.py` | 5-6 | `API_KEY = "d6ee11ff..."`, `TOKEN = "ATTA5fa83..."` |
| `10_Skills_Library\05_Operations\AI_Media_Pipeline\scripts\generate_asset_request.py` | 11-12 | `API_KEY = "d6ee11ff..."`, `TOKEN = "ATTA5fa83..."` |

The approved credential file `01_Operating\Operating Paperwork\Trello_API_Credentials.md` already contains these exact values. The scripts should **read from the credential file** instead of embedding secrets.

### 6.3 Suspicious File
- `08_Design_Brand\.env.example.bin` — 456-byte binary file with `.bin` extension. Likely a real `.env` file misnamed. **Recommendation:** Rename to `.env.example` and verify contents; if it contains real secrets, move to approved credentials location and add to `.gitignore`.

### 6.4 .gitignore Status
**`.gitignore` does NOT mention any credential files.** This means `buffer_credentials.json`, `hubspot_credentials.json`, `zapier_credentials.json`, and `Trello_API_Credentials.md` are at risk of being committed to the GitHub backup repo.

**Recommendations (Priority: High):**
1. Add the following to `.gitignore`:
   ```
   # Credentials
   *credentials*.json
   *credentials*.md
   .env.local
   .env
   ```
2. **Immediately rotate** the Trello API key and token (they are exposed in 3 scripts).
3. Patch `trello_sync.py`, `trello_audit.py`, and `generate_asset_request.py` to read from `01_Operating\Operating Paperwork\Trello_API_Credentials.md` or `10_Skills_Library\05_Operations\zapier_credentials.json`.
4. Inspect `08_Design_Brand\.env.example.bin` and either add to `.gitignore` or move to approved credentials folder.

---

## 7. Additional Findings

### 7.1 Plugin Configuration
- **Templater:** Two plugin directories exist: `Templater/` (broken, empty) and `templater-obsidian/` (working). Remove `Templater/` to avoid confusion.
- **Core config missing:** `.obsidian/config` and `.obsidian/hotkeys.json` are absent. Vault appearance and shortcuts rely on defaults or other config files.

### 7.2 Vault Structure
- `11_Torus_Ops` duplicate vault has already been removed (noted in prior audit).
- Top-level folders use mixed numbering: `06_Growth_Marketing` and `06_Website` share prefix `06_`; `08_Archive`, `08_Design_Brand`, `08_Reports` share prefix `08_`. This is documented in the vault but creates ambiguity in automation paths.

### 7.3 Website Artifacts
- The `06_Website` folder contains 4 parallel website versions: `Website/`, `next-storefront/`, `Design/Website/`, `dashboard/`. This aligns with the known `Website/website` case-collision history.
- Build outputs (`.next/`, `out/`, `.cache/`) are present inside the vault and inflate file count.

---

## 8. Recommendations (Priority Order)

| Priority | Action | Owner |
|----------|--------|-------|
| **P0** | Add credential files to `.gitignore`; rotate Trello API key+token | Torus |
| **P0** | Remove hardcoded secrets from `trello_sync.py`, `trello_audit.py`, `generate_asset_request.py` | Torus |
| **P1** | Delete `35` duplicate image pairs in `08_Design_Brand` | Torus |
| **P1** | Fix 36 broken Trello wikilinks to include list subfolder (e.g., `[[Backlog/Card_*]]`) | Torus |
| **P1** | Remove broken `.obsidian/plugins/Templater/` directory | Torus |
| **P1** | Inspect and secure `08_Design_Brand/.env.example.bin` | Torus |
| **P2** | Delete obsolete `test_integrations.py` and `test_suite.py` | Torus |
| **P2** | Add `**/node_modules/` to `.gitignore` if missing | Torus |
| **P3** | Restore missing `.obsidian/config` and `hotkeys.json` if custom shortcuts were lost | Torus |
| **P3** | Consider moving website build artifacts (`06_Website/.next/`, `out/`) outside vault | Torus |

---

## Appendix A: Trello Board Status

The vault contains 50 `Card_*.md` files across 3 boards:
- **Business_Docs:** 13 cards (Backlog, Done, In_Progress, Review, Templates)
- **Torus_Ops:** 22 cards (Backlog, Done, In_Progress, Review, To_Do)
- **Website_Rebuild:** 11 cards (Backlog, Done, In_Progress, Review, To_Do)

All wikilinks in list files (`Backlog.md`, `Done.md`, etc.) are missing the list subfolder prefix.

---

## Appendix B: Top-Level Folder Inventory

| Folder | Purpose |
|--------|---------|
| 00_Inbox | Incoming notes, dashboards |
| 01_Operating | Operating agreements, credentials |
| 02_Tax | Tax records |
| 03_Financials | Financial statements, budgets |
| 04_Products | Product SKUs, photos, inventory |
| 05_Legal | Legal docs |
| 06_Growth_Marketing | Marketing plans, images |
| 06_Website | Website source + build artifacts |
| 07_Photos | Photo library |
| 07_Templates | Note templates |
| 08_Archive | Archived items |
| 08_Design_Brand | Brand assets, social templates |
| 08_Reports | Audit reports |
| 09_Projects | Trello boards, project docs |
| 10_Skills_Library | Scripts, Docker, automation |
| 11_Vendors | Vendor profiles |
| 12_Customers | Customer data |
| 13_Team | Team profiles |
| 14_Infrastructure | Domains, hosting, keys |
| 99_Inbox | Overflow inbox |

---

*Report generated by Hermes Agent — automated vault audit.*
