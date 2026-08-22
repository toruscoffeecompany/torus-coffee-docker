#!/usr/bin/env python3
"""
Tax Preparer automation for Torus Coffee Company.
Federal + Iowa tax deadlines, zero-income runbook checks, reminder output.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
FINANCIALS_DIR = VAULT / "03_Financials"
TAX_DIR = VAULT / "02_Tax"
DAILY_DIR = VAULT / "00_Inbox" / "01_Daily"

def get_tax_deadlines(year=None):
    """Return federal + Iowa tax deadlines for the given year."""
    today = datetime.now()
    year = year or today.year

    deadlines = [
        # Federal
        {"name": "Federal Q4 Estimated Tax (prior year)", "date": f"{year-1}-01-15", "type": "quarterly", "jurisdiction": "federal"},
        {"name": "Federal Form 1065 due", "date": f"{year}-03-15", "type": "annual", "jurisdiction": "federal"},
        {"name": "Federal Q1 Estimated Tax", "date": f"{year}-04-15", "type": "quarterly", "jurisdiction": "federal"},
        {"name": "Federal Q2 Estimated Tax", "date": f"{year}-06-15", "type": "quarterly", "jurisdiction": "federal"},
        {"name": "Federal Q3 Estimated Tax", "date": f"{year}-09-15", "type": "quarterly", "jurisdiction": "federal"},
        {"name": "Federal Q4 Estimated Tax", "date": f"{year}-01-15", "type": "quarterly", "jurisdiction": "federal"},
        {"name": "1099-NEC due to contractors", "date": f"{year}-01-31", "type": "annual", "jurisdiction": "federal"},
        # Iowa
        {"name": "Iowa IA 1065 due", "date": f"{year}-04-15", "type": "annual", "jurisdiction": "iowa"},
        {"name": "Iowa sales/use tax zero return", "date": f"{year}-02-01", "type": "monthly", "jurisdiction": "iowa", "note": "file by last day of month following period"},
        {"name": "Iowa withholding tax zero return", "date": f"{year}-02-01", "type": "monthly", "jurisdiction": "iowa", "note": "file by last day of month following period"},
    ]

    return deadlines

def check_tax_deadlines(year=None):
    """Check for upcoming tax deadlines and return alerts."""
    today = datetime.now()
    deadlines = get_tax_deadlines(year)
    alerts = []

    for deadline in deadlines:
        try:
            due = datetime.strptime(deadline["date"], "%Y-%m-%d")
        except ValueError:
            continue

        days_until = (due - today).days

        if days_until < 0:
            alerts.append({
                "level": "critical",
                "item": f"{deadline['jurisdiction'].upper()}: {deadline['name']}",
                "days": days_until,
                "due": deadline["date"],
                "type": deadline["type"],
            })
        elif days_until <= 14:
            alerts.append({
                "level": "critical",
                "item": f"{deadline['jurisdiction'].upper()}: {deadline['name']}",
                "days": days_until,
                "due": deadline["date"],
                "type": deadline["type"],
            })
        elif days_until <= 30:
            alerts.append({
                "level": "warning",
                "item": f"{deadline['jurisdiction'].upper()}: {deadline['name']}",
                "days": days_until,
                "due": deadline["date"],
                "type": deadline["type"],
            })
        elif days_until <= 90:
            alerts.append({
                "level": "info",
                "item": f"{deadline['jurisdiction'].upper()}: {deadline['name']}",
                "days": days_until,
                "due": deadline["date"],
                "type": deadline["type"],
            })

    return sorted(alerts, key=lambda x: x["days"])

def write_daily_note_alerts(alerts):
    """Append tax alerts to today's daily note."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_path = DAILY_DIR / f"{today_str}.md"

    if not alerts:
        return

    lines = ["\n## Tax Alerts\n"]
    for alert in alerts:
        lines.append(f"- [{alert['level'].upper()}] {alert['item']}: {alert['days']} days (due {alert['due']})")

    if daily_path.exists():
        existing = daily_path.read_text(encoding="utf-8")
        daily_path.write_text(existing + "\n".join(lines), encoding="utf-8")
    else:
        daily_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    print("=== Tax Preparer - Torus Coffee Company ===\n")

    alerts = check_tax_deadlines()
    write_daily_note_alerts(alerts)

    if alerts:
        print(f"Tax deadlines ({len(alerts)}):\n")
        for alert in alerts:
            print(f"[{alert['level'].upper()}] {alert['item']}: {alert['days']} days (due {alert['due']})")

        try:
            from alert_router import route_alert
            critical = [a for a in alerts if a["level"] == "critical"]
            warnings = [a for a in alerts if a["level"] == "warning"]

            if critical:
                route_alert("tax_critical", f"{len(critical)} urgent tax items", severity="critical")
            if warnings:
                route_alert("tax_warning", f"{len(warnings)} tax deadlines within 30 days", severity="warning")
        except ImportError:
            pass
    else:
        print("✓ No urgent tax deadlines")

if __name__ == "__main__":
    main()
