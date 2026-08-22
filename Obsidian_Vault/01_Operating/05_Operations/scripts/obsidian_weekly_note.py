#!/usr/bin/env python3
"""Generate weekly Obsidian note for Torus Coffee Company."""
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
WEEKLY_DIR = VAULT / "00_Inbox" / "02_Weekly"

def generate_weekly_note():
    today = datetime.now()
    # Find Monday of current week
    monday = today - timedelta(days=today.weekday())
    date_str = monday.strftime("%Y-%m-%d")
    filename = f"Week of {date_str}.md"
    filepath = WEEKLY_DIR / filename
    
    if filepath.exists():
        print(f"Weekly note already exists: {filepath}")
        return
    
    content = f"""# Week of {date_str} — Weekly Review

## Inventory Count
- Full count completed: [ ]
- Discrepancies:
- COGS check:

## Expense Review
- This week’s spend:
- Categories:
- Anomalies:

## Goal Progress
- [ ] 
- [ ] 

## Next Week Priorities
- [ ] 
- [ ] 

## Notes
- 
"""
    
    filepath.write_text(content, encoding="utf-8")
    print(f"Created weekly note: {filepath}")

if __name__ == "__main__":
    generate_weekly_note()
