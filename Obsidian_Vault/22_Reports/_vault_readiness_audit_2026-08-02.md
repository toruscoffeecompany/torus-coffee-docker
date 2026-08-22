# Torus Coffee Company Vault Readiness Audit

**Date:** 2026-08-02  
**Vault:** `D:\Work\Torus Coffee Company LLC`  
**Auditor:** Hermes Agent (read-only)  

---

## 1. Top-Level Folder Structure

**Found:** 18 top-level folders


- `01_Operating/`

- `02_Tax/`

- `03_Financials/`

- `04_Products/`

- `05_Legal/`

- `06_Growth_Marketing/`

- `06_Website/`

- `07_Photos/`

- `08_Archive/`

- `08_Design_Brand/`

- `08_Reports/`

- `09_Projects/`

- `10_Skills_Library/`

- `11_Vendors/`

- `12_Customers/`

- `13_Team/`

- `14_Infrastructure/`

- `99_Inbox/`

- `01_Operating/` — ✓ Has root markdown file(s)

- `02_Tax/` — ❌ No root index `.md` file

- `03_Financials/` — ✓ Has root markdown file(s)

- `04_Products/` — ✓ Has root markdown file(s)

- `05_Legal/` — ✓ Has root markdown file(s)

- `06_Growth_Marketing/` — ❌ No root index `.md` file

- `06_Website/` — ❌ No root index `.md` file

- `07_Photos/` — ❌ No root index `.md` file

- `08_Archive/` — ❌ No root index `.md` file

- `08_Design_Brand/` — ✓ Has root markdown file(s)

- `08_Reports/` — ✓ Has root markdown file(s)

- `09_Projects/` — ✓ Has root markdown file(s)

- `10_Skills_Library/` — ✓ Has root markdown file(s)

- `11_Vendors/` — ✓ Has root markdown file(s)

- `12_Customers/` — ✓ Has root markdown file(s)

- `13_Team/` — ✓ Has root markdown file(s)

- `14_Infrastructure/` — ✓ Has root markdown file(s)

- `99_Inbox/` — ❌ No root index `.md` file


**⚠️ BLOCKER:** 6 folders lack root index files: 02_Tax, 06_Growth_Marketing, 06_Website, 07_Photos, 08_Archive, 99_Inbox

---

## 2. Obsidian Plugins

**Found:** 5 plugin directories: QuickAdd, Templater, obsidian-calendar, obsidian-dataview, obsidian-periodic-notes


### Installation Status

- `QuickAdd`: ❌ Source checkout (not built/installed)

- `Templater`: ⚠️ main.js exists but missing manifest.json

- `obsidian-calendar`: ⚠️ main.js exists but missing manifest.json

- `obsidian-dataview`: ❌ Build artifacts present but no manifest.json

- `obsidian-periodic-notes`: ❌ Empty or not installed


**⚠️ BLOCKER:** 5 plugins are not properly installed as Obsidian community plugins.

---

## 3. Templater Configuration

**Templates folder:** `00_Inbox/07_Templates`

- Target path exists: ❌ (`D:\Work\Torus Coffee Company LLC\00_Inbox\07_Templates` not found)

---

## 4. QuickAdd Configuration

**Choices (macros) found:** 3

- `Daily Ops Log`

- `Quick Inventory Entry`

- `Weekly Review`

---

## 5. Periodic Notes Configuration

**❌ data.json not found — plugin directory is empty or not installed**

---

## 6. Templater Templates

**❌ Templates folder not found:** `00_Inbox/07_Templates`


### Template Search

**❌ No template files found in expected locations.**

---

## 7. Dataview Dashboards

**Expected dashboards:**

- `00_Vault_Home.md` — ✓

  - Contains dataview code

- `00_Inbox/04_Projects/Dataview_Projects_Dashboard.md` — ❌

- `04_Products/Dataview_Products_Dashboard.md` — ✓

  - Contains dataview code

