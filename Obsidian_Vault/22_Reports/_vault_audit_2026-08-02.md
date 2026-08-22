# Torus Coffee Company — Vault Structural Audit
**Date:** 2026-08-02  
**Vault Path:** `D:\Work\Torus Coffee Company LLC`  
**Auditor:** Hermes Agent (automated)

---

## 1. Top-Level Folder Structure

### Observed top-level folders
| # | Folder | Status |
|---|--------|--------|
| — | `.obsidian` | Expected |
| 00 | `00_Inbox` | ✅ Present |
| 01 | `01_Operating` | ✅ Present |
| 02 | `02_Tax` | ✅ Present |
| 03 | `03_Financials` | ✅ Present |
| 04 | `04_Products` | ✅ Present |
| 05 | `05_Research` | ✅ Present |
| 06 | `06_Growth_Marketing` | ⚠️ Duplicate prefix (see §2) |
| 06 | `06_Website` | ⚠️ Duplicate prefix (see §2) |
| 07 | `07_Photos` | ✅ Present |
| 08 | `08_Archive` | ⚠️ Duplicate prefix (see §2) |
| 08 | `08_Design_Brand` | ⚠️ Duplicate prefix (see §2) |
| 08 | `08_Reports` | ⚠️ Duplicate prefix (see §2) |
| 09 | `09_Projects` | ✅ Present |
| 10 | `10_Skills_Library` | ✅ Present |
| 11 | `11_Torus_Ops` | ⚠️ Anomalous (old vault clone; see §2) |
| 99 | `99_Inbox` | ❌ Orphan (outside 00–11) |
| — | `Product Production` | ❌ Orphan (no number prefix) |

**Summary:** 17 numbered folders + 2 orphan folders + `.obsidian`. Numbering convention is **not** strictly followed.

---

## 2. Duplicate / Orphan Folders

### Duplicate numeric prefixes
- **`06`** → `06_Growth_Marketing` and `06_Website`  
  *Impact:* Two folders claim the same index. This breaks any automation that expects a single `06_*` folder.

- **`08`** → `08_Archive`, `08_Design_Brand`, `08_Reports`  
  *Impact:* Three folders share `08`. Any tooling that maps prefix → folder will behave unpredictably.

### Orphan folders
- **`99_Inbox`** — Number `99` falls outside the allowed `00–11` range.  
  *Contents:* `Personal_Tax/` (contains `Bryon_Smith_1099-SA_2026.pdf`, `Federal_W-2_2026.pdf`, `Federal_W-2_2026_duplicate.pdf`) and `Unidentified_Personal/`.  
  *Note:* Personal tax documents (W-2, 1099-SA) should **not** be in this business vault.

- **`Product Production`** — No numeric prefix. Contains only `desktop.ini` (Windows shell metadata). Effectively an empty/shell folder.

### Suspicious duplicate vault
- **`11_Torus_Ops/`** contains its own `.git` directory and a full set of legacy folders (`00_Inbox`, `01_Operating`, `02_Tax`, etc.). This is an **old vault clone** that should be removed or moved outside the vault. It also contains copies of the VOID Pirate references (see §6).

---

## 3. `.obsidian` Folder Structure

**Config files:** `app.json`, `appearance.json`, `community-plugins.json`, `core-plugins.json`, `graph.json`, `obsidian.json`, `workspace.json` — present and clean.

**Installed plugins (5):**
| Plugin | Status | Notes |
|--------|--------|-------|
| `calendar` | ✅ | Contains `node_modules` (~132 MB) |
| `dataview` | ✅ | Contains `node_modules` (~131 MB) |
| `quickadd` | ✅ | Contains `node_modules` (~319 MB) |
| `templater-obsidian` | ✅ | Contains `node_modules` (~323 MB) |
| `periodic-notes` | ✅ | Main code present (`main.js`) |

**Issue:** The plugin directories include full `node_modules` trees and source files. Obsidian does **not** need source/`node_modules` inside `.obsidian/plugins/` for normal operation — only the compiled plugin main JS and `manifest.json` are required. This inflates vault size by ~900 MB.

---

## 4. Automation Folders

### Expected convention
The automation system expects standalone folders:
`00_Inbox/`, `01_Daily/`, `02_Weekly/`, `03_Monthly/`, `04_Quarterly/`, `05_Annual/`, `06_Project/`, `07_Templates/`

