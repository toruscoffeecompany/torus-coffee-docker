#!/usr/bin/env python3
"""
Torus Coffee Company — OODA Self-Prompting Loop
Runs watcher + auto-prompts + backlog updates in one process.
If Sir Green does not respond, Miss Pink continues with unblocked work.
"""
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
STATE_FILE = VAULT / "10_Skills_Library/05_Operations/Crew/.pinkcady_comms_state.json"
LOG_FILE = VAULT / "10_Skills_Library/05_Operations/Crew/pinkcady_comms.log"
BACKLOG = VAULT / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
PYTHON = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def log(msg: str) -> None:
    line = f"[{now_iso()}] {msg}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def get_last_commit() -> str:
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


def extract_unified_tasks(backlog_text: str) -> dict:
    """Extract task counts from unified backlog."""
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "P4": 0, "total": 0}
    for line in backlog_text.splitlines():
        if line.startswith("- `⏳`") or line.startswith("- `🔄`") or line.startswith("- `🚫`"):
            counts["total"] += 1
            for p in ["P0", "P1", "P2", "P3", "P4"]:
                if f"**{p}**" in line or line.startswith(f"- `⏳` {p}"):
                    counts[p] += 1
    return counts


def build_ooda_prompt() -> dict:
    """Build a self-prompt message for the next unblocked item."""
    backlog_text = read_file(BACKLOG)
    counts = extract_unified_tasks(backlog_text)
    last_commit = get_last_commit()
    ts = now_stamp()
    msg_id = f"ooda_{ts}"

    body_lines = [
        "# OODA Self-Prompt: Torus Coffee Automation Loop",
        "",
        f"Generated: {now_iso()}",
        f"Last commit: {last_commit}",
        "",
        "## Current Priority Stack",
        "",
        f"- P0: {counts['P0']} items",
        f"- P1: {counts['P1']} items",
        f"- P2: {counts['P2']} items",
        f"- P3: {counts['P3']} items",
        f"- P4: {counts['P4']} items",
        f"- Total unblocked: {counts['total']}",
        "",
        "## Next Unblocked Actions",
        "",
        "1. **Contact/wholesale form backend** — add API endpoint",
        "2. **Square links** — Captain must create in Square dashboard",
        "3. **Social accounts** — Substack, YouTube, Discord",
        "4. **Alerts** — Discord webhook, Gmail app password",
        "5. **API layer** — connect website to local DB",
        "",
        "## If Sir Green is Silent",
        "",
        "Miss Pink will continue executing unblocked items autonomously.",
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
    ]

    body = "\n".join(body_lines)

    return {
        "id": msg_id,
        "topic": "ooda-loop",
        "body": body,
        "timestamp": now_iso(),
    }


def write_message(msg: dict, recipient: str) -> Path:
    """Write prompt message to outbox and shared comms bus."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    ts = now_stamp()
    filename = f"{ts}_misspink_{msg['topic']}_{msg['id']}.msg.md"
    path = OUTBOX / filename

    content = f"""---
from: misspink
to: {recipient}
topic: {msg['topic']}
id: {msg['id']}
requires_response: true
action_required: false
---
{msg['body']}
"""
    path.write_text(content, encoding="utf-8")
    try:
        update_shared_bus(
            {"id": msg["id"], "from": "misspink"},
            msg["topic"],
            msg["body"],
        )
    except Exception as exc:
        log(f"SHARED_BUS_FAIL {exc}")
    return path


def update_shared_bus(meta: dict, topic: str, body: str) -> None:
    try:
        OUTBOX.mkdir(parents=True, exist_ok=True)
        bus_path = OUTBOX / "SHARED_COMMS_BUS.json"
        entry = {
            "from": "misspink",
            "to": meta.get("from", "sirgreen"),
            "topic": topic,
            "id": meta.get("id", ""),
            "reply_to": meta.get("id", ""),
            "ts": now_iso(),
            "body": body.strip(),
            "source": "ooda_self_prompt_loop",
        }
        bus = {"last_updated": now_iso(), "entries": [entry]}
        if bus_path.exists():
            try:
                existing = json.loads(bus_path.read_text(encoding="utf-8"))
                if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
                    existing.setdefault("entries", []).append(entry)
                    existing["last_updated"] = now_iso()
                    bus = existing
            except Exception:
                pass
        bus_path.write_text(json.dumps(bus, indent=2), encoding="utf-8")
        log(f"SHARED_BUS_WRITE {bus_path}")
    except Exception as exc:
        log(f"SHARED_BUS_FAIL {exc}")


def run_auto_prompts() -> tuple:
    """Run both auto-prompt generators."""
    results = []
    for name, script in [
        ("misspink", VAULT / "10_Skills_Library/05_Operations/scripts/misspink_auto_prompt.py"),
        ("sirgreen", VAULT / "10_Skills_Library/05_Operations/scripts/sirgreen_auto_prompt.py"),
    ]:
        try:
            out = subprocess.check_output(
                [str(PYTHON), str(script)],
                cwd=VAULT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            ).strip()
            results.append((name, out))
        except Exception as exc:
            results.append((name, f"FAIL: {exc}"))
    return results


def main() -> None:
    log("OODA Self-Prompting Loop starting...")

    # Observe: refresh unified backlog from Trello before each loop cycle
    try:
        backlog_script = VAULT / "10_Skills_Library/05_Operations/scripts/build_unified_backlog.py"
        if backlog_script.exists():
            subprocess.check_output(
                [str(PYTHON), str(backlog_script)],
                cwd=VAULT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            log("BACKLOG_REFRESH_OK")
    except Exception as exc:
        log(f"BACKLOG_REFRESH_FAIL {exc}")

    # Observe: reference cross-business master tasklist for priority context
    master_tasklist = VAULT / "10_Skills_Library/05_Operations/MASTER_OODA_TASKLIST.md"
    if master_tasklist.exists():
        log(f"MASTER_OODA_TASKLIST_OK {master_tasklist.stat().st_size} bytes")

    # Observe: run auto-prompts
    results = run_auto_prompts()
    for name, out in results:
        log(f"AUTO_PROMPT_{name.upper()}: {out[:120]}")

    # Generate OODA loop prompt
    msg = build_ooda_prompt()
    path = write_message(msg, "sirgreen")
    log(f"OODA_PROMPT_WRITE {path}")

    # Update state
    try:
        state = {}
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        state.setdefault("last_ooda_loop", {})[msg["id"]] = time.time()
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as exc:
        log(f"STATE_SAVE_FAIL {exc}")

    log("OODA Self-Prompting Loop cycle complete.")


if __name__ == "__main__":
    main()