- `03_Financials/Dataview_Financials_Dashboard.md` — ✓

  - Contains dataview code

---

## 8. Task Scheduler

**Found 5 relevant scheduled tasks:**

```
TaskName:      \Torus_Daily_Obsidian_Note
Next Run Time: 8/3/2026 8:00:00 AM
Status:        Ready
Logon Mode:    Interactive only

HostName:      PINKCADY
```

```
TaskName:      \Torus_Monthly_Obsidian_Note
Next Run Time: 9/1/2026 8:00:00 AM
Status:        Ready
Logon Mode:    Interactive only

HostName:      PINKCADY
```

```
TaskName:      \Torus_Vault_Sync_To_GitHub
Next Run Time: 8/3/2026 8:30:00 AM
Status:        Ready
Logon Mode:    Interactive only

HostName:      PINKCADY
```

```
TaskName:      \Torus_Weekly_Obsidian_Note
Next Run Time: 8/3/2026 8:00:00 AM
Status:        Ready
Logon Mode:    Interactive only

HostName:      PINKCADY
```

```
TaskName:      \Microsoft\Windows\ApplicationData\appuriverifierdaily
Next Run Time: N/A
Status:        Ready
Logon Mode:    Interactive/Background

HostName:      PINKCADY
```

**✓ At least 4 Torus-related scheduled tasks found.**

---

## 9. Broken Links & Missing References

**Found 43 potential broken links (sample):**

- `08_Reports\_content_quality_audit_2026-08-02.md` → `...`

- `09_Projects\Trello_Boards\How_to_Use_Trello_Boards.md` → `Card_Weekly_Inventory_Count`

- `09_Projects\Trello_Boards\Business_Docs\Backlog.md` → `Card_Update_Employee_Handbook`

- `09_Projects\Trello_Boards\Business_Docs\Backlog.md` → `Card_Create_Social_Media_Policy`

- `09_Projects\Trello_Boards\Business_Docs\Backlog.md` → `Card_Draft_Return_Policy`

- `09_Projects\Trello_Boards\Business_Docs\Done.md` → `Card_Q2_Financial_Reporting_Checklist`

- `09_Projects\Trello_Boards\Business_Docs\Done.md` → `Card_Vendor_NDA_Template`

- `09_Projects\Trello_Boards\Business_Docs\index.md` → `To Do`

- `09_Projects\Trello_Boards\Business_Docs\index.md` → `In Progress`

- `09_Projects\Trello_Boards\Business_Docs\In_Progress.md` → `Card_Update_LLC_Operating_Agreement`

- `09_Projects\Trello_Boards\Business_Docs\In_Progress.md` → `Card_Draft_Health_Safety_Checklist`

- `09_Projects\Trello_Boards\Business_Docs\Review.md` → `Card_Review_Insurance_Coverage_Policy`

- `09_Projects\Trello_Boards\Business_Docs\Review.md` → `Card_Audit_Customer_Privacy_Policy`

- `09_Projects\Trello_Boards\Business_Docs\To_Do.md` → `Card_Write_SOP_Espresso_Pull`

- `09_Projects\Trello_Boards\Business_Docs\To_Do.md` → `Card_Create_Supplier_Agreement_Template`

- `09_Projects\Trello_Boards\Torus_Ops\Backlog.md` → `Card_Equipment_Maintenance_Schedule`

- `09_Projects\Trello_Boards\Torus_Ops\Backlog.md` → `Card_Supplier_Contract_Renewal`

- `09_Projects\Trello_Boards\Torus_Ops\Backlog.md` → `Card_Staff_Training_Plan_Q4`

- `09_Projects\Trello_Boards\Torus_Ops\Done.md` → `Card_June_Payroll_Processing`

- `09_Projects\Trello_Boards\Torus_Ops\Done.md` → `Card_Coffee_Bean_Sourcing_Ethiopian`

- ... and 23 more

---

