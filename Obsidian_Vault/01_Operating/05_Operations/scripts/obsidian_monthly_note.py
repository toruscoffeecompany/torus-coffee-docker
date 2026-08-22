#!/usr/bin/env python3
"""Generate monthly Obsidian note for Torus Coffee Company."""
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
MONTHLY_DIR = VAULT / "00_Inbox" / "03_Monthly"

def generate_monthly_note():
    today = datetime.now()
    date_str = today.strftime("%Y-%m")
    filename = f"{date_str}.md"
    filepath = MONTHLY_DIR / filename
    
    if filepath.exists():
        print(f"Monthly note already exists: {filepath}")
        return
    
    content = f"""# {date_str} — Monthly Review

## Reconciliation
- Bank vs expense report:
- Inventory to COGS:
- Revenue accuracy:

## Tax / Permit Status
- Iowa sales tax filed: [ ]
- Permits expiring soon:
- Estimated tax payment:

## Partner Review
- Contributions:
- Distributions:
- Capital adjustments:

## Next Month Plan
- [ ] 
- [ ] 

## Notes
- 
"""
    
    filepath.write_text(content, encoding="utf-8")
    print(f"Created monthly note: {filepath}")

if __name__ == "__main__":
    generate_monthly_note()
