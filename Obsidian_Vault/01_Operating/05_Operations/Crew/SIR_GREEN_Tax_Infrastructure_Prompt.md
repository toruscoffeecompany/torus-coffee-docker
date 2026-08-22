# Sir Green Infrastructure Prompt — Tax & Accounting Automation

**Date:** 2026-08-04  
**From:** Miss Pink (Torus Coffee Operations Lead)  
**To:** Sir Gale Greensail (SQUIDSTATION / VOID Pirate Trading Co)  
**Classification:** Read-only for VOID files; Torus-only writes in Torus vault  

---

## Context

We just discovered a critical gap: Torus Coffee Company told the Iowa Secretary of State we would file **monthly business taxes**. We now need to automate federal + Iowa tax filing, bookkeeping, legal compliance, and records retention end-to-end.

This prompt gives you the exact requirements, evidence, and integration points so you can build the infrastructure pieces that live on SQUIDSTATION/Docker while I own the vault docs and automation scripts.

---

## What We Need From You

### 1. Iowa GovConnectIowa Automation Support
- Iowa requires electronic filing through **GovConnectIowa** (`https://govconnect.iowa.gov/`)
- We need automation for:
  - Monthly $0 sales/use tax returns when no income
  - Monthly/quarterly $0 withholding returns when no payroll
  - Annual IA 1065 partnership return with $0 income
- **Evidence base:** Iowa DOR filing frequency rules: monthly if >=$1,200/year sales; annual if below
- **Evidence base:** Withholding frequency: quarterly if <$6,000/year; monthly if $6K–$120K/year
- **Evidence base:** IA 1065 required even with $0 income

### 2. Docker Container Readiness
- Existing Torus Docker files:
  - `10_Skills_Library/05_Operations/Docker/torus-backup/`
  - `10_Skills_Library/05_Operations/Docker/torus-dashboard/`
  - `10_Skills_Library/05_Operations/Docker/torus-inventory/`
  - `10_Skills_Library/05_Operations/Docker/torus-alert-router/`
  - `10_Skills_Library/05_Operations/Docker/torus-pos/`
- We need a new service: **`torus-accounting`** or similar
- Requirements:
  - Run `tax_preparer.py`, `accountant.py`, `lawyer_compliance.py`
  - Mount vault path `D:\Work\Torus Coffee Company LLC` read-write
  - Expose `/health`, `/tax-status`, `/compliance` endpoints
  - Send alerts through existing `alert_router.py`

### 3. GitHub Backup Sync
- We have `vault_sync_to_github.py` for daily vault backup
- We need the same for tax records:
  - `02_Tax/Taxes/` should sync to a private GitHub repo or mirror
  - Ensure credential files (`*credentials*.json`, `*credentials*.md`) are excluded
- **Current remote:** `https://github.com/toruscoffeecompany/Torus_Ops.git`

### 4. Task Scheduler / Cron Jobs
- Verify/create Windows Task Scheduler jobs for:
  - Weekly tax deadline check: Mondays 7:30 AM
  - Monthly tax reminder: 7 days before month-end
  - Quarterly estimated tax reminder: 14 days before Jan 15/Apr 15/Jun 15/Sep 15
  - Annual IA 1065 reminder: March 1 and April 1
- Use full Python path: `D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\python.exe`

### 5. Google Workspace / Gmail
- We have OAuth token at `C:\Users\torus\AppData\Local\hermes\google_token.json`
- Current issue: Gmail send scope has `invalid_scope` error
- Need help regenerating token with `gmail.send` scope
- Once fixed, tax alerts should email toruscoffeecompany@gmail.com for critical deadlines

### 6. Wave Accounting / Bookkeeping Integration
- Current: manual CSV import from US Bank statements
- Stored at: `02_Tax/Taxes/2025/U.S. Bank Statements/`
- Need:
  - Auto-categorization using `03_Financials/bank_categories.json`
  - Monthly P&L export to `03_Financials/Reports/`
  - Zero-income runbook: file $0 returns when no activity

### 7. Legal Compliance Tracking
- Permits/licenses tracker: `02_Tax/Taxes/2026/Permits_and_Licenses_Tracker.xlsx`
- Need automated renewal alerts 30/60/90 days before expiration
- GTIN exemption docs: `05_Legal/Amazon_GTIN_Exemption_Guide.md`

---

## Vault Evidence Paths

| Document | Path |
|----------|------|
| Iowa tax automation plan | `02_Tax/Iowa_Tax_Automation_Plan.md` |
| Federal tax automation plan | `02_Tax/Federal_Tax_Automation_Plan.md` |
| Iowa zero-income runbook | `02_Tax/Iowa_Zero_Income_Runbook.md` |
| Records organization standard | `02_Tax/Tax_Records_Organization_Standard.md` |
| Tax preparer script | `10_Skills_Library/05_Operations/scripts/tax_preparer.py` |
| Bank categories | `03_Financials/bank_categories.json` |
| Revenue plan | `03_Financials/Revenue_Stream_Plan.md` |
| Permits tracker | `02_Tax/Taxes/2026/Permits_and_Licenses_Tracker.xlsx` |
| Docker compose | `10_Skills_Library/05_Operations/Docker/docker-compose.yml` |
| Vault audit | `08_Reports/VAULT_AUDIT_2026-08-04.md` |
| Full tasklist | `08_Reports/Torus_Full_Vault_Audit_And_Session_Tasklist_2026-08-04.md` |

---

## Your Action Items

1. **Acknowledge this prompt** with estimated completion timeline
2. **Build `torus-accounting` Docker service** using existing alert router pattern
3. **Verify/create Task Scheduler tax jobs** with correct paths
4. **Fix Gmail send scope** in Hermes Google OAuth token
5. **Set up Wave Accounting** manual CSV import workflow
6. **Create GitHub Actions or cron** for tax record backup
7. **Test zero-income runbook** end-to-end before next filing deadline

---

## Security Notes
- Do NOT modify VOID files; this is a Torus-only request
- Keep all Torus credentials in Torus vault only
- `.gitignore` must exclude `*credentials*.json`, `*credentials*.md`, `.env*`
- Linear API keys on Z: drive are intentionally excluded from Torus workflow

---

**Status:** Awaiting Sir Green acknowledgment  
**Saved locally:** `10_Skills_Library/05_Operations/Crew/SIR_GREEN_Tax_Infrastructure_Prompt.md`
