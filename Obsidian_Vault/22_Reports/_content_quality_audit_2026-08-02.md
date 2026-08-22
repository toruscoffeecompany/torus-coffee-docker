# Content Quality Audit — 2026-08-02

**Vault:** `D:\Work\Torus Coffee Company LLC`  
**Audited:** 2026-08-02  
**Auditor:** Automated scan + manual spot-check  
**Scope:** All `.md` files in vault (excluded `.obsidian`, `.git`, `node_modules`, `venv`)  

---

## Executive Summary

| Metric | Count |
|---|---|
| Total markdown files scanned | 124 |
| Files with any issue | 98 |
| Files clean | 26 |
| Missing YAML frontmatter | 80 |
| Incomplete YAML frontmatter | 18 |
| Templater syntax issues | 0 |
| Dataview syntax issues | 0 |
| Broken wiki-links / markdown links | 0 |

**Overall health:** Moderate. Core dashboards and templates use correct plugin syntax, but frontmatter coverage is very low outside a small subset of files. The largest single contributor to “missing frontmatter” is the `11_Torus_Ops` directory, which appears to be a duplicate/staging copy of the vault.

---

## 1. Frontmatter Completeness

### 1.1 Business documents missing frontmatter entirely

These files have **no YAML frontmatter** at all.

| File | Notes |
|---|---|
| `00_Inbox\07_Templates\Daily_Ops_Log.md` | Template missing frontmatter |
| `00_Inbox\07_Templates\Monthly_Review.md` | Template missing frontmatter |
| `00_Inbox\07_Templates\Weekly_Review.md` | Template missing frontmatter |
| `01_Operating\Entity_Summary.md` | Core operating doc |
| `01_Operating\Operating Paperwork\Google Workspace Access.md` | |
| `01_Operating\Operating Paperwork\Google Workspace OAuth Setup.md` | |
| `01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Expense_Tracker_Template.md` | |
| `01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Filing_Template.md` | |
| `01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_Entity_Summary.md` | |
| `01_Operating\Privacy Policy.md` | Legal doc |
| `01_Operating\Refund and Returns Policy.md` | Legal doc |
| `01_Operating\Sara's Business Plan (Torus Coffee Company).md` | Key strategic doc |
| `01_Operating\Shipping Policy.md` | Legal doc |
| `01_Operating\Terms and Conditions.md` | Legal doc |
| `01_Operating\torus_color_codes.md` | Reference |
| `06_Growth_Marketing\orbit_report_3_15_26.md` | Marketing report |
| `06_Website\Website\Website Design Brief v1.md` | |
| `06_Website\next-storefront\DEPLOY.md` | Website code/doc |
| `06_Website\next-storefront\GITHUB_PUSH.md` | Website code/doc |
| `06_Website\next-storefront\README.md` | Website code/doc |
| `06_Website\next-storefront\out\README.md` | Website code/doc |
| `06_Website\next-storefront\public\README.md` | Website code/doc |
| `08_Design_Brand\01_Torus_Blog_Strategy_Guide.md` | |
| `08_Design_Brand\02_Blog_Post_Template.md` | |
| `08_Design_Brand\03_Content_Calendar_Template.md` | |
| `08_Design_Brand\DEPLOYMENT_GUIDE.md` | |
| `08_Design_Brand\GROWTH_STRATEGY.md` | |
| `08_Design_Brand\README.md` | |
| `09_Projects\2026_2027_Action_Plan.md` | |
| `09_Projects\CODEOWNERS_CI_Hints.md` | |
| `09_Projects\GitHub_Projects.md` | |
| `09_Projects\GitHub_Workflow.md` | |
| `09_Projects\Issue_Templates.md` | |
| `09_Projects\Project_Management_Board.md` | |
| `10_Skills_Library\06_Growth_Marketing\_INDEX.md` | Reference index |
| `10_Skills_Library\08_Design_Brand\_INDEX.md` | Reference index |
| `11_Torus_Ops\00_Vault_Home.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Entity_Summary.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Operating Paperwork\Google Workspace Access.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Operating Paperwork\Google Workspace OAuth Setup.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Expense_Tracker_Template.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Filing_Template.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_Entity_Summary.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Privacy Policy.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Refund and Returns Policy.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Sara's Business Plan (Torus Coffee Company).md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Shipping Policy.md` | Mirror copy |
| `11_Torus_Ops\01_Operating\Terms and Conditions.md` | Mirror copy |
| `11_Torus_Ops\06_Website\Website\Website Design Brief v1.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\01_Torus_Blog_Strategy_Guide.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\02_Blog_Post_Template.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\03_Content_Calendar_Template.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\DEPLOYMENT_GUIDE.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\GROWTH_STRATEGY.md` | Mirror copy |
| `11_Torus_Ops\08_Design_Brand\README.md` | Mirror copy |
| `11_Torus_Ops\08_Reports\2026-2027_Update_Audit.md` | Mirror/report copy |
| `11_Torus_Ops\08_Reports\_vault_gap_analysis.md` | Mirror/report copy |
| `11_Torus_Ops\09_Projects\2026_2027_Action_Plan.md` | Mirror copy |
| `11_Torus_Ops\09_Projects\CODEOWNERS_CI_Hints.md` | Mirror copy |
| `11_Torus_Ops\09_Projects\GitHub_Projects.md` | Mirror copy |
| `11_Torus_Ops\09_Projects\GitHub_Workflow.md` | Mirror copy |
| `11_Torus_Ops\09_Projects\Issue_Templates.md` | Mirror copy |
| `11_Torus_Ops\09_Projects\Project_Management_Board.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\00_Index.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\01_Website_Building\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\01_Website_Building\Free_Website_Tools_Reference.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\02_Legal_Compliance\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\03_Finance_Tax\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\03_Finance_Tax\Free_Finance_Tax_Tools_Reference.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\04_Product_Development\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\05_Operations\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\05_Operations\Automation_Runbook.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\05_Operations\Free_Inventory_Ops_Tools_Reference.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\05_Operations\Obsidian_Automation_Guide.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\06_Growth_Marketing\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\07_Ecommerce\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\07_Ecommerce\Free_Ecommerce_Tools_Reference.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\08_Design_Brand\_INDEX.md` | Mirror copy |
| `11_Torus_Ops\10_Skills_Library\09_GitHub_Workflow.md` | Mirror copy |
| `11_Torus_Ops\README.md` | Mirror copy |

