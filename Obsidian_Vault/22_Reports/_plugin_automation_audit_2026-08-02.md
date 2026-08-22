# Plugin & Automation Audit
**Date:** 2026-08-02  
**Vault:** `D:\Work\Torus Coffee Company LLC`  
**Auditor:** Hermes Agent

---

## 1. Plugin File Integrity

| Plugin | Directory | main.js | manifest.json | Status |
|--------|-----------|---------|---------------|--------|
| Calendar | `obsidian-calendar` | ✓ (142 KB) | ✓ | OK |
| Dataview | `obsidian-dataview` | ✓ (2.3 MB) | ✓ | OK |
| Periodic Notes | `periodic-notes` | ✓ (180 KB) | ✓ | OK |
| QuickAdd | `QuickAdd` | ✓ (1.3 MB) | ✓ | OK |
| Templater | `Templater` | ✓ (451 KB) | ✓ | OK |

**Finding:** All five active plugins contain both `main.js` and `manifest.json`.

> ⚠️ **Leftover directory:** `.obsidian/plugins/obsidian-periodic-notes/` is empty. It appears to be a remnant of a previous install/update. It does not contain `main.js` or `manifest.json` and is not referenced by `community-plugins.json`.

---

## 2. Periodic Notes Configuration

**Config file:** `.obsidian/plugins/periodic-notes/data.json`

| Frequency | Folder | Format | Template |
|-----------|--------|--------|----------|
| Daily | `00_Inbox/01_Daily` | `YYYY-MM-DD` | `07_Templates/Daily_Ops_Log.md` |
| Weekly | `00_Inbox/02_Weekly` | `YYYY-[W]ww` | `07_Templates/Weekly_Review.md` |
| Monthly | `00_Inbox/03_Monthly` | `YYYY-MM` | `07_Templates/Monthly_Review.md` |

**Verification:**
- `00_Inbox/01_Daily/` — exists, contains `2026-08-01.md` and `2026-08-02.md`
- `00_Inbox/02_Weekly/` — exists, contains `Week of 2026-07-27.md`
- `00_Inbox/03_Monthly/` — exists, contains `2026-08.md`
- `00_Inbox/07_Templates/` — exists, contains `Daily_Ops_Log.md`, `Weekly_Review.md`, `Monthly_Review.md`

**Status:** ✓ Config matches actual folder structure and templates.

---

## 3. Templater Configuration

**Expected config location:** `.obsidian/plugins/templater-obsidian/data.json` (based on plugin ID `templater-obsidian`)  
**Actual config location:** Not found anywhere in `.obsidian/`

**Findings:**
- `Templater/manifest.json` declares `id: "templater-obsidian"`.
- No `templater-obsidian/data.json` exists.
- No `Templater/data.json` exists.
- `app.json` is empty (`{}`).
- `workspace.json` does not contain Templater settings.

**Status:** ⚠️ **MISCONFIGURED** — Templater has no persistent settings file. The template folder is **not explicitly configured**, which means Templater is running with defaults. The templates in `07_Templates/` use Templater syntax (`<% tp.date.now(...) %>`), so a missing template folder setting could cause note-creation workflows to fail or fall back to default behavior.

---

## 4. QuickAdd Macros

**Macros file:** `10_Skills_Library/05_Operations/scripts/quickadd_macros.json`

**Validation:** JSON parses successfully.

**Macros defined:**

| ID | Name | Type | Template / Capture Target | Folder |
|----|------|------|---------------------------|--------|
| `daily-ops-log-id` | Daily Ops Log | Template | `07_Templates/Daily_Ops_Log.md` | `00_Inbox/01_Daily` |
| `quick-inventory-entry-id` | Quick Inventory Entry | Capture | `00_Inbox/Inventory.md` | N/A |
| `weekly-review-id` | Weekly Review | Template | `07_Templates/Weekly_Review.md` | `00_Inbox/02_Weekly` |

**Cross-check:**
- `Daily_Ops_Log.md` exists in `00_Inbox/07_Templates/`
- `Weekly_Review.md` exists in `00_Inbox/07_Templates/`
- `Inventory.md` does not exist in `00_Inbox/` — QuickAdd will create it on first capture.

