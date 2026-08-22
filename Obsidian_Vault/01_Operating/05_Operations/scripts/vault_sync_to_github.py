#!/usr/bin/env python3
"""
Vault sync to GitHub - commits and pushes all changes.
Runs daily at 8:30 AM via Task Scheduler.
"""
import os
import subprocess
from subprocess import CREATE_NO_WINDOW
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def run_command(cmd, cwd=None):
    """Run shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=False, creationflags=CREATE_NO_WINDOW,
        capture_output=True,
        text=True,
        cwd=cwd or VAULT
    )
    return result.returncode, result.stdout, result.stderr

def sync_to_github():
    """Commit and push all changes to GitHub."""
    os.chdir(VAULT)
    
    print(f"=== Vault Sync to GitHub - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    # Check git status
    code, stdout, stderr = run_command("git status --short")
    if code != 0:
        print(f"✗ Git status failed: {stderr}")
        return
    
    changes = stdout.strip()
    if not changes:
        print("✓ No changes to commit")
        return
    
    print(f"Found {len(changes.splitlines())} changes")
    
    # Add all changes
    code, stdout, stderr = run_command("git add -A")
    if code != 0:
        print(f"✗ Git add failed: {stderr}")
        return
    print("✓ Git add complete")
    
    # Commit
    commit_msg = f"auto: vault sync {datetime.now().strftime('%Y-%m-%d')}"
    code, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"✗ Git commit failed: {stderr}")
        return
    print(f"✓ Git commit: {commit_msg}")
    
    # Push
    code, stdout, stderr = run_command(
        "git push https://github.com/toruscoffeecompany/Torus_Ops.git main"
    )
    if code != 0:
        print(f"✗ Git push failed: {stderr}")
        return
    print("✓ Git push complete")
    print(f"\n✓ Vault sync complete - {len(changes.splitlines())} files synced")

if __name__ == "__main__":
    sync_to_github()
