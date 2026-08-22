# 🏷️ Products Dashboard

> Dataview dashboard for product catalog, pricing, and stock status.

---

## Product Catalog

```dataview
TABLE 
  sku AS "SKU",
  category AS "Category",
  price AS "Price",
  stock_status AS "Stock Status",
  supplier AS "Supplier",
  launch_date AS "Launch Date"
FROM "04_Products"
WHERE tags CONTAINS "product"
SORT category ASC, sku ASC
```

---

## Pricing Overview

```dataview
LIST
FROM "04_Products"
WHERE tags CONTAINS "product"
SORT price DESC
```

> 💰 **Price range:** $0.00 – $999.99

---

## Stock Status

### In Stock

```dataview
LIST
FROM "04_Products"
WHERE stock_status = "in-stock"
SORT file.name ASC
```

### Low Stock

```dataview
LIST
FROM "04_Products"
WHERE stock_status = "low-stock"
SORT file.name ASC
```

### Out of Stock

```dataview
LIST
FROM "04_Products"
WHERE stock_status = "out-of-stock"
SORT file.name ASC
```

---

## Product Inventory Summary

```dataview
TABLE 
  count() AS "Total SKUs",
  length(filter(file.etags, (t) => contains(t, "freeze-dried"))) AS "Freeze-Dried",
  length(filter(file.etags, (t) => contains(t, "coffee"))) AS "Coffee"
FROM "04_Products"
WHERE tags CONTAINS "product"
```

---

## Recent Product Updates

```dataview
TABLE file.mtime AS "Last Modified"
FROM "04_Products"
WHERE tags CONTAINS "product"
SORT file.mtime DESC
LIMIT 5
```
