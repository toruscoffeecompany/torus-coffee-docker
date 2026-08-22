#!/usr/bin/env python3
"""Torus Coffee Company — Obsidian Vault Automation Setup."""
import os
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

FOLDERS = [
    "00_Inbox",
    "01_Daily",
    "02_Weekly",
    "03_Monthly",
    "04_Projects",
    "05_Meetings",
    "06_Research",
    "07_Templates",
]

TEMPLATES = {
    "07_Templates/Daily_Template.md": """# {{date}} — Daily Ops Log

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
""",
    "07_Templates/Weekly_Template.md": """# Week of {{date}} — Weekly Review

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
""",
    "07_Templates/Monthly_Template.md": """# {{date}} — Monthly Review

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
""",
}

def setup():
    print(f"Setting up Obsidian vault at: {VAULT}")
    
    # Create folders
    for folder in FOLDERS:
        path = VAULT / folder
        path.mkdir(exist_ok=True)
        print(f"  Created: {folder}/")
    
    # Create templates
    for template_path, content in TEMPLATES.items():
        full_path = VAULT / template_path
        full_path.write_text(content, encoding="utf-8")
        print(f"  Created: {template_path}")
    
    print("\nObsidian vault setup complete!")
    print("\nNext steps:")
    print("1. Install Obsidian plugins: Periodic Notes, Templater, Dataview, QuickAdd, Calendar")
    print("2. Configure Periodic Notes to use folders 01_Daily, 02_Weekly, 03_Monthly")
    print("3. Configure Templater to use 07_Templates/ for new notes")
    print("4. Run this script weekly via Task Scheduler to create weekly notes")
    print("5. Link business docs using [[wiki-links]] for cross-referencing")

if __name__ == "__main__":
    setup()
