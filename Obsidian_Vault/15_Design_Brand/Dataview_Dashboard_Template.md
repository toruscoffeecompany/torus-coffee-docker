# Dataview Dashboard Template — Torus Coffee Company

> **Purpose:** Reusable Dataview query blocks for products, financials, projects, and crew.  
> **How to use:** Copy query blocks into any dashboard note. Adjust paths and WHERE clauses to match your folder structure.  
> **Vault convention:** Files should use YAML frontmatter or inline fields (`key:: value`) for Dataview to surface properties.  

---

## 1. Products

### Product Catalog (from `inventory_master.json`)
```dataview
TABLE 
  sku AS "SKU",
  name AS "Product",
  collection AS "Collection",
  price AS "Price",
  inventory AS "Inventory",
  cost AS "Unit Cost",
  weight AS "Net Wt",
  ribbon AS "Ribbon"
FROM "04_Products/inventory_master.json"
WHERE visible = true
SORT collection ASC, sku ASC
```

### Low Stock Alerts
```dataview
TABLE 
  sku AS "SKU",
  name AS "Product",
  inventory AS "Qty Remaining",
  price AS "Price"
FROM "04_Products/inventory_master.json"
WHERE inventory < 10 AND visible = true
SORT inventory ASC
LIMIT 10
```

### Revenue-at-Risk (out of stock / hidden)
```dataview
TABLE 
  sku AS "SKU",
  name AS "Product",
  price AS "Price",
  inventory AS "Inventory"
FROM "04_Products/inventory_master.json"
WHERE inventory = 0 OR visible = false
SORT price DESC
```

### Collection Summary
```dataview
TABLE 
  length(rows) AS "SKU Count",
  sum(rows.price) AS "List Value",
  sum(rows.inventory) AS "Total Units"
FROM "04_Products/inventory_master.json"
FLATTEN collection AS col
WHERE visible = true
GROUP BY col
SORT "SKU Count" DESC
```

---

## 2. Financials

### Expense Register
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

### Pending Expenses
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

### Spend by Category
```dataview
TABLE 
  sum(amount) AS "Total Spent",
  count() AS "Reports"
FROM "03_Financials"
WHERE tags CONTAINS "expense"
GROUP BY category
SORT "Total Spent" DESC
```

### Financial Statements
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

### Recent Financial Activity
```dataview
TABLE file.mtime AS "Last Modified"
FROM "03_Financials"
SORT file.mtime DESC
LIMIT 8
```

---

## 3. Projects

### Active Projects Board
```dataview
TABLE 
  status AS "Status",
  priority AS "Priority",
  due AS "Due Date",
  tags AS "Tags"
FROM "09_Projects"
WHERE type = "card" AND status != "Done"
SORT priority DESC, due ASC
```

### Projects by Board
```dataview
TABLE 
  board AS "Board",
  status AS "Status",
  priority AS "Priority"
FROM "09_Projects"
WHERE type = "card"
SORT board ASC, status ASC
```

### High-Priority To-Do
```dataview
TABLE 
  file.link AS "Task",
  board AS "Board",
  due AS "Due",
  assignee AS "Assignee"
FROM "09_Projects"
WHERE type = "card" AND priority = "high" AND status != "Done"
SORT due ASC
LIMIT 15
```

### Tag Filter (brand / marketing / design)
```dataview
TABLE 
  file.link AS "Project",
  status AS "Status",
  board AS "Board"
FROM "09_Projects"
WHERE type = "card" AND tags CONTAINS "brand"
SORT file.mtime DESC
```

### Recent Project Updates
```dataview
TABLE file.mtime AS "Last Modified"
FROM "09_Projects"
SORT file.mtime DESC
LIMIT 10
```

---

## 4. Crew

### Crew Roster
```dataview
TABLE 
  rank AS "Rank",
  title AS "Title",
  department AS "Department",
  account_type AS "Account Type",
  station AS "Station"
FROM "10_Skills_Library/05_Operations/Crew/Torus_Crew"
SORT rank ASC
```

### Crew by Department
```dataview
TABLE 
  department AS "Department",
  length(rows) AS "Headcount"
FROM "10_Skills_Library/05_Operations/Crew/Torus_Crew"
GROUP BY department
SORT "Headcount" DESC
```

### Bots vs Humans
```dataview
TABLE 
  account_type AS "Account Type",
  count() AS "Count"
FROM "10_Skills_Library/05_Operations/Crew/Torus_Crew"
GROUP BY account_type
```

### Active Crew (recently updated profiles)
```dataview
TABLE 
  file.mtime AS "Last Updated",
  title AS "Title",
  station AS "Station"
FROM "10_Skills_Library/05_Operations/Crew/Torus_Crew"
SORT file.mtime DESC
LIMIT 10
```

---

## 5. Cross-Vault Brand Dashboard

### Brand Asset Inventory
```dataview
TABLE 
  file.folder AS "Folder",
  file.name AS "Asset",
  file.size AS "Size",
  file.mtime AS "Modified"
FROM "08_Design_Brand"
WHERE file.name != "Torus_Brand_Pack.md" 
  AND file.name != "Dataview_Dashboard_Template.md"
  AND file.name != "Brand_Style_Guide.md"
SORT file.folder ASC, file.mtime DESC
LIMIT 30
```

### Recent Vault-Wide Activity
```dataview
TABLE 
  file.folder AS "Folder",
  file.name AS "File",
  file.mtime AS "Modified"
FROM "D:/Work/Torus Coffee Company LLC"
WHERE file.name != "_analysis.json" 
  AND file.name != "_file_inventory.json"
  AND file.name != "_inventory_history.json"
  AND file.extension = "md"
SORT file.mtime DESC
LIMIT 20
```

---

## 6. Notes on Implementation

- **JSON files:** `inventory_master.json` works with Dataview when each top-level array element is treated as a virtual "page." Fields like `sku`, `price`, and `inventory` are queryable directly.
- **Inline fields:** If files lack YAML frontmatter, use Obsidian's inline field syntax (`field:: value`) anywhere in the note.
- **Tags:** Standard Dataview tags use `tags:: [value1, value2]` or YAML frontmatter `tags: [value1, value2]`.
- **Performance:** Limit `TABLE` queries to 100 rows. Use `GROUP BY` for summaries.
- **Fallback:** If a query returns no results, verify the folder path and confirm properties exist on the target files.
