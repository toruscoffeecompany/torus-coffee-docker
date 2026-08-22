#!/usr/bin/env python3
"""Background high-priority OODA loop."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG = VAULT / "10_Skills_Library/05_Operations/logs/high_priority_ooda_loop.log"
TASKLIST = VAULT / "10_Skills_Library/05_Operations/HIGH_PRIORITY_TASKLIST.json"
WORKER = VAULT / "10_Skills_Library/05_Operations/scripts/continuous_ooda_worker.py"
PYTHON = VAULT / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_tasklist() -> list:
    if TASKLIST.exists():
        try:
            data = json.loads(TASKLIST.read_text(encoding="utf-8"))
            return data.get("items", [])
        except json.JSONDecodeError:
            pass
    return []


def save_tasklist(items: list) -> None:
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(items),
        "items": items,
    }
    TASKLIST.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    log("HIGH_PRIORITY_OODA_LOOP_START")
    items = load_tasklist()
    total = len(items)
    log(f"Loaded {total} high-priority cards")

    processed = 0
    for idx, item in enumerate(items, 1):
        card_id = item.get("id")
        if not card_id:
            continue

        log(f"Processing {idx}/{total}: {card_id} {item.get('name','')[:60]}")
        try:
            p = subprocess.run(
                [str(PYTHON), str(WORKER)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = (p.stdout or "") + (p.stderr or "")
            lines = [ln for ln in out.splitlines() if ln.strip()]
            marker = next(
                (
                    ln
                    for ln in reversed(lines)
                    if any(k in ln for k in ["TRELLO_STATUS_UPDATED", "GITHUB_STATUS_UPDATED", "PROMOTED_TO_TOP10", "DOWNGRADED", "CONTINUOUS_OODA_WORKER_COMPLETE"])
                ),
                "NO_OUTPUT",
            )
            log(f"  Result: {marker}")
            if p.returncode != 0:
                log(f"  WARN: worker exited {p.returncode}")
        except subprocess.TimeoutExpired:
            log("  TIMEOUT after 120s")
        except Exception as e:
            log(f"  ERROR: {type(e).__name__}: {e}")

        processed += 1
        if processed % 10 == 0:
            log(f"Progress: {processed}/{total}")
            # Refresh tasklist in case counts changed
            items = load_tasklist()
            total = len(items)

    log(f"HIGH_PRIORITY_OODA_LOOP_COMPLETE processed={processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
