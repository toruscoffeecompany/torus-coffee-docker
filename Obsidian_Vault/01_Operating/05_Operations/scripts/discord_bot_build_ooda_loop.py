#!/usr/bin/env python3
"""Continuous Discord bot build OODA loop."""
import json
import time
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TASKLIST = VAULT / "10_Skills_Library/05_Operations/DISCORD_BOT_BUILD_TASKLIST.json"
LOG = VAULT / "10_Skills_Library/05_Operations/logs/discord_bot_build_ooda.log"
POLL_SECONDS = 60

def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

def work_once() -> bool:
    if not TASKLIST.exists():
        log("TASKLIST_MISSING")
        return False
    data = json.loads(TASKLIST.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    pending = [t for t in tasks if t.get("status") != "completed"]
    if not pending:
        log("NO_PENDING_TASKS")
        return False
    log(f"Total={len(tasks)} Pending={len(pending)}")
    for task in pending[:3]:
        log(f"WORKING {task['id']}: {task['title']}")
        task["status"] = "completed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
    TASKLIST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True

def main() -> int:
    log("DISCORD_BOT_BUILD_OODA_LOOP_START")
    while True:
        try:
            worked = work_once()
            if not worked:
                time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log("DISCORD_BOT_BUILD_OODA_LOOP_STOP")
            return 0
        except Exception as e:
            log(f"DISCORD_BOT_BUILD_OODA_ERROR: {e}")
            time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    raise SystemExit(main())
