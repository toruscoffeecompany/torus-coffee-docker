#!/usr/bin/env python3
"""
Continuous self-repopulating tasklist generator.
Combines Trello cards, GitHub issues, vault audit findings, inbox items, and Docker/K8s tasks.
Uses OODA loop principles to prioritize and generate actionable tasklists.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(r"D:\Work\Torus Coffee Company LLC") / "10_Skills_Library/05_Operations/scripts"))
from credential_loader import load_trello_credentials

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TASKLIST_PATH = VAULT / "10_Skills_Library/05_Operations/CONTINUOUS_TASKLIST.md"
TRELLO_AUDIT = VAULT / "10_Skills_Library/05_Operations/trello_full_audit.json"
GITHUB_ISSUES = VAULT / "10_Skills_Library/05_Operations/github_issues.json"
AUTOMATION_STATUS = VAULT / "10_Skills_Library/05_Operations/automation_status.json"

def load_trello_high_priority():
    """Load P1/P2 Trello cards from audit data."""
    if not TRELLO_AUDIT.exists():
        return []
    
    audit = json.loads(TRELLO_AUDIT.read_text(encoding="utf-8"))
    cards = audit.get("cards", [])
    labels = {l["id"]: l.get("name", "") for l in audit.get("labels", [])}
    lists = {l["id"]: l.get("name", "") for l in audit.get("lists", [])}
    
    high_priority = []
    for c in cards:
        # Labels are stored as full label objects, not just IDs
        card_label_objs = c.get("labels", [])
        card_labels = []
        for lbl in card_label_objs:
            if isinstance(lbl, dict):
                card_labels.append(lbl.get("name", ""))
            else:
                card_labels.append(labels.get(str(lbl), ""))
        
        if "P1" in card_labels or "P2" in card_labels:
            list_name = lists.get(c.get("idList", ""), "Unknown")
            high_priority.append({
                "source": "trello",
                "id": c["id"],
                "name": c["name"],
                "list": list_name,
                "labels": card_labels,
                "due": c.get("due", ""),
                "url": c.get("url", ""),
                "priority": "P1" if "P1" in card_labels else "P2",
            })
    
    return sorted(high_priority, key=lambda x: (0 if x["priority"] == "P1" else 1, x["name"]))

def load_github_high_priority():
    """Load high priority GitHub issues."""
    if not GITHUB_ISSUES.exists():
        return []
    
    issues = json.loads(GITHUB_ISSUES.read_text(encoding="utf-8"))
    high_priority = []
    
    for issue in issues:
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        if any(p in labels for p in ["P1", "P2", "high", "critical", "blocker"]):
            high_priority.append({
                "source": "github",
                "id": str(issue.get("number", "")),
                "name": issue.get("title", ""),
                "labels": labels,
                "state": issue.get("state", ""),
                "url": issue.get("html_url", ""),
                "priority": "P1" if any(p in labels for p in ["P1", "high", "critical", "blocker"]) else "P2",
            })
    
    return sorted(high_priority, key=lambda x: (0 if x["priority"] == "P1" else 1, x["name"]))

def load_vault_tasks():
    """Load vault audit tasks."""
    tasks = []
    
    # Broken links
    snapshot = VAULT / "10_Skills_Library/05_Operations/VAULT_AUDIT_SNAPSHOT.json"
    if snapshot.exists():
        data = json.loads(snapshot.read_text(encoding="utf-8"))
        broken = data.get("broken_links", 0)
        if broken > 0:
            tasks.append({
                "source": "vault",
                "id": "vault-1",
                "name": f"Fix {broken} broken wiki-links in Obsidian vault",
                "priority": "P2",
                "labels": ["obsidian", "vault", "automation"],
            })
        
        # Duplicates
        duplicates = data.get("duplicate_filenames", 0)
        if isinstance(duplicates, dict):
            duplicate_count = len(duplicates)
        else:
            duplicate_count = int(duplicates) if duplicates else 0
        
        if duplicate_count > 0:
            tasks.append({
                "source": "vault",
                "id": "vault-2",
                "name": f"Resolve {duplicate_count} duplicate files in vault",
                "priority": "P3",
                "labels": ["obsidian", "vault", "cleanup"],
            })
    
    return tasks

def load_automation_tasks():
    """Load automation status tasks."""
    tasks = []
    
    if not AUTOMATION_STATUS.exists():
        return tasks
    
    status = json.loads(AUTOMATION_STATUS.read_text(encoding="utf-8"))
    
    for check in status.get("checks", []):
        if check.get("status") == "failed":
            tasks.append({
                "source": "automation",
                "id": f"auto-{check['name']}",
                "name": f"FIX AUTOMATION: {check['name']} — {check.get('note', '')}",
                "priority": "P1",
                "labels": ["automation", "ops", "P1"],
            })
        elif check.get("status") == "partial":
            tasks.append({
                "source": "automation",
                "id": f"auto-{check['name']}",
                "name": f"Complete automation: {check['name']} — {check.get('note', '')}",
                "priority": "P2",
                "labels": ["automation", "ops", "P2"],
            })
    
    return tasks

def load_inbox_tasks():
    """Load tasks from inbox messages."""
    tasks = []
    
    inbox_dir = VAULT / "02_Business_Operations/Communications/Outbox"
    if not inbox_dir.exists():
        return tasks
    
    # Get recent messages (last 24h)
    recent_msgs = sorted(inbox_dir.glob("*.msg.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]
    
    for msg_path in recent_msgs:
        content = msg_path.read_text(encoding="utf-8", errors="ignore")
        # Extract action items from messages
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("- [ ] ") or line.startswith("- [x] ") or "TODO" in line.upper():
                task_text = line.lstrip("- [x] ").lstrip("- [ ] ").strip()
                if task_text and len(task_text) > 10:
                    tasks.append({
                        "source": "inbox",
                        "id": f"inbox-{msg_path.stem}",
                        "name": task_text,
                        "priority": "P2",
                        "labels": ["inbox", "automation"],
                    })
    
    return tasks[:10]  # Limit to 10 inbox tasks

def generate_tasklist():
    """Generate continuous self-repopulating tasklist."""
    print("GENERATING_TASKLIST...")
    
    # Load all tasks
    trello_tasks = load_trello_high_priority()
    github_tasks = load_github_high_priority()
    vault_tasks = load_vault_tasks()
    automation_tasks = load_automation_tasks()
    inbox_tasks = load_inbox_tasks()
    
    all_tasks = trello_tasks + github_tasks + vault_tasks + automation_tasks + inbox_tasks
    
    # Deduplicate by name
    seen = set()
    unique_tasks = []
    for task in all_tasks:
        name_key = task["name"].lower().strip()
        if name_key not in seen:
            seen.add(name_key)
            unique_tasks.append(task)
    
    # Sort by priority
    unique_tasks.sort(key=lambda x: (
        0 if x["priority"] == "P1" else (1 if x["priority"] == "P2" else 2),
        x["source"],
        x["name"]
    ))
    
    # Count by priority
    p1 = len([t for t in unique_tasks if t["priority"] == "P1"])
    p2 = len([t for t in unique_tasks if t["priority"] == "P2"])
    p3 = len([t for t in unique_tasks if t["priority"] == "P3"])
    
    # Generate markdown
    md = f"""# CONTINUOUS SELF-REPOPULATING TASKLIST