> **Action:** Add YAML frontmatter with `title`, `date`, and `tags` to every business document. The `11_Torus_Ops` folder should either be removed from the active vault or maintained in sync.

---

### 1.2 Business documents with incomplete frontmatter

These files **have frontmatter** but are missing one or more required fields.

| File | Missing Fields |
|---|---|
| `00_Inbox\07_Templates\Inventory_Log.md` | title, date |
| `00_Inbox\07_Templates\Meeting_Notes.md` | title, date |
| `00_Inbox\07_Templates\Project_Note.md` | title, date |
| `00_Inbox\07_Templates\Research_Note.md` | title, date |
| `00_Inbox\07_Templates\Sales_Order.md` | title, date |
| `03_Financials\Expense_Report_2026-07-01.md` | title |
| `03_Financials\Expense_Report_2026-07-15.md` | title |
| `03_Financials\Expense_Report_2026-07-28.md` | title |
| `03_Financials\Financial_Statement_2025_FY.md` | title |
| `03_Financials\Financial_Statement_2026-07.md` | title |
| `04_Products\Aurora_Bites.md` | title, date |
| `04_Products\Cosmic_Bananas.md` | title, date |
| `04_Products\Gummy_Critters.md` | title, date |
| `04_Products\Rainbow_Crunch.md` | title, date |
| `04_Products\Rancher_Rocks.md` | title, date |
| `09_Projects\Business_Docs_Refresh_2026_2027.md` | title, date |
| `09_Projects\Freeze_Dried_Candy_Line_Expansion.md` | title, date |
| `09_Projects\Website_Launch.md` | title, date |

> **Action:** Patch frontmatter in the above files. Product and project notes should especially have `title` and `date`. Expense reports need a human-readable `title` in addition to the filename date.

---

## 2. Templater Syntax Check

Templates audited: 18 files  
Templater calls detected: 8 templates use Templater  
Templater syntax errors: **0**

### 2.1 Templates using Templater correctly

| File | Templater Calls |
|---|---|
| `00_Inbox\07_Templates\Daily_Ops_Log.md` | `tp.date.now` |
| `00_Inbox\07_Templates\Inventory_Log.md` | `tp.file.title`, `tp.user.prompt`, `tp.date.now` |
| `00_Inbox\07_Templates\Meeting_Notes.md` | `tp.file.title`, `tp.date.now` |
| `00_Inbox\07_Templates\Monthly_Review.md` | `tp.date.now` |
| `00_Inbox\07_Templates\Project_Note.md` | `tp.file.title`, `tp.user.prompt`, `tp.date.now` |
| `00_Inbox\07_Templates\Research_Note.md` | `tp.file.title`, `tp.user.prompt`, `tp.date.now` |
| `00_Inbox\07_Templates\Sales_Order.md` | `tp.file.title`, `tp.user.prompt`, `tp.date.now` |
| `00_Inbox\07_Templates\Weekly_Review.md` | `tp.date.now` |

