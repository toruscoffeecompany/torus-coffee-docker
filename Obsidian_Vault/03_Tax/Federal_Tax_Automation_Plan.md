# Federal Tax Automation — Torus Coffee Company

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Classification:** Torus-only  
**Rule:** Free tier first. No paid upgrades without revenue proof.

---

## 1. Federal Filing Requirements

### 1.1 Federal Partnership Return
- **Form:** 1065 — U.S. Return of Partnership Income
- **Due date:** March 15 for calendar-year partnerships
- **Zero-income rule:** Must file even with $0 income
- **Outputs:** Form 1065 + Schedule K-1 per partner

### 1.2 Quarterly Estimated Tax
- **Deadlines:**
  - Q4 prior year: January 15
  - Q1 current year: April 15
  - Q2 current year: June 15
  - Q3 current year: September 15
  - Q4 current year: January 15 of next year
- **Threshold:** Owe >= $1,000 when return filed
- **Form:** 1040-ES for individuals; partnership-level estimated tax if applicable

### 1.3 1099/K-1
- **1099-NEC due January 31** to contractors paid >= $600
- **K-1s issued with 1065** to each partner
- **Record retention:** 7 years minimum

---

## 2. Automation Plan

### 2.1 Deadline Tracking
- `tax_preparer.py` tracks:
  - 1065 filing deadline
  - 1040-ES quarterly deadlines
  - 1099/K-1 preparation deadlines

### 2.2 Alerting
- 14 days before deadline → warning
- 7 days before deadline → warning
- 1 day before deadline → critical
- Overdue → critical + Gmail alert

### 2.3 Daily Note Integration
- Every daily note includes upcoming tax deadlines
- Alert router writes warnings/criticals to Obsidian

### 2.4 Records Storage
- All federal tax records stored in `02_Tax/Taxes/<year>/Federal/`
- K-1s stored in partner-specific subfolders
- Bank statements stored by quarter in `02_Tax/Taxes/<year>/U.S. Bank Statements/`

---

## 3. Zero-Income Runbook

### 3.1 Form 1065 Zero Return
1. Open IRS Free File or tax software supporting 1065
2. Enter $0 income, $0 deductions, $0 credits
3. Attach statement: “Partnership had no income or deductions for tax year”
4. E-file or mail with signature
5. Save confirmation to `02_Tax/Taxes/<year>/Federal/`

### 3.2 Schedule K-1 Zero
1. Issue one K-1 per partner with $0 income
2. Both partners sign if filing paper return
3. Save copies in `02_Tax/Taxes/<year>/Federal/K-1s/`

### 3.3 Quarterly Estimated Tax
- If income is $0, estimated tax is $0
- File Form 1040-ES voucher with $0 payment or skip if no liability
- Document decision in `03_Financials/Revenue_Stream_Plan.md`

---

## 4. Task Scheduler Jobs

| Job | Schedule | Script | Purpose |
|-----|----------|--------|---------|
| Torus_Tax_Deadline_Check | Weekly Mondays 7:30 AM | `tax_preparer.py` | Check federal deadlines |
| Torus_Quarterly_Tax_Payment | Quarterly Jan/Apr/Jun/Sep 1st | `tax_preparer.py` | Estimated tax reminder |
| Torus_Annual_Tax_Filing | March 1, April 1, January 1 | `tax_preparer.py` | 1065/K-1/1099 reminders |

---

## 5. Integration Points
- `bank_reconciler.py` → feeds expense data to tax prep
- `alert_router.py` → routes tax alerts to Gmail/Obsidian
- `03_Financials/Revenue_Stream_Plan.md` → tracks income by stream
- `04_Products/inventory_master.json` → COGS basis if needed

---

## 6. Next Actions
1. Update `tax_preparer.py` with full federal deadline calendar
2. Add Iowa tax deadlines from `Iowa_Tax_Automation_Plan.md`
3. Create Task Scheduler jobs
4. Test zero-income runbook before first filing season
5. Document CPA engagement if/when revenue grows
