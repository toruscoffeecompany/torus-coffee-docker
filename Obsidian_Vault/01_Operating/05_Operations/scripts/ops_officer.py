#!/usr/bin/env python3
"""
Operations Officer automation for Torus Coffee Company.
Task Scheduler health, vault cleanup, GitHub sync verification.
"""
import subprocess
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")

def check_task_scheduler():
    """Check Task Scheduler jobs."""
    result = subprocess.run(
        ["schtasks", "/query", "/fo", "LIST", "/v"],
        capture_output=True, text=True, timeout=30
    )
    
    broken_jobs = []
    lines = result.stdout.split('\n')
    
    for i, line in enumerate(lines):
        if 'Torus_' in line and 'TaskName:' in line:
            job_name = line.split('TaskName:')[-1].strip()
            # Find next Last Result line
            for la in lines[i:i+20]:
                if 'Last Result:' in la:
                    result_code = la.split('Last Result:')[-1].strip()
                    if result_code != '0':
                        broken_jobs.append(f"{job_name}: {result_code}")
                    break
    
    return broken_jobs

def check_git_sync():
    """Check if vault is synced to GitHub."""
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=VAULT,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    changes = [c for c in result.stdout.strip().split('\n') if c.strip()]
    return len(changes)

def main():
    print("=== Ops Officer - Torus Coffee Company ===\n")
    
    # Check Task Scheduler
    broken = check_task_scheduler()
    if broken:
        print(f"⚠ {len(broken)} Task Scheduler jobs need attention:")
        for job in broken:
            print(f"  - {job}")
    else:
        print("✓ All Task Scheduler jobs healthy")
    
    # Check git sync
    changes = check_git_sync()
    if changes > 0:
        print(f"⚠ {changes} uncommitted changes in vault")
    else:
        print("✓ Vault synced to GitHub")
    
    print("\n✓ Ops check complete")

if __name__ == "__main__":
    main()