Generated: {datetime.utcnow().isoformat()}Z
Sources: Trello, GitHub, Vault Audit, Automation Status, Inbox

## SUMMARY
- Total tasks: {len(unique_tasks)}
- P1 (do now): {p1}
- P2 (this week): {p2}
- P3 (next week): {p3}

## P1 — DO NOW
"""
    for task in unique_tasks:
        if task["priority"] == "P1":
            md += f"- [{task['source'].upper()}] {task['name']}\n"
            if task.get("url"):
                md += f"  - {task['url']}\n"
    
    md += "\n## P2 — THIS WEEK\n"
    for task in unique_tasks:
        if task["priority"] == "P2":
            md += f"- [{task['source'].upper()}] {task['name']}\n"
            if task.get("url"):
                md += f"  - {task['url']}\n"
    
    md += "\n## P3 — NEXT WEEK\n"
    for task in unique_tasks:
        if task["priority"] == "P3":
            md += f"- [{task['source'].upper()}] {task['name']}\n"
            if task.get("url"):
                md += f"  - {task['url']}\n"
    
    md += """
## AUTOMATION
- This file is auto-generated by continuous_tasklist.py
- Run every 15 minutes via cron/Windows Task Scheduler
- Sources: Trello API, GitHub API, VAULT_AUDIT_SNAPSHOT.json, automation_status.json, inbox
"""
    
    TASKLIST_PATH.write_text(md, encoding="utf-8")
    print(f"TASKLIST_GENERATED {len(unique_tasks)} tasks")
    print(f"  P1={p1}, P2={p2}, P3={p3}")
    print(f"  Sources: {len(trello_tasks)} trello, {len(github_tasks)} github, {len(vault_tasks)} vault, {len(automation_tasks)} automation, {len(inbox_tasks)} inbox")
    
    return unique_tasks

if __name__ == "__main__":
    tasks = generate_tasklist()
    print(f"\nTOP 10 TASKS:")
    for i, task in enumerate(tasks[:10], 1):
        print(f"  {i}. [{task['priority']}] [{task['source'].upper()}] {task['name']}")