### Actual state
| Expected folder | Exists at root? | Actual location / notes |
|-----------------|----------------|------------------------|
| `00_Inbox` | ✅ Yes | Exists at root with subfolders |
| `01_Daily` | ❌ No | Nested inside `00_Inbox/01_Daily/` |
| `02_Weekly` | ❌ No | Nested inside `00_Inbox/02_Weekly/` |
| `03_Monthly` | ❌ No | Nested inside `00_Inbox/03_Monthly/` |
| `04_Quarterly` | ❌ No | Missing entirely |
| `05_Annual` | ❌ No | Missing entirely |
| `06_Project` | ❌ No | Nested inside `00_Inbox/04_Projects/` (note naming mismatch) |
| `07_Templates` | ❌ No | Nested inside `00_Inbox/07_Templates/` |

**Current `00_Inbox` structure:**
```
00_Inbox/
├── 01_Daily/
│   ├── 2026-08-01.md
│   └── 2026-08-02.md
├── 02_Weekly/
│   └── Week of 2026-07-27.md
├── 03_Monthly/
│   └── 2026-08.md
├── 04_Projects/
│   └── Dataview_Projects_Dashboard.md
├── 05_Meetings/          ← empty
├── 06_Research/          ← empty
└── 07_Templates/
    ├── Daily_Ops_Log.md
    ├── Inventory_Log.md
    ├── Meeting_Notes.md
    ├── Monthly_Review.md
    ├── Project_Note.md
    ├── Research_Note.md
    ├── Sales_Order.md
    └── Weekly_Review.md
```

**Findings:**
- `04_Quarterly` and `05_Annual` are **missing** entirely.
- `06_Project` is named `04_Projects` inside `00_Inbox` (prefix mismatch).
- `05_Meetings` and `06_Research` are empty directories inside `00_Inbox`.
- The automation folders are **nested** inside `00_Inbox` rather than being siblings at the root, which will break periodic-notes / Task Scheduler expectations.

---

## 5. Problematic / Out-of-Place Files

### Large binaries (>10 MB)
| Size | File | Recommendation |
|------|------|----------------|
| 520.5 MB | `08_Archive/Torus_Coffee_Company_20260528.zip` | Move to cloud / external backup |
| 147.2 MB | `06_Website/next-storefront/node_modules/.../next-swc.win32-x64-msvc.node` | Should not be in vault; move website project out |
| 28.7 MB | `.obsidian/plugins/QuickAdd/.../tsgolint.exe` | Remove from vault (plugin binary) |
| 28.1 MB | `06_Growth_Marketing/ANMR0013.mp4` | Consider external media hosting |
| 28.1 MB | `.obsidian/plugins/QuickAdd/.../vite-plus.win32-x64-msvc.node` | Remove from vault (plugin binary) |
| 23.4 MB | `.obsidian/plugins/Templater/.../tsc.exe` | Remove from vault (plugin binary) |
| 21.2 MB | `06_Website/next-storefront/.next/cache/.../0.pack` | Should not be in vault |
| 20.1 MB | `.obsidian/plugins/QuickAdd/.../longLatDemo.gif` | Remove or externalize |
| 19.8 MB | `06_Website/.../rolldown-binding.win32-x64-msvc.node` | Remove from vault |
| 19.6 MB | `.obsidian/plugins/QuickAdd/.../rolldown-binding.win32-x64-msvc.node` | Remove from vault |
| 18.2 MB | `06_Website/.../libvips-42.dll` | Remove from vault |
| 12.5 MB | `.obsidian/plugins/QuickAdd/.../oxlint.win32-x64-msvc.node` | Remove from vault |
| 11.1 MB | `.obsidian/plugins/Templater/.../tsserver.js` | Remove from vault |
| 11.1 MB | `.obsidian/plugins/QuickAdd/.../esbuild.exe` | Remove from vault |
| 11.1 MB | `.obsidian/plugins/Templater/.../esbuild.exe` | Remove from vault |
| 11.1 MB | `.obsidian/plugins/Templater/.../tsserverlibrary.js` | Remove from vault |
| 10.5 MB | `06_Growth_Marketing/The Orbit Report 12-2-25 v6.jpg` | Consider external hosting |
| 10.4 MB | `.obsidian/plugins/Templater/.../typescriptServices.js` | Remove from vault |
| 10.4 MB | `.obsidian/plugins/Templater/.../typescript.js` | Remove from vault |
| 10.4 MB | `06_Growth_Marketing/Stain Glass Leaf Art 2025 v3.jpg` | Consider external hosting |
| 10.0 MB | `06_Growth_Marketing/The Orbit Report 12-2-25 v7.jpg` | Consider external hosting |
| 10.0 MB | `.obsidian/plugins/QuickAdd/.../rolldown-binding.wasm32-wasi.wasm` | Remove from vault |

