# Iowa Business Tax Automation — Torus Coffee Company

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Classification:** Torus-only  
**Rule:** Free tier first. No paid upgrades without revenue proof.

---

## 1. Iowa Monthly/Quarterly Tax Filing Plan

### 1.1 Sales/Use Tax
- **Expected filing frequency:** Monthly once you cross $1,200/year in taxable sales; annual if below that threshold.
- **Payment portal:** GovConnectIowa only — `https://govconnect.iowa.gov/`
- **General due date:** Last day of the month following the reporting period.
- **Zero-income runbook:** File a $0 sales/use tax return monthly until taxable sales begin; do not skip returns once a permit is active.
- **Evidence to keep:** GovConnectIowa confirmation number, screenshot/PDF of $0 return, bank $0-payment proof if applicable.

### 1.2 Withholding Tax
- **Frequency thresholds:** Quarterly if <$6,000/year; monthly if $6,000–$120,000/year; semimonthly if >$120,000/year.
- **Due cadence:** Monthly filers pay twice monthly and one quarterly return per quarter.
- **Zero-income runbook:** If no payroll yet, file $0 withholding returns on schedule once registered.

### 1.3 Iowa Partnership Income Tax
- **Form:** IA 1065
- **Due date:** 15th day of the 4th month after year end; for calendar year = April 15.
- **Zero-income requirement:** Even with $0 income, an IA 1065 informational return is required for active partnerships.
- **Supporting forms:** IA Schedule K-1 per partner; keep zeroed schedules in `02_Tax/Taxes/<year>/Federal/`.

---

## 2. Federal Tax Automation Plan

### 2.1 Federal Partnership Return
- **Form:** 1065
- **Due date:** March 15 for calendar-year partnerships.
- **State equivalent:** Iowa IA 1065 due April 15.
- **Zero-income runbook:** File 1065 with $0 income; issue $0 Schedule K-1s to both members.

### 2.2 Quarterly Estimated Tax
- **Deadlines:**
  - Q4 prior-year payment: January 15
  - Q1 current-year: April 15
  - Q2 current-year: June 15
  - Q3 current-year: September 15
  - Q4 current-year: January 15 of next year
- **Trigger:** Estimated tax owed >= $1,000.
- **Automation:** Use `tax_preparer.py` deadline checker + alert router; add calendar reminders and daily-note alerts 14 days before each deadline.

### 2.3 1099/K-1 Prep
- **1099-NEC/K due January 31** to contractors.
- **K-1s due with 1065 filing; keep copies in `02_Tax/Taxes/<year>/Federal/`.**

---

## 3. Records Organization Rules

### 3.1 Folder Structure
```
02_Tax/
  Taxes/
    <year>/
      Federal/
        Form 1065 + schedules/
        K-1s/
      Iowa/
        IA 1065/
        Sales_Use_Tax_Returns/
        Withholding_Returns/
      U.S. Bank Statements/
        Q1/ Q2/ Q3/ Q4/
      Invoices/
      Receipts/
```

### 3.2 Naming Convention
- `YYYY-MM-DD <entity> <form> <status>.pdf`
- Examples:
  - `2026-04-15 Torus IA-1065 filed.pdf`
  - `2026-01-31 Torus 1099-NEC contractors.pdf`
  - `2026-02-28 USB Checking 5287 statement.pdf`

### 3.3 Retention
- Keep tax records minimum 7 years.
- Store source docs in `02_Tax/` only; never in `08_Archive/` for active-year tax material.

---

## 4. Automated Calendar Reminders

### 4.1 Recurring Reminders
| Frequency | Reminder | Lead Time |
|-----------|----------|-----------|
| Monthly | Iowa sales/use tax zero return | 7 days before due |
| Monthly | Withholding zero return if registered | 7 days before due |
| Quarterly | Federal estimated tax payment | 14 days before due |
| Annually | IA 1065 + 1065 filing | 30 days before April 15 |
| Annually | 1099/K-1 prep | 21 days before January 31 |

### 4.2 Implementation
- Use Obsidian Periodic Notes daily note to surface upcoming tax deadlines.
- Use Task Scheduler to run `tax_preparer.py` weekly on Mondays.
- Route critical overdue tax items through `alert_router.py` to Gmail/Obsidian.

---

## 5. Automation Script Requirements

### 5.1 `tax_preparer.py` Enhancements
- Add Iowa sales/use tax zero-return scheduler
- Add withholding zero-return scheduler
- Add federal estimated tax payment reminders
- Add annual IA 1065 / Form 1065 reminders
- Write monthly tax status to `00_Inbox/01_Daily/<date>.md`

### 5.2 `accountant.py` Enhancements
- Auto-categorize bank transactions using `bank_categories.json`
- Produce monthly P&L from bank CSV exports
- Export categorized CSV to `03_Financials/Reports/`

### 5.3 `lawyer_compliance.py` Enhancements
- License renewal reminders
- Insurance expiration alerts
- GTIN/exemption deadline tracking

---

## 6. Free-Tier Stack

| Function | Tool | Notes |
|----------|------|-------|
| Bookkeeping | Wave Accounting Free | Manual CSV import until revenue grows |
| Tax filing | GovConnectIowa | Iowa sales/withholding; free portal |
| Federal filing | IRS e-file / Free File | Partnership 1065; free when income is low |
| Calendar | Google Calendar Free | Tax deadline reminders |
| Expense tracking | Excel/Sheets | `03_Financials/Expense_Report_2026_Template.xlsx` |
| Document storage | Obsidian vault `02_Tax/` | Never store in git-exposed paths |

---

## 7. Next Actions

1. **Today:** Add Iowa tax calendar + zero-return runbook to vault
2. **This week:** Update `tax_preparer.py` with Iowa/federal deadlines
3. **This week:** Add Task Scheduler weekly tax reminder job
4. **Before next filing deadline:** Run end-to-end test with $0 return workflow
5. **When revenue starts:** Enable expense categorization + monthly P&L automation
