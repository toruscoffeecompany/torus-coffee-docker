#!/usr/bin/env python3
"""
Legal compliance automation for Torus Coffee Company.
Tracks licenses, permits, insurance renewals, legal deadlines.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LEGAL_DIR = VAULT / "05_Legal"
COMPLIANCE_FILE = LEGAL_DIR / "compliance_tracker.json"

DEFAULT_COMPLIANCE = [
    {"item": "Business Registration Renewal", "due_date": "2027-01-01", "frequency": "annual", "category": "registration"},
    {"item": "Food Handler\'s License", "due_date": "2026-12-01", "frequency": "annual", "category": "health"},
    {"item": "General Liability Insurance", "due_date": "2026-09-01", "frequency": "annual", "category": "insurance"},
    {"item": "Sales Tax Permit", "due_date": "2026-10-01", "frequency": "annual", "category": "tax"},
]

def load_compliance():
    if COMPLIANCE_FILE.exists():
        with open(COMPLIANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": DEFAULT_COMPLIANCE, "last_updated": datetime.now().isoformat()}

def check_deadlines():
    data = load_compliance()
    items = data.get("items", [])
    today = datetime.now()
    alerts = []
    
    for item in items:
        due = datetime.strptime(item.get("due_date", "2099-01-01"), "%Y-%m-%d")
        days_until = (due - today).days
        
        if days_until < 0:
            alerts.append({"level": "critical", "item": item["item"], "days": days_until})
        elif days_until <= 30:
            alerts.append({"level": "warning", "item": item["item"], "days": days_until})
    
    return alerts

def main():
    print("=== Lawyer/Compliance - Torus Coffee Company ===\n")
    alerts = check_deadlines()
    
    if alerts:
        print(f"Found {len(alerts)} compliance alerts:\n")
        for alert in alerts:
            print(f"[{alert['level'].upper()}] {alert['item']}: {alert['days']} days")
        
        try:
            from alert_router import route_alert
            critical = [a for a in alerts if a['level'] == 'critical']
            warnings = [a for a in alerts if a['level'] == 'warning']
            
            if critical:
                route_alert("compliance_critical", f"{len(critical)} overdue compliance items", severity="critical")
            if warnings:
                route_alert("compliance_warning", f"{len(warnings)} items due within 30 days", severity="warning")
        except ImportError:
            pass
    else:
        print("✓ No compliance alerts")

if __name__ == "__main__":
    main()