## 10. Duplicate Files or Folders

**⚠️ Duplicate names found (excluding system dirs):**

- `06_Growth_Marketing` appears 2 times

- `08_Design_Brand` appears 2 times

- `Taxes` appears 2 times

- `2025` appears 4 times

- `Q2` appears 2 times

- `Bryon Smith K-1 - f1065sk1-v2.pdf` appears 2 times

- `Sara Jane Schedule K-1 - f1065sk1.pdf` appears 2 times

- `Torus Coffee Needs Signed - f1065.pdf` appears 2 times

- `f1065.pdf` appears 2 times

- `Q1` appears 2 times

- `2025-02-28 Statement - USB Checking 5287.pdf` appears 2 times

- `catalog_products.csv` appears 2 times

- `Rainbow_Crunch_Labels_Printable.pdf` appears 2 times

- `ANMP0005.jpg` appears 4 times

- `ANMP0006.jpg` appears 3 times

- `ANMP0007.jpg` appears 3 times

- `ANMP0008.jpg` appears 4 times

- `ANMP0009.jpg` appears 6 times

- `ANMP0010.jpg` appears 6 times

- `ANMP0000.jpg` appears 4 times

- `ANMP0001.jpg` appears 4 times

- `ANMP0002.jpg` appears 3 times

- `ANMP0003.jpg` appears 4 times

- `ANMP0004.jpg` appears 4 times

- `ANMP0011.jpg` appears 5 times

- `ANMP0012.jpg` appears 4 times

- `ANMP0019.jpg` appears 2 times

- `ANMP0014.jpg` appears 2 times

- `ANMP0015.jpg` appears 2 times

- `ANMP0016.jpg` appears 2 times

- ... and 131 more

---

## 11. Google OAuth Token

- Found: `01_Operating\Operating Paperwork\Google Workspace OAuth Setup.md`

  - ⚠️ Contains sensitive credential data

---

## 12. GitHub Repositories

```
origin	https://github.com/toruscoffeecompany/Torus_Ops.git (fetch)
origin	https://github.com/toruscoffeecompany/Torus_Ops.git (push)

```

- ✓ Torus_Ops repo configured

- ⚠️ Torus_website_rebuild remote not found

---

## 13. Website Project Folder (06_Website)

**Path:** `06_Website/`

**Contents (3 items):**

- `PROJECT WEBSITE R3DEPLOY`

- `Website`

- `next-storefront`


**R3DEPLOY items found:** 1

- `06_Website\PROJECT WEBSITE R3DEPLOY`


**R3DEPLOY structure:** 5 items

- `01_Designs`

- `02_Plans`

- `03_Live_Code`

- `04_Archive`

- `index.md`

---

## 14. Colliding Folder Prefixes

**⚠️ Multiple folders share the same numeric prefix:**

- `06_*`: ['06_Growth_Marketing', '06_Website']

- `08_*`: ['08_Archive', '08_Design_Brand', '08_Reports']

---

## 15. Obsidian Vault Configuration

- `config`: ❌ missing

- `hotkeys.json`: ❌ missing

- `community-plugins.json`: ❌ missing

- `graph.json`: ❌ missing

- `workspace.json`: ✓

---

## Summary

**Total issues found:** 13


1. QuickAdd: source checkout, missing manifest.json

2. Templater: missing manifest.json

3. obsidian-calendar: missing manifest.json

4. obsidian-dataview: build artifacts exist but missing manifest.json

5. obsidian-periodic-notes: not properly installed

6. Templater templates_folder points to missing directory

7. Templater templates_folder points to missing directory

8. No template files found in vault

9. Periodic Notes plugin not installed / data.json missing

10. 43 broken links found

11. Duplicate names: 161 sets

12. Torus_website_rebuild remote missing

13. Colliding folder prefixes: 06, 08


**VERDICT: NOT READY** — Vault has critical blockers that must be resolved before website rebuild.
