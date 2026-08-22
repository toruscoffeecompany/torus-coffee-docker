#!/usr/bin/env python3
"""
Miss Pink Auto-Prompt Generator — Torus Coffee Company
Generates self-prompting messages for Sir Green based on vault goals and OODA tasklist.
Runs as scheduled task/daemon.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
TASKLIST = VAULT / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
AUTOMATION_STATUS = VAULT / "08_Reports/Automation_Status_Report_2026-08-03.md"
GIT_LOG = VAULT / "08_Reports/git_log.txt"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def get_last_commit() -> str:
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--oneline"],
            cwd=VAULT,
            text=True,
            encoding="utf-8",
            errors="ignore",
        ).strip()
        return out
    except Exception:
        return "UNKNOWN"


def extract_pending_tasks(tasklist_text: str) -> list:
    """Extract pending unblocked tasks from unified backlog or markdown tasklist."""
    tasks = []
    current_priority = "P1"
    in_unified = False
    for line in tasklist_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## P0"):
            in_unified = True
            current_priority = "P0"
        elif stripped.startswith("## P1"):
            in_unified = True
            current_priority = "P1"
        elif stripped.startswith("## P2"):
            in_unified = True
            current_priority = "P2"
        elif stripped.startswith("## P3"):
            in_unified = True
            current_priority = "P3"
        elif stripped.startswith("## P4"):
            in_unified = True
            current_priority = "P4"
        elif in_unified and stripped.startswith("---"):
            in_unified = False

        if in_unified and line.startswith("- `⏳`"):
            task_text = line.replace("- `⏳`", "").strip()
            if not task_text.startswith(("P0.", "P1.", "P2.", "P3.", "P4.")):
                task_text = f"{current_priority}. {task_text}"
            tasks.append(task_text)
        elif line.startswith("- [ ] "):
            task_text = line.replace("- [ ] ", "").strip()
            if not task_text.startswith(("P0.", "P1.", "P2.", "P3.", "P4.")):
                task_text = f"{current_priority}. {task_text}"
            tasks.append(task_text)
    return tasks


def build_prompt_message(tasks: list, last_commit: str) -> dict:
    """Build a self-prompt message for Sir Green."""
    ts = now_stamp()
    msg_id = f"auto_{ts}"

    # Extract priorities from task text if present, otherwise default to P1
    p0, p1, p2, p3 = [], [], [], []
    for t in tasks:
        if t.startswith("P0."):
            p0.append(t)
        elif t.startswith("P1."):
            p1.append(t)
        elif t.startswith("P2."):
            p2.append(t)
        elif t.startswith("P3."):
            p3.append(t)
        else:
            p1.append(t)

    body_lines = [
        "# Auto-Prompt: Torus Coffee Automation Goals",
        "",
        f"Generated: {now_iso()}",
        f"Last commit: {last_commit}",
        "",
        "## Current Focus",
        "",
    ]

    if p0:
        body_lines.append("### P0 — Do Today")
        for t in p0:
            body_lines.append(f"- {t}")
        body_lines.append("")

    if p1:
        body_lines.append("### P1 — This Week")
        for t in p1[:8]:
            body_lines.append(f"- {t}")
        body_lines.append("")

    if p2:
        body_lines.append("### P2 — Next Week")
        for t in p2[:8]:
            body_lines.append(f"- {t}")
        body_lines.append("")

    if p3:
        body_lines.append("### P3 — Ongoing")
        for t in p3[:8]:
            body_lines.append(f"- {t}")
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
    filename = f"{ts}_misspink_{msg['topic']}_{msg['id']}.msg.md"
    path = OUTBOX / filename
    
    content = f"""---
from: misspink
to: sirgreen
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
    automation_text = read_file(AUTOMATION_STATUS)
    last_commit = get_last_commit()
    
    tasks = extract_pending_tasks(tasklist_text)
    if not tasks:
        print("No pending tasks found")
        return
    
    msg = build_prompt_message(tasks, last_commit)
    path = write_message(msg)
    print(f"Generated auto-prompt: {path}")
    print(f"Pending tasks: {len(tasks)}")
    p0 = [t for t in tasks if t.startswith("P0.")]
    p1 = [t for t in tasks if t.startswith("P1.")]
    p2 = [t for t in tasks if t.startswith("P2.")]
    p3 = [t for t in tasks if t.startswith("P3.")]
    print(f"P0: {len(p0)}")
    print(f"P1: {len(p1)}")
    print(f"P2: {len(p2)}")
    print(f"P3: {len(p3)}")


if __name__ == "__main__":
    main()