### Personal / private documents
- `99_Inbox/Personal_Tax/Bryon_Smith_1099-SA_2026.pdf`
- `99_Inbox/Personal_Tax/Federal_W-2_2026.pdf`
- `99_Inbox/Personal_Tax/Federal_W-2_2026_duplicate.pdf`
- `99_Inbox/Unidentified_Personal/WHOUT291636.pdf`

### Temporary / cache files (19 files)
Examples found inside `.obsidian/plugins/*/node_modules/` and `06_Website/next-storefront/`:
- `.DS_Store` files
- `npm-debug.log.*`
- `index_vite_proxy.tmp.mjs`
- `*.temporal.d.ts` / `*.temporal.js` (TypeScript build artifacts)
- `lint.log`

**Note:** Most “secret” filename hits (`api_key`, `credentials`, `token`) are **false positives** from `node_modules` and Python `site-packages` (e.g., `google/auth/credentials.py`, `cacert.pem`). No actual API keys or environment files were found.

---

## 6. VOID Pirate Trading Co Content

**CRITICAL:** VOID Pirate Trading Co references were found in **6 unique files**:

| File | Context |
|------|---------|
| `00_Vault_Home.md` | `VOID Pirate Trading Co.: ⏸️ pending Tailscale connection` |
| `01_Operating/Entity_Summary.md` | `Separate entity from VOID Pirate Trading Co` |
| `01_Operating/Operating Paperwork/Z_Reference/Torus_Coffee_Entity_Summary.md` | Same references |
| `11_Torus_Ops/00_Vault_Home.md` | Duplicate (old vault clone) |
| `11_Torus_Ops/01_Operating/Entity_Summary.md` | Duplicate (old vault clone) |
| `11_Torus_Ops/01_Operating/Operating Paperwork/Z_Reference/Torus_Coffee_Entity_Summary.md` | Duplicate (old vault clone) |

The presence of these references in the **main vault** (not just the clone) means cleanup is required. The references in `11_Torus_Ops` will be resolved once the clone is deleted.

---

## 7. Overall Vault Statistics

| Metric | Value |
|--------|-------|
| Total files | 94,856 |
| Total size | ~3.77 GB |
| Top-level folders (excluding `.obsidian`) | 17 |
| Orphan / mis-numbered folders | 2 (`99_Inbox`, `Product Production`) |
| Duplicate-prefix folders | 2 prefixes (`06`, `08`) |
| Stale vault clone | 1 (`11_Torus_Ops` with embedded `.git`) |
| Large files (>10 MB) | 22 |
| Temp / cache files | 19 |
| Personal tax PDFs in vault | 3 + 1 duplicate |
| VOID Pirate Trading Co references | 6 (3 in main vault, 3 in clone) |

---

## 8. Recommendations (Priority Order)

1. **Delete `11_Torus_Ops/`** — it is a stale vault clone with its own `.git`. Remove it to reclaim ~1.1 GB and eliminate duplicate VOID Pirate references.
2. **Clean up `99_Inbox`** — move or delete the personal tax PDFs (`W-2`, `1099-SA`). They do not belong in a business vault.
3. **Resolve duplicate prefixes** — rename `06_Website` and one of the `08_*` folders, or integrate them into a unified numbering scheme.
4. **Restructure automation folders** — make `01_Daily` through `07_Templates` standalone siblings of `00_Inbox` (or update the Task Scheduler to match the current nested layout).
5. **Move or externalize large binaries:**
   - `08_Archive/*.zip` → external backup / cloud storage
   - `06_Website/` project (with `node_modules`, `.next`) → move outside vault
   - `06_Growth_Marketing/` large media → external CDN or external folder
6. **Prune `.obsidian/plugins/*`** — remove `node_modules`, `src/`, and build artifacts from all plugin folders. This alone can free ~900 MB.
7. **Remove temp files** — `.DS_Store`, `npm-debug.log*`, `*.tmp.mjs`, etc.
8. **Review VOID Pirate references** in `00_Vault_Home.md`, `01_Operating/Entity_Summary.md`, and `01_Operating/Operating Paperwork/Z_Reference/Torus_Coffee_Entity_Summary.md` and either delete or replace with current entity info.

---

*Report generated by automated structural audit on 2026-08-02.*
