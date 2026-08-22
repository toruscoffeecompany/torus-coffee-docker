#!/usr/bin/env python3
"""
Inventory Manager automation for Torus Coffee Company.
Stock alerts, reorder points, product photo tracking.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY_FILE = VAULT / "04_Products" / "inventory_master.json"
ALERT_THRESHOLD = 5

def check_stock_levels():
    if not INVENTORY_FILE.exists():
        print("⚠ Inventory file not found")
        return []
    
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    
    alerts = []
    for sku, item in inventory.get('products', {}).items():
        qty = item.get('qty', 0)
        reorder_point = item.get('reorder_point', ALERT_THRESHOLD)
        
        if qty == 0:
            alerts.append({"level": "critical", "sku": sku, "name": item.get('name'), "qty": 0})
        elif qty <= reorder_point:
            alerts.append({"level": "warning", "sku": sku, "name": item.get('name'), "qty": qty})
    
    return alerts

def main():
    print("=== Inventory Manager - Torus Coffee Company ===\n")
    
    alerts = check_stock_levels()
    if alerts:
        print(f"Stock alerts ({len(alerts)}):\n")
        for alert in alerts:
            print(f"[{alert['level'].upper()}] {alert['name']} ({alert['sku']}): {alert['qty']} units")
        
        try:
            from alert_router import route_alert
            critical = [a for a in alerts if a['level'] == 'critical']
            warnings = [a for a in alerts if a['level'] == 'warning']
            
            if critical:
                route_alert("inventory_critical", 
                           f"{len(critical)} products out of stock",
                           severity="critical")
            if warnings:
                route_alert("inventory_warning",
                           f"{len(warnings)} products below reorder point",
                           severity="warning")
        except ImportError:
            pass
    else:
        print("✓ All stock levels healthy")

if __name__ == "__main__":
    main()
