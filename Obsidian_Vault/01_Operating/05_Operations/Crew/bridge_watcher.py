#!/usr/bin/env python3
"""
Bridge watcher for Torus Coffee Company ops.
Watches PINKCADY_INBOX, auto-replies to Sir Green ops prompts,
and logs activity. Run from PINKCADY.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

INBOX = Path(r"Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX")
OUTBOX = Path(r"D:\Work\Torus Coffee Company LLC\02_Business_Operations\Communications\Outbox")
LOG = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\bridge_watcher.log")
STATE = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\.sirgreen_inbox_state.json")
SHARED_BUS = OUTBOX / "SHARED_COMMS_BUS.json"

TOPICS = ["DASHBOARD", "GITHUB", "HEALING", "SECURITY"]

def log(msg: str):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text(
            LOG.read_text() if LOG.exists() else ""
            + f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def atomic_write(path: Path, content: str) -> None:
    try:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        path.replace(tmp)
    except Exception:
        pass

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def build_reply(topic: str, msg_id: str, ts: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""---
from: misspink
to: sirgreen
topic: {topic.lower()}
id: RE_{msg_id}
requires_response: true
action_required: true
ts: {now}
reply_to: {msg_id}
---

Auto-reply received {topic} OODA prompt {msg_id}.
Status: queued for execution.
If secrets/credentials required, please supply.

"""


def update_shared_bus(reply_name: str, topic: str, msg_id: str, body: str) -> None:
    try:
        OUTBOX.mkdir(parents=True, exist_ok=True)
        entry = {
            "from": "misspink",
            "to": "sirgreen",
            "topic": topic.lower(),
            "id": reply_name,
            "reply_to": msg_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "body": body.strip(),
            "source": "bridge_watcher",
        }
        bus = {"last_updated": entry["ts"], "entries": [entry]}
        if SHARED_BUS.exists():
            try:
                existing = json.loads(SHARED_BUS.read_text(encoding="utf-8"))
                if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
                    existing.setdefault("entries", []).append(entry)
                    existing["last_updated"] = entry["ts"]
                    bus = existing
            except Exception:
                pass
        atomic_write(SHARED_BUS, json.dumps(bus, indent=2))
        log(f"SHARED_BUS_WRITE {SHARED_BUS}")
    except Exception as exc:
        log(f"SHARED_BUS_FAIL {exc}")

def process_inbox(state):
    files = sorted(INBOX.glob("*.msg.md"))
    new_files = [f for f in files if f.name not in state.get("processed", {})]
    for path in new_files:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "from: sirgreen" not in text or "to: misspink" not in text:
            state.setdefault("processed", {})[path.name] = {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "skipped",
            }
            continue
        if path.name.startswith("RE_") or path.name.startswith("AUTO_") or "_misspink" in path.name:
            state.setdefault("processed", {})[path.name] = {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "skipped",
            }
            continue

        topic = "UNKNOWN"
        msg_id = path.stem
        ts = datetime.now(timezone.utc).isoformat()
        for line in text.splitlines():
            if line.startswith("topic:"):
                topic = line.split(":", 1)[1].strip()
            if line.startswith("id:"):
                msg_id = line.split(":", 1)[1].strip()
            if line.startswith("ts:"):
                ts = line.split(":", 1)[1].strip()

        reply = build_reply(topic, msg_id, ts)
        reply_name = f"RE_{msg_id}_misspink.msg.md"
        reply_path = OUTBOX / reply_name
        try:
            atomic_write(reply_path, reply)
            log(f"replied {path.name} -> {reply_path.name}")
            update_shared_bus(reply_name, topic, msg_id, reply)
            state.setdefault("processed", {})[path.name] = {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "replied",
                "reply": reply_name,
            }
        except Exception as e:
            log(f"reply_failed {path.name}: {e}")

def run_once():
    state = load_state()
    process_inbox(state)
    save_state(state)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
        return
    while True:
        try:
            run_once()
        except Exception as e:
            log(f"loop_error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()
