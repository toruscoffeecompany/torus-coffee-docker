#!/usr/bin/env python3
"""
Accountant automation for Torus Coffee Company.
Monthly bank reconciliation, expense categorization, profit/loss summary.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
BANK_DIR = VAULT / "02_Tax" / "Taxes" / "2025" / "U.S. Bank Statements"
REPORTS_DIR = VAULT / "03_Financials" / "Reports"

def main():
    print("=== Accountant - Torus Coffee Company ===\n")
    
    csv_files = sorted(BANK_DIR.glob("*.csv"))
    if not csv_files:
        print("⚠ No CSV files found in bank directory")
        return
    
    latest_csv = csv_files[-1]
    print(f"Found CSV: {latest_csv.name}")
    print("✓ Accountant ready for bank reconciliation")
    print("  Run bank_reconciler.py for full reconciliation")

if __name__ == "__main__":
    main()
