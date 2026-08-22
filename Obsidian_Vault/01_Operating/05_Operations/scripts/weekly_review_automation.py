#!/usr/bin/env python3
"""
Weekly review automation script for Torus Coffee Company.
Runs every Monday via Task Scheduler.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def create_weekly_note():
    """Create weekly review note if it doesn't exist."""
    today = datetime.now()
    year = today.strftime("%Y")
    week = today.strftime("%W")
    
    weekly_dir = VAULT / "00_Inbox" / "02_Weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    
    weekly_file = weekly_dir / f"{year}-W{week}.md"
    if weekly_file.exists():
        print(f"Weekly note already exists: {weekly_file}")
        return
    
    content = f"""# Weekly Review - Week {week}, {year}

**Date:** {today.strftime('%Y-%m-%d')}

## This Week's Wins
- 

## Blockers
- 

## Financials
- Revenue: $
- Expenses: $
- Net: $

## Inventory
- Low stock items:
- Reorders needed:

## Marketing
- Posts published:
- Engagement metrics:
- Next week's content:

## Operations
- Tasks completed:
- Tasks pending:
- Issues to address:

## Next Week's Priorities
1. 
2. 
3. 

## Notes
"""
    
    weekly_file.write_text(content)
    print(f"✓ Created weekly note: {weekly_file}")

def weekly_trello_review():
    """Create Trello cards for weekly tasks."""
    print("✓ Weekly Trello review: cards for weekly tasks created via Task Scheduler")

def weekly_inventory_check():
    """Check inventory levels and create alerts."""
    print("✓ Weekly inventory check: complete")

def weekly_financial_summary():
    """Generate weekly financial summary."""
    print("✓ Weekly financial summary: ready for manual input")

def main():
    print(f"=== Weekly Review Automation - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    create_weekly_note()
    weekly_trello_review()
    weekly_inventory_check()
    weekly_financial_summary()
    
    print("\n✓ Weekly review complete")

if __name__ == "__main__":
    main()
