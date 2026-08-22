#!/usr/bin/env python3
"""
Check inventory levels and create alerts for low stock.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY_FILE = VAULT / "04_Products" / "inventory_master.json"
ALERT_THRESHOLD = 5

try:
    from alert_router import route_alert
    HAS_ALERT_ROUTER = True
except ImportError:
    HAS_ALERT_ROUTER = False


def check_inventory():
    """Check inventory levels and return alerts."""
    if not INVENTORY_FILE.exists():
        print("⚠ Inventory file not found")
        return
    
    with open(INVENTORY_FILE) as f:
        inventory = json.load(f)
    
    alerts = []
    products = inventory.get('products', {})
    if isinstance(products, dict):
        for sku, product in products.items():
            qty = product.get('qty', 0)
            name = product.get('name', sku)
            if qty < ALERT_THRESHOLD:
                alerts.append(f"LOW STOCK: {name} ({sku}) - {qty} units remaining")
    else:
        for product in products:
            qty = product.get('quantity', 0)
            if qty < ALERT_THRESHOLD:
                alerts.append(f"LOW STOCK: {product.get('name')} - {qty} units remaining")
    
    if alerts:
        message = f"LOW STOCK: {len(alerts)} products below threshold: " + ", ".join(alerts)
        if HAS_ALERT_ROUTER:
            route_alert("inventory_low_stock", message, severity="warning")
        print("Inventory Alerts:")
        for alert in alerts:
            print(f"  {alert}")
    else:
        msg = "All products above stock threshold"
        if HAS_ALERT_ROUTER:
            route_alert("inventory_check", msg, severity="info")
        print(msg)
    
    return alerts

def main():
    print(f"=== Inventory Alert Check - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    alerts = check_inventory()
    
    if alerts:
        print(f"\n⚠ {len(alerts)} alerts generated")
    else:
        print("\n✓ No alerts")

if __name__ == "__main__":
    main()
