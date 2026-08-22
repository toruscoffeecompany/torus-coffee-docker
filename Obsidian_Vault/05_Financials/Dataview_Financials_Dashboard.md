# 💰 Financials Dashboard

> Dataview dashboard for expense reports and financial statements.

---

## Expense Reports

```dataview
TABLE 
  date AS "Date",
  category AS "Category",
  amount AS "Amount",
  vendor AS "Vendor",
  status AS "Status",
  payment_method AS "Payment Method"
FROM "03_Financials"
WHERE tags CONTAINS "expense"
SORT date DESC
```

---

## Pending Expenses

```dataview
TABLE 
  date AS "Date",
  category AS "Category",
  amount AS "Amount",
  vendor AS "Vendor"
FROM "03_Financials"
WHERE tags CONTAINS "expense" AND status = "pending"
SORT date ASC
```

> ⚠️ **Action needed:** Review and approve pending expenses.

---

## Expense Summary by Category

```dataview
TABLE 
  sum(amount) AS "Total Spent",
  count() AS "Reports"
FROM "03_Financials"
WHERE tags CONTAINS "expense"
GROUP BY category
SORT sum(amount) DESC
```

---

## Financial Statements

```dataview
TABLE 
  date AS "Date",
  period AS "Period",
  statement_type AS "Type",
  revenue AS "Revenue",
  net_income AS "Net Income"
FROM "03_Financials"
WHERE tags CONTAINS "financial"
SORT date DESC
```

---

## Recent Financial Activity

```dataview
TABLE file.mtime AS "Last Modified"
FROM "03_Financials"
SORT file.mtime DESC
LIMIT 8
```

---

## Quick Links

- 📊 Full expense reports: `Expense_Report_2025.xlsx`, `Expense_Report_2026_Template.xlsx`
- 📈 Financial statements: `Financial_Statements_2025.xlsx`
- 📒 Ledger backups: stored in `03_Financials/`
