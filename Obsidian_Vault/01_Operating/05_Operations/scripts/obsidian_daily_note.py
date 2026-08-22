#!/usr/bin/env python3
"""Generate daily Obsidian note for Torus Coffee Company."""
import os
from pathlib import Path
from datetime import datetime

# Resolve vault path relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent
VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DAILY_DIR = VAULT / "00_Inbox" / "01_Daily"

def generate_daily_note():
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    filename = f"{date_str}.md"
    filepath = DAILY_DIR / filename
    
    if filepath.exists():
        print(f"Daily note already exists: {filepath}")
        return
    
    content = f"""# {date_str} — Daily Ops Log

## OODA Loop
- **Observe:** 
- **Orient:** 
- **Decide:** 
- **Act:** 

## Inventory Quick Log
- Freeze-dryer batches:
- Pack/ship count:
- Low stock alerts:

## Sales Log
- Online orders:
- Market/pop-up sales:
- Wholesale inquiries:

## Issues / Blockers
- 

## Next Actions
- [ ] 
- [ ] 

## Notes
- 
"""
    
    filepath.write_text(content, encoding="utf-8")
    print(f"Created daily note: {filepath}")

if __name__ == "__main__":
    generate_daily_note()