**Status:** ✓ Macros JSON is valid and importable. Template paths resolve correctly.

> **Note:** The QuickAdd plugin's own `data.json` has `"choices": []` and `"templateFolderPaths": []`. This means the macros defined in `quickadd_macros.json` have **not been imported into the plugin's active data store**. Either the file is a backup/export intended for manual import, or the macros need to be loaded via QuickAdd's import mechanism.

---

## 5. Task Scheduler Jobs

Three scheduled tasks were found under user `torus`:

| Task Name | Script | Schedule | Status |
|-----------|--------|----------|--------|
| Obsidian Daily Note | `obsidian_daily_note.py` | Daily at 08:00 | Enabled |
| Obsidian Monthly Note | `obsidian_monthly_note.py` | Monthly on the 1st at 08:00 | Enabled |
| Obsidian Weekly Note | `obsidian_weekly_note.py` | Weekly (Mon) at 08:00 | Enabled |

**Script paths:** `D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\`

**Status:** ✓ All three jobs point to correct scripts and are enabled.

> ⚠️ **Missing task:** `vault_sync_to_github.py` is **not** scheduled in Task Scheduler, despite being present in the scripts folder.

---

## 6. Scripts Functional Verification

All scripts in `10_Skills_Library/05_Operations/scripts/` were executed or inspected:

| Script | Result | Notes |
|--------|--------|-------|
| `obsidian_daily_note.py` | ✓ Runs | Correctly reports "already exists" when daily note is present |
| `obsidian_weekly_note.py` | ✓ Runs | Correctly reports "already exists" when weekly note is present |
| `obsidian_monthly_note.py` | ✓ Runs | Correctly reports "already exists" when monthly note is present |
| `obsidian_setup.py` | ✓ Inspected | Creates folders and templates; contains references to `Daily_Template.md`, `Weekly_Template.md`, `Monthly_Template.md` which do **not** match actual template filenames (`Daily_Ops_Log.md`, etc.) |
| `vault_sync_to_github.py` | ⚠️ Minor bug | `datetime` is imported inside `if __name__ == "__main__":` but used in `sync_repo()`. Works when run directly, fails if imported as a module. |

**Status:** Core note-generation scripts are functional.

---

## 7. Broken / Misconfigured Plugin Settings

| Issue | Severity | Detail |
|-------|----------|--------|
| Empty `obsidian-periodic-notes/` directory | Low | Leftover from prior install; no active files |
| Missing Templater `data.json` | **High** | Template folder is not configured; Templater will use defaults |
| QuickAdd macros not imported into plugin data | **Medium** | `QuickAdd/data.json` has empty `choices` array; macros exist only in external JSON file |
| `vault_sync_to_github.py` import scope | Low | Minor code-quality issue; does not affect scheduled runs |
| `obsidian_setup.py` template name mismatch | Low | Script creates `*_Template.md` but vault uses `*_Ops_Log.md` / `*_Review.md` |

---

## 8. Recommendations

1. **Templater:** Create `.obsidian/plugins/templater-obsidian/data.json` (or configure via Obsidian UI) with:
   - `"templates_folder": "00_Inbox/07_Templates"`
2. **QuickAdd:** Import `10_Skills_Library/05_Operations/scripts/quickadd_macros.json` into QuickAdd's macro manager so the macros appear in the plugin's active `data.json`.
3. **Leftover cleanup:** Delete the empty `.obsidian/plugins/obsidian-periodic-notes/` directory.
4. **Scripts:** Fix the `datetime` import in `vault_sync_to_github.py` by moving it to the top of the file.
5. **Sync task:** If `vault_sync_to_github.py` is meant to run automatically, add it to Task Scheduler.

---

## Summary

- **5/5 plugins** have required `main.js` and `manifest.json`.
- **Periodic Notes** config is correct and folders/templates exist.
- **Templater** template folder is **not configured** (missing `data.json`).
- **QuickAdd** macros JSON is valid but **not imported** into the plugin.
- **Task Scheduler** correctly runs 3 of 5 scripts; `vault_sync_to_github.py` is unscheduled.
- **Scripts** are functional; minor import bug in sync script.
- **No critical broken configs** beyond the missing Templater settings and empty plugin directory.
