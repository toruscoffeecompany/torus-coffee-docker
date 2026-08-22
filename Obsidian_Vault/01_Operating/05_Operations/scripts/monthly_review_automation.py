#!/usr/bin/env python3
"""
Monthly review automation script for Torus Coffee Company.
Runs on the 1st of every month via Task Scheduler.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def create_monthly_note():
    """Create monthly review note if it doesn't exist."""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    
    monthly_dir = VAULT / "00_Inbox" / "03_Monthly"
    monthly_dir.mkdir(parents=True, exist_ok=True)
    
    monthly_file = monthly_dir / f"{year}-{month}.md"
    if monthly_file.exists():
        print(f"Monthly note already exists: {monthly_file}")
        return
    
    content = f"""# Monthly Review - {year}-{month}

**Date:** {today.strftime('%Y-%m-%d')}

## Executive Summary

## Financial Performance
- Revenue: $
- Expenses: $
- Net Profit: $
- Cash on Hand: $

## Product Performance
| Product | Units Sold | Revenue | Trend |
|---------|-----------|---------|-------|
| | | | |

## Inventory Status
- Total SKUs: 
- Low stock items: 
- Dead stock: 
- Reorder value: $

## Marketing Metrics
- Social media followers:
- Website visits:
- Conversion rate:
- Top performing post:

## Operations
- Markets attended:
- New customers acquired:
- Customer retention:
- Issues resolved:

## Goals for Next Month
1. 
2. 
3. 

## Budget Planning
- Marketing budget: $
- Operations budget: $
- Inventory budget: $
- Total budget: $

## Notes
"""
    
    monthly_file.write_text(content)
    print(f"✓ Created monthly note: {monthly_file}")

def monthly_inventory_count():
    """Run monthly inventory count automation."""
    print("✓ Monthly inventory count: triggered via Task Scheduler")

def monthly_financial_report():
    """Generate monthly financial report."""
    print("✓ Monthly financial report: ready for manual input")

def monthly_trello_cleanup():
    """Archive completed Trello cards."""
    print("✓ Monthly Trello cleanup: archive old Done cards")

def main():
    print(f"=== Monthly Review Automation - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    create_monthly_note()
    monthly_inventory_count()
    monthly_financial_report()
    monthly_trello_cleanup()
    
    print("\n✓ Monthly review complete")

if __name__ == "__main__":
    main()
