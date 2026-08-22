#!/usr/bin/env python3
"""
Sir Green Auto-Prompt Generator — Torus Coffee Company
Generates self-prompting messages for Miss Pink based on Docker/goals/tasklist.
Runs as scheduled task/daemon.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
TASKLIST = VAULT / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
DOCKER_PROMPT = VAULT / "10_Skills_Library/05_Operations/Docker/SIR_GREEN_DEPLOYMENT_PROMPT.md"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def extract_sirgreen_tasks(tasklist_text: str) -> list:
    """Extract Sir Green-related tasks from tasklist."""
    tasks = []
    keywords = ["Docker", "SQUIDSTATION", "Sir Green", "torus-", "container", "backup", "alert", "Gmail", "Discord", "webhook"]
    for line in tasklist_text.splitlines():
        if line.startswith("- [ ] ") and any(k.lower() in line.lower() for k in keywords):
            tasks.append(line.replace("- [ ] ", "").strip())
    return tasks


def build_prompt_message(tasks: list) -> dict:
    """Build a self-prompt message for Miss Pink from Sir Green."""
    ts = now_stamp()
    msg_id = f"auto_{ts}"
    
    body_lines = [
        "# Auto-Prompt: Sir Green Infrastructure Goals",
        "",
        f"Generated: {now_iso()}",
        "",
        "## Current Focus",
        "",
    ]
    
    if tasks:
        body_lines.append("### Pending Tasks")
        for t in tasks:
            body_lines.append(f"- {t}")
        body_lines.append("")
    else:
        body_lines.append("No explicit Sir Green tasks found in tasklist.")
        body_lines.append("")
    
    body_lines.extend([
        "## Your Action Items",
        "",
        "1. Acknowledge this auto-prompt with your current status",
        "2. Report progress on highest-priority unfinished task",
        "3. Identify blockers or missing inputs",
        "4. Request Captain support if needed",
        "",
        "## Reply Format",
        "",
        "Reply with topic `status` or `ops` and include:",
        "- Completed items since last prompt",
        "- Current task in progress",
        "- Blockers or missing inputs",
        "- Next expected completion",
        "",
        "## Security Notes",
        "- Do NOT transmit secrets in plaintext",
        "- Use secure handoff protocol for credentials",
        "- Escalate to Captain if human action required",
    ])
    
    body = "\n".join(body_lines)
    
    return {
        "id": msg_id,
        "topic": "ops",
        "body": body,
        "timestamp": now_iso(),
    }


def write_message(msg: dict) -> Path:
    """Write prompt message to outbox."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    ts = now_stamp()
    filename = f"{ts}_sirgreen_{msg['topic']}_{msg['id']}.msg.md"
    path = OUTBOX / filename
    
    content = f"""---
from: sirgreen
to: misspink
topic: {msg['topic']}
id: {msg['id']}
requires_response: true
action_required: false
---
{msg['body']}
"""
    path.write_text(content, encoding="utf-8")
    return path


def main():
    tasklist_text = read_file(TASKLIST)
    docker_text = read_file(DOCKER_PROMPT)
    
    tasks = extract_sirgreen_tasks(tasklist_text)
    if not tasks:
        # Fallback to Docker-specific tasks
        tasks = [
            "Verify torus-accounting Docker service",
            "Test Gmail send scope fix",
            "Confirm backup host path",
            "Create Discord webhook",
        ]
    
    msg = build_prompt_message(tasks)
    path = write_message(msg)
    print(f"Generated auto-prompt: {path}")
    print(f"Pending tasks: {len(tasks)}")


if __name__ == "__main__":
    main()
