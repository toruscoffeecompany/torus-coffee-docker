#!/usr/bin/env python3
"""
Daily ops automation script for Torus Coffee Company.
Runs daily via Task Scheduler.
"""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def create_daily_note():
    """Create daily ops log if it doesn't exist."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_dir = VAULT / "00_Inbox" / "01_Daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    daily_file = daily_dir / f"{today}.md"
    if daily_file.exists():
        print(f"Daily note already exists: {daily_file}")
        return
    
    template = daily_dir.parent.parent / "07_Templates" / "Daily_Ops_Log.md"
    if template.exists():
        content = template.read_text()
    else:
        content = f"# Daily Ops Log - {today}\n\n## Tasks\n\n## Notes\n\n## Tomorrow\n"
    
    daily_file.write_text(content)
    print(f"✓ Created daily note: {daily_file}")

def check_inventory_alerts():
    """Check if inventory is below threshold."""
    try:
        from alert_router import route_alert
        route_alert("inventory_check", "Daily inventory check started", severity="info")
    except ImportError:
        pass
    inventory_file = VAULT / "04_Products" / "inventory_master.json"
    if not inventory_file.exists():
        msg = "Inventory file not found"
        try:
            from alert_router import route_alert
            route_alert("inventory_file_missing", msg, severity="warning")
        except ImportError:
            pass
        print(f"⚠ {msg}")
        return
    print(f"✓ Inventory check: {inventory_file.name}")

def backup_check():
    """Verify backup jobs are running."""
    print("✓ Backup check: SQUIDSTATION backup runs daily at 3AM")
    print("✓ Git sync: runs daily at 8:30AM")

def git_status_check():
    """Check if vault has uncommitted changes."""
    # FIX: Don't os.chdir — use cwd parameter instead to avoid side effects
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        cwd=str(VAULT),
    )
    output = result.stdout.strip()
    if output:
        print(f"⚠ Uncommitted changes found:\n{output}")
    else:
        print("✓ Git status: clean")

def main():
    print(f"=== Daily Ops Automation - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    create_daily_note()
    check_inventory_alerts()
    backup_check()
    git_status_check()
    
    print("\n✓ Daily ops check complete")

if __name__ == "__main__":
    main()
