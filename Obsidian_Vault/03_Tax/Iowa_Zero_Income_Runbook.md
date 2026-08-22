# Iowa Tax Zero-Income Runbook — Torus Coffee Company

**Date:** 2026-08-04  
**Owner:** Miss Pink  
**Status:** Ready for use  
**Rule:** Free tier first. No paid upgrades without revenue proof.

---

## 1. Iowa Sales/Use Tax Zero Return

**Portal:** GovConnectIowa — `https://govconnect.iowa.gov/`  
**Frequency:** Monthly once active; $0 if no taxable sales  
**Due date:** Last day of month following reporting period

### Steps
1. Log in to GovConnectIowa
2. Select “Sales/Use Tax” → current period
3. Enter $0 taxable sales, $0 tax due
4. Submit return
5. Save confirmation PDF to `02_Tax/Taxes/<year>/Iowa/Sales_Use_Tax_Returns/`
6. Name file: `YYYY-MM-DD Torus Iowa Sales Tax Zero Return.pdf`

---

## 2. Iowa Withholding Tax Zero Return

**When required:** If registered for withholding and have no payroll  
**Frequency:** Monthly or quarterly based on registration  
**Due date:** Last day of month following period

### Steps
1. Log in to GovConnectIowa
2. Select “Withholding Tax” → current period
3. Enter $0 wages, $0 tax withheld
4. Submit return
5. Save confirmation to `02_Tax/Taxes/<year>/Iowa/Withholding_Returns/`
6. Name file: `YYYY-MM-DD Torus Iowa Withholding Zero Return.pdf`

---

## 3. Iowa Partnership Income Tax Zero Return

**Form:** IA 1065  
**Due date:** April 15 for calendar year  
**Requirement:** Must file even with $0 income

### Steps
1. Open Iowa e-file portal or tax software supporting IA 1065
2. Enter $0 income, $0 deductions, $0 tax due
3. Attach statement: “Partnership had no Iowa-source income”
4. E-file or mail with signature
5. Save confirmation to `02_Tax/Taxes/<year>/Iowa/IA_1065/`
6. Name file: `YYYY-MM-DD Torus IA-1065 Zero Return.pdf`

---

## 4. Records Checklist

- [ ] GovConnectIowa confirmation saved
- [ ] Bank $0-payment proof if applicable
- [ ] Daily note updated with filing status
- [ ] Trello card created if deadline is upcoming

---

## 5. Alert Thresholds
- 7 days before deadline → warning
- 1 day before deadline → critical
- Overdue → critical + Gmail alert via alert_router.py
