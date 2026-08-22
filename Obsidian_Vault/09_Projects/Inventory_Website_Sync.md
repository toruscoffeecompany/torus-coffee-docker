# Inventory → Website Sync Automation

## Overview
Automatically syncs inventory status from Excel/JSON to website product listings. When stock hits 0, product is hidden. When restocked, product reappears.

## Components

### 1. Inventory Data Source
**File:** `04_Products/inventory_master.json`
```json
{
  "TCC-SS-05": {
    "name": "Solar Strawberries",
    "qty": 0,
    "reorder_point": 10,
    "status": "out_of_stock"
  }
}
```

### 2. Website Sync Script
**File:** `10_Skills_Library/05_Operations/scripts/inventory_sync.py`
- Reads inventory_master.json
- Updates website product data file
- Hides out-of-stock products
- Logs changes to daily note

### 3. Alert Trigger
- Stock hits 0 → Warning alert to Obsidian
- Stock below reorder_point → Info alert to log
- Stock restocked → Info alert to log

## Implementation

```python
#!/usr/bin/env python3
"""
Inventory to website sync automation.
Updates website product data from inventory_master.json.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY_FILE = VAULT / "04_Products" / "inventory_master.json"
WEBSITE_DATA = VAULT / "06_Website" / "website" / "data" / "products.json"

def sync_inventory_to_website():
    """Sync inventory status to website product data."""
    if not INVENTORY_FILE.exists():
        print("⚠ Inventory file not found")
        return
    
    with open(INVENTORY_FILE) as f:
        inventory = json.load(f)
    
    products = {}
    for sku, item in inventory.get('products', {}).items():
        qty = item.get('qty', 0)
        products[sku] = {
            "name": item.get('name', sku),
            "price": item.get('price', 0),
            "inStock": qty > 0,
            "qty": qty,
            "reorderPoint": item.get('reorder_point', 5)
        }
    
    WEBSITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(WEBSITE_DATA, "w") as f:
        json.dump(products, f, indent=2)
    
    print(f"✓ Synced {len(products)} products to website data")
    
    # Route alerts
    try:
        from alert_router import route_alert
        out_of_stock = [p['name'] for p in products.values() if not p['inStock']]
        if out_of_stock:
            route_alert("inventory_out_of_stock", 
                       f"{len(out_of_stock)} products out of stock: {', '.join(out_of_stock)}",
                       severity="warning")
    except ImportError:
        pass

if __name__ == "__main__":
    sync_inventory_to_website()
```

## Task Scheduler
- **Job:** Torus_Inventory_Sync
- **Schedule:** Every 4 hours
- **Script:** inventory_sync.py

## Website Integration
- Next.js reads `data/products.json` on build
- Products with `inStock: false` show "Sold Out" badge
- Add to cart button disabled for out-of-stock items
