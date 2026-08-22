#!/usr/bin/env python3
"""
Clean up vault: remove temp files, empty folders, duplicates.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def remove_old_temp_files():
    """Remove temp files older than 7 days."""
    temp_dirs = [
        VAULT / "00_Inbox" / "00_Temp",
        VAULT / "99_Inbox" / "Temp",
    ]
    
    removed = 0
    for temp_dir in temp_dirs:
        if not temp_dir.exists():
            continue
        for f in temp_dir.rglob("*"):
            if f.is_file():
                age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                if age > timedelta(days=7):
                    f.unlink()
                    removed += 1
    print(f"✓ Removed {removed} old temp files")

def remove_empty_folders():
    """Remove empty folders."""
    removed = 0
    for root, dirs, files in os.walk(VAULT, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed += 1
            except:
                pass
    print(f"✓ Removed {removed} empty folders")

def main():
    print(f"=== Vault Cleanup - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    remove_old_temp_files()
    remove_empty_folders()
    print("\n✓ Vault cleanup complete")

if __name__ == "__main__":
    main()
