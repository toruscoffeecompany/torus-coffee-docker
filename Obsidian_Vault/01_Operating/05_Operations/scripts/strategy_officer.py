#!/usr/bin/env python3
"""
Strategy Officer automation for Torus Coffee Company.
Revenue tracking vs milestones, KPI dashboard, upgrade recommendations.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
FINANCIALS_DIR = VAULT / "03_Financials"
REPORTS_DIR = FINANCIALS_DIR / "Reports"

MILESTONES = [
    {"name": "First Revenue", "target": 1, "unit": "dollar", "current": 0},
    {"name": "Sustainable Revenue", "target": 500, "unit": "monthly", "current": 0},
    {"name": "Growth Stage", "target": 1500, "unit": "monthly", "current": 0},
    {"name": "Scale Stage", "target": 5000, "unit": "monthly", "current": 0},
]

def check_milestones():
    report_files = sorted(REPORTS_DIR.glob("bank_reconciliation_*.json"))
    if not report_files:
        return []
    
    latest_report = report_files[-1]
    with open(latest_report, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    monthly_income = report.get("total_income", 0)
    status = []
    
    for milestone in MILESTONES:
        achieved = monthly_income >= milestone["target"]
        status.append({
            "milestone": milestone["name"],
            "target": milestone["target"],
            "current": monthly_income,
            "achieved": achieved,
        })
    
    return status

def main():
    print("=== Strategy Officer - Torus Coffee Company ===\n")
    status = check_milestones()
    
    if status:
        print("Revenue Milestones:\n")
        for s in status:
            icon = "✓" if s["achieved"] else "○"
            print(f"{icon} {s['milestone']}: ${s['target']}/mo (current: ${s['current']})")
        
        try:
            from alert_router import route_alert
            next_milestone = next((s for s in status if not s["achieved"]), None)
            if next_milestone:
                route_alert("strategy_milestone", 
                           f"Next milestone: {next_milestone['milestone']} at ${next_milestone['target']}/mo",
                           severity="info")
        except ImportError:
            pass
    else:
        print("⚠ No bank reconciliation reports found")

if __name__ == "__main__":
    main()
