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
        return False
    
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    
    products = {}
    raw_products = inventory.get('products', [])
    if isinstance(raw_products, dict):
        raw_products = [raw_products]
    for item in raw_products:
        sku = item.get('sku')
        if not sku:
            continue
        qty = item.get('inventory', item.get('qty', 0))
        products[sku] = {
            "name": item.get('name', sku),
            "price": item.get('price', 0),
            "inStock": qty > 0,
            "qty": qty,
            "reorderPoint": item.get('reorder_point', 5),
        }
    
    WEBSITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(WEBSITE_DATA, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)
    
    print(f"✓ Synced {len(products)} products to website data")
    
    try:
        from alert_router import route_alert
        out_of_stock = [p['name'] for p in products.values() if not p['inStock']]
        if out_of_stock:
            route_alert("inventory_out_of_stock", 
                       f"{len(out_of_stock)} products out of stock: {', '.join(out_of_stock)}",
                       severity="warning")
    except ImportError:
        pass
    
    return True

if __name__ == "__main__":
    print("=== Inventory Sync to Website ===\n")
    sync_inventory_to_website()
