# 🚀 Brand Dashboard — Dataview

> Live Dataview queries grounded in the Torus Coffee Company vault.  
> **Sources:** `04_Products/inventory_master.json`, `03_Financials`, `09_Projects/Trello_Boards`, `10_Skills_Library/05_Operations/Crew/Torus_Crew`  
> **Refresh:** Open this note in Obsidian to render queries.  

---

## 1. Product Catalog

```dataview
TABLE 
  sku AS "SKU",
  name AS "Product",
  collection AS "Collection",
  price AS "Price",
  inventory AS "Inventory",
  cost AS "Unit Cost",
  weight AS "Net Wt",
  round((price - cost) / price * 100, 1) AS "Margin %"
FROM "04_Products/inventory_master.json"
WHERE visible = true
SORT collection ASC, sku ASC
```

### Product Stats
- **Total active SKUs:** `TABLE length(rows) FROM "04_Products/inventory_master.json" WHERE visible = true`
- **Total inventory units:** `TABLE sum(inventory) FROM "04_Products/inventory_master.json" WHERE visible = true`
- **Avg. retail price:** `TABLE round(avg(price), 2) FROM "04_Products/inventory_master.json" WHERE visible = true`
- **Catalog value at retail:** `TABLE round(sum(price * inventory), 2) FROM "04_Products/inventory_master.json" WHERE visible = true`

---

## 2. Low Stock & Alerts

```dataview
TABLE 
  sku AS "SKU",
  name AS "Product",
  collection AS "Collection",
  inventory AS "Qty",
  price AS "Price"
FROM "04_Products/inventory_master.json"
WHERE inventory < 10 AND visible = true
SORT inventory ASC
```

---

## 3. Revenue Mix by Collection

```dataview
TABLE 
  length(rows) AS "SKUs",
  sum(inventory) AS "Units",
  round(avg(price), 2) AS "Avg Price",
  round(sum(price * inventory), 2) AS "Inventory Value"
FROM "04_Products/inventory_master.json"
FLATTEN collection AS col
WHERE visible = true
GROUP BY col
SORT "SKUs" DESC
```

---

## 4. Financial Documents

```dataview
TABLE 
  file.link AS "Document",
  file.mtime AS "Last Modified",
  file.size AS "Size"
FROM "03_Financials"
WHERE file.extension = "md"
SORT file.mtime DESC
LIMIT 15
```

### Recent Financial Files
```dataview
TABLE file.mtime AS "Last Modified"
FROM "03_Financials"
SORT file.mtime DESC
LIMIT 8
```

---

## 5. Projects Board

### Active Project Cards
```dataview
TABLE 
  file.link AS "Card",
  board AS "Board",
  status AS "Status",
  priority AS "Priority",
  due AS "Due",
  assignee AS "Assignee",
  tags AS "Tags"
FROM "09_Projects"
WHERE type = "card" AND status != "Done"
SORT priority DESC, due ASC
LIMIT 25
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

### Projects by Status
```dataview
TABLE 
  status AS "Status",
  count() AS "Cards",
  board AS "Board"
FROM "09_Projects"
WHERE type = "card"
GROUP BY status, board
SORT "Cards" DESC
```

### Brand & Marketing Projects
```dataview
TABLE 
  file.link AS "Project",
  status AS "Status",
  board AS "Board"
FROM "09_Projects"
WHERE type = "card" AND tags CONTAINS "brand"
SORT file.mtime DESC
```

---

## 6. Crew Roster

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
  count() AS "Headcount"
FROM "10_Skills_Library/05_Operations/Crew/Torus_Crew"
GROUP BY department
SORT "Headcount" DESC
```

---

## 7. Brand Assets in `08_Design_Brand`

```dataview
TABLE 
  file.name AS "Asset",
  file.folder AS "Folder",
  file.size AS "Size",
  file.mtime AS "Modified"
FROM "08_Design_Brand"
WHERE file.name != "Torus_Brand_Pack.md" 
  AND file.name != "Dataview_Dashboard_Template.md"
  AND file.name != "Dataview_Brand_Dashboard.md"
  AND file.name != "Brand_Style_Guide.md"
SORT file.folder ASC, file.mtime DESC
LIMIT 40
```

---

## 8. Quick Reference

| Section | Source | Key Fields |
|---------|--------|------------|
| Products | `04_Products/inventory_master.json` | `sku`, `name`, `price`, `inventory`, `collection` |
| Financials | `03_Financials` | `tags`, `date`, `amount`, `status` |
| Projects | `09_Projects` | `type`, `board`, `status`, `priority`, `tags`, `due` |
| Crew | `10_Skills_Library/05_Operations/Crew/Torus_Crew` | `rank`, `title`, `department`, `account_type` |

---

*This dashboard is auto-generated from vault data. If queries return empty, verify YAML frontmatter or inline fields exist on target files.*