All templates use recognized Templater functions (`tp.date.now`, `tp.file.title`, `tp.user.prompt`). No syntax issues found.

### 2.2 Templates without Templater

These are template files that do **not** currently use Templater functions. This is acceptable if they are meant to be static, but worth reviewing:

- `01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Expense_Tracker_Template.md`
- `01_Operating\Operating Paperwork\Z_Reference\Torus_Coffee_2026_Filing_Template.md`
- `08_Design_Brand\02_Blog_Post_Template.md`
- `08_Design_Brand\03_Content_Calendar_Template.md`
- `09_Projects\Issue_Templates.md`

---

## 3. Dataview Query Check

Dataview dashboards audited: 5 files  
Dataview syntax errors: **0**

### 3.1 Dashboards using Dataview

| File | Notes |
|---|---|
| `00_Inbox\04_Projects\Dataview_Projects_Dashboard.md` | Contains `TABLE`/`LIST` queries with proper `FROM` clauses |
| `03_Financials\Dataview_Financials_Dashboard.md` | 5 dataview blocks, all properly closed |
| `04_Products\Dataview_Products_Dashboard.md` | Contains product `TABLE` queries |
| `11_Torus_Ops\03_Financials\Dataview_Financials_Dashboard.md` | Mirror copy |
| `11_Torus_Ops\04_Products\Dataview_Products_Dashboard.md` | Mirror copy |

All `TABLE` and `LIST` queries include `FROM` clauses, and all ````` ```dataview ```` code blocks are properly closed.

---

## 4. Link & Reference Check

- **Broken wiki-style links (`[[...]]`):** 0
- **Broken markdown links (`[text](path)`):** 0

All internal file references resolve correctly.

---

## 5. Additional Observations

1. **`11_Torus_Ops` duplicate vault:** This directory contains a near-complete mirror of the main vault. It inflates the issue count and creates maintenance burden. Decide whether this is a backup, a staging area, or should be removed from the active Obsidian vault.
2. **`06_Website\next-storefront`:** Contains Next.js source docs (`DEPLOY.md`, `GITHUB_PUSH.md`, `README.md`, `out/README.md`, `public/README.md`). These are likely not Obsidian business notes and may be noise in the vault.
3. **`10_Skills_Library`:** Reference index files without frontmatter. If these are meant to be Obsidian notes, add frontmatter. If they are raw reference documents, consider moving them out of the vault or treating them as exempt.
4. **Frontmatter keys in use:** Existing frontmatter uses `title`, `date`, and `tags`. No unusual or deprecated keys were found.

---

## 6. Recommended Fixes (Priority Order)

### High priority
1. **Add frontmatter to core legal/operating docs:**
   - `01_Operating\Privacy Policy.md`
   - `01_Operating\Terms and Conditions.md`
   - `01_Operating\Refund and Returns Policy.md`
   - `01_Operating\Shipping Policy.md`
   - `01_Operating\Sara's Business Plan (Torus Coffee Company).md`
2. **Add `title` to financial reports:**
   - `03_Financials\Expense_Report_2026-07-01.md` (etc.)
   - `03_Financials\Financial_Statement_2025_FY.md`
   - `03_Financials\Financial_Statement_2026-07.md`
3. **Add `title` and `date` to product notes:**
   - `04_Products\Aurora_Bites.md` (and all 4 siblings)
4. **Add `title` and `date` to project notes:**
   - `09_Projects\Business_Docs_Refresh_2026_2027.md`
   - `09_Projects\Freeze_Dried_Candy_Line_Expansion.md`
   - `09_Projects\Website_Launch.md`

### Medium priority
5. **Add frontmatter to all templates in `00_Inbox\07_Templates\`:**
   - `Daily_Ops_Log.md`, `Monthly_Review.md`, `Weekly_Review.md`
   - Complete missing fields in `Inventory_Log.md`, `Meeting_Notes.md`, `Project_Note.md`, `Research_Note.md`, `Sales_Order.md`
6. **Add frontmatter to design/brand docs:**
   - `08_Design_Brand\01_Torus_Blog_Strategy_Guide.md`
   - `08_Design_Brand\DEPLOYMENT_GUIDE.md`
   - `08_Design_Brand\GROWTH_STRATEGY.md`
7. **Decide fate of `11_Torus_Ops`:** either sync frontmatter, move out, or exclude from vault.

### Low priority
8. Add frontmatter to reference indexes in `10_Skills_Library` if they should be vault notes.
9. Consider moving `06_Website\next-storefront` docs out of the Obsidian vault.

---

*End of audit.*
