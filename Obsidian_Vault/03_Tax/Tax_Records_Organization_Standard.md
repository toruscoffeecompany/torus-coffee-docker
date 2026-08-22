# Tax Records Organization — Torus Coffee Company

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Status:** Active standard  
**Rule:** Free tier first. No paid upgrades without revenue proof.

---

## 1. Canonical Folder Structure

```
02_Tax/
  Taxes/
    <year>/
      Federal/
        Form_1065/
        K-1s/
        1099s/
      Iowa/
        IA_1065/
        Sales_Use_Tax_Returns/
        Withholding_Returns/
      U.S. Bank Statements/
        Q1/
        Q2/
        Q3/
        Q4/
      Invoices/
      Receipts/
      Permits_and_Licenses/
```

---

## 2. Naming Standard

- `YYYY-MM-DD <Entity> <Form/Type> <Status>.<ext>`
- Examples:
  - `2026-04-15 Torus IA-1065 Zero Return.pdf`
  - `2026-01-31 Torus 1099-NEC Contractors.pdf`
  - `2026-03-31 USB Checking 5287 Statement.pdf`
  - `2026-06-15 Federal Estimated Tax Q2 Payment.pdf`

---

## 3. Retention Rules

- Tax returns + supporting docs: 7 years minimum
- Bank statements: 7 years
- Invoices/receipts: 7 years
- Permits/licenses: keep current + 7 years after expiration

---

## 4. Automation Hooks

- `tax_preparer.py` writes filing confirmations to `02_Tax/Taxes/<year>/...`
- `accountant.py` categorizes bank CSV exports by quarter
- `alert_router.py` alerts when filing deadlines are within 14 days

---

## 5. Annual Migration Rule
- At year-end, move active-year docs from `02_Tax/Taxes/2025/` into archive only after:
  - Federal return filed
  - Iowa return filed
  - All quarterly payments confirmed
  - K-1s/1099s issued
