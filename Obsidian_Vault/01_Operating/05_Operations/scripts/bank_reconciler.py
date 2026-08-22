#!/usr/bin/env python3
"""
US Bank transaction categorizer for Torus Coffee Company.
Reads exported CSV, categorizes transactions, creates monthly report.
"""
import csv
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
BANK_DIR = VAULT / "02_Tax" / "Taxes" / "2025" / "U.S. Bank Statements"
CATEGORIES_FILE = VAULT / "03_Financials" / "bank_categories.json"

CATEGORIES = {
    "square_payment": ["SQUARE INC", "SQUARE"],
    "venmo": ["VENMO"],
    "supplies": ["AMAZON", "OFFICEDEPOT", "UBER"],
    "shipping": ["USPS", "FEDEX", "UPS"],
    "food": ["HY-VEE", "CASH STORE", "GATEWAY"],
    "gas": ["CIRCLE K", "KUM&GO", "PILOT"],
    "income": ["DEPOSIT", "TRANSFER"],
}

def load_categories():
    """Load custom categories from file."""
    if CATEGORIES_FILE.exists():
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return {**CATEGORIES, **json.load(f)}
    return CATEGORIES

def categorize_transaction(description, categories):
    """Categorize a transaction by description keywords."""
    desc_upper = description.upper()
    for category, keywords in categories.items():
        if any(kw in desc_upper for kw in keywords):
            return category
    return "uncategorized"

def reconcile_month(csv_file):
    """Reconcile a month's transactions from CSV."""
    if not csv_file.exists():
        print(f"⚠ CSV file not found: {csv_file}")
        return None

    categories = load_categories()
    transactions = []

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            txn = {
                "date": row.get("Date", ""),
                "description": row.get("Description", ""),
                "amount": float(row.get("Amount", 0)),
                "category": categorize_transaction(row.get("Description", ""), categories),
            }
            transactions.append(txn)

    # Save categorized transactions
    output_file = BANK_DIR / f"categorized_{datetime.now().strftime('%Y%m%d')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2)

    print(f"✓ Reconciled {len(transactions)} transactions")
    print(f"  Saved to: {output_file}")
    return transactions

def generate_monthly_report(transactions):
    """Generate monthly spending report."""
    categories = {}
    total_spent = 0
    total_income = 0

    for txn in transactions:
        cat = txn["category"]
        amount = txn["amount"]

        if cat not in categories:
            categories[cat] = {"count": 0, "total": 0}

        categories[cat]["count"] += 1
        categories[cat]["total"] += amount

        if amount < 0:
            total_spent += abs(amount)
        else:
            total_income += amount

    report = {
        "month": datetime.now().strftime("%Y-%m"),
        "total_spent": round(total_spent, 2),
        "total_income": round(total_income, 2),
        "net": round(total_income - total_spent, 2),
        "by_category": {k: {"count": v["count"], "total": round(v["total"], 2)} for k, v in categories.items()},
    }

    # Save report
    report_file = VAULT / "03_Financials" / "Reports" / f"bank_reconciliation_{datetime.now().strftime('%Y%m%d')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Monthly Bank Reconciliation ===")
    print(f"Month: {report['month']}")
    print(f"Total Income: ${report['total_income']:.2f}")
    print(f"Total Spent: ${report['total_spent']:.2f}")
    print(f"Net: ${report['net']:.2f}")
    print(f"\nBy Category:")
    for cat, data in report["by_category"].items():
        print(f"  {cat}: {data['count']} txns, ${data['total']:.2f}")

    print(f"\n✓ Report saved to: {report_file}")
    return report

def main():
    print("=== US Bank Transaction Reconciler ===\n")

    # Find latest CSV in bank directory
    csv_files = sorted(BANK_DIR.glob("*.csv"))
    if not csv_files:
        print("⚠ No CSV files found in bank directory")
        print(f"  Export CSV from US Bank online banking and save to: {BANK_DIR}")
        return

    latest_csv = csv_files[-1]
    print(f"Found CSV: {latest_csv.name}")

    transactions = reconcile_month(latest_csv)
    if transactions:
        generate_monthly_report(transactions)
        print("\n✓ Reconciliation complete")

if __name__ == "__main__":
    main()
