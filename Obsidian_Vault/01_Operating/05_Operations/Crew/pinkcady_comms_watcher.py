#!/usr/bin/env python3
"""
Pinkcady Comms Watcher — Torus Coffee Company
Local-network mailbox watcher for Miss Pink <-> Sir Green.
Watches Shared_With_Pink inboxes, acts on new messages, writes auto-replies.
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

SHARED = Path(r"Z:\Developer_Brain\Shared_With_Pink")
PINK_INBOX = SHARED / "PINKCADY_INBOX"
GREEN_INBOX = SHARED / "SIR_GREEN_INBOX"
LOCAL_STATE = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\.pinkcady_comms_state.json")
LOCAL_LOG = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\pinkcady_comms.log")
LOCAL_OUTBOX = Path(r"D:\Work\Torus Coffee Company LLC\02_Business_Operations\Communications\Outbox")
LOCAL_ARCHIVE = Path(r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\comms_archive")
SHARED_BUS = LOCAL_OUTBOX / "SHARED_COMMS_BUS.json"

STATE_FILE = LOCAL_STATE
LOG_FILE = LOCAL_LOG
SCAN_LOG_EVERY = 60
INSTANCE_LOCK = LOCAL_STATE.parent / ".pinkcady_comms_watcher.lock"


def acquire_instance_lock() -> bool:
    try:
        if INSTANCE_LOCK.exists():
            return False
        INSTANCE_LOCK.write_text("locked", encoding="utf-8")
        return True
    except Exception:
        return False


def release_instance_lock() -> None:
    try:
        INSTANCE_LOCK.unlink(missing_ok=True)
    except Exception:
        pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{now_iso()}] {msg}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"last_green": {}, "last_pink": {}}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as exc:
        log(f"STATE_SAVE_FAIL {exc}")


def parse_frontmatter(text: str) -> dict:
    if yaml is None:
        return {}
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("---", 3)
        block = text[3:end].strip()
        return yaml.safe_load(block) or {}
    except Exception:
        return {}


def read_message(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        body = text.split("---", 2)[-1].strip() if "---" in text else text
        return meta, body
    except Exception as exc:
        log(f"READ_FAIL {path}: {exc}")
        return {}, ""


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(str(tmp), str(path))


def move_to_archive(msg_path: Path, subfolder: str = "archive") -> None:
    target_dir = LOCAL_ARCHIVE / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / msg_path.name
    try:
        os.replace(str(msg_path), str(target))
        log(f"ARCHIVED {msg_path.name} -> {target}")
    except Exception as exc:
        log(f"ARCHIVE_FAIL {msg_path}: {exc}")


def write_reply(original_name: str, topic: str, body: str, meta: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reply_name = f"RE_{ts}_misspink_{topic}_{meta.get('id','unknown')}.msg.md"
    fm = {
        "from": "misspink",
        "to": meta.get("from", "*"),
        "topic": topic,
        "id": meta.get("id", reply_name),
        "reply_to": original_name,
        "requires_response": False,
        "action_required": False,
        "ts": now_iso(),
    }
    if yaml is not None:
        content = "---\n" + yaml.dump(fm, sort_keys=False) + "---\n\n" + body.strip() + "\n"
    else:
        content = "---\nfrom: misspink\n---\n\n" + body.strip() + "\n"
    try:
        LOCAL_OUTBOX.mkdir(parents=True, exist_ok=True)
        reply_path = LOCAL_OUTBOX / reply_name
        atomic_write(reply_path, content)
        log(f"REPLY_WRITE {reply_path}")
    except Exception as exc:
        log(f"REPLY_FAIL {exc}")


def update_shared_bus(meta: dict, topic: str, body: str) -> None:
    try:
        LOCAL_OUTBOX.mkdir(parents=True, exist_ok=True)
        entry = {
            "from": "misspink",
            "to": meta.get("from", "sirgreen"),
            "topic": topic,
            "id": meta.get("id", ""),
            "reply_to": meta.get("id", ""),
            "ts": now_iso(),
            "body": body.strip(),
            "source": "pinkcady_comms_watcher",
        }
        bus = {"last_updated": now_iso(), "entries": [entry]}
        if SHARED_BUS.exists():
            try:
                existing = json.loads(SHARED_BUS.read_text(encoding="utf-8"))
                if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
                    existing.setdefault("entries", []).append(entry)
                    existing["last_updated"] = now_iso()
                    bus = existing
            except Exception:
                pass
        atomic_write(SHARED_BUS, json.dumps(bus, indent=2))
        log(f"SHARED_BUS_WRITE {SHARED_BUS}")
    except Exception as exc:
        log(f"SHARED_BUS_FAIL {exc}")


def handle_status(meta: dict, body: str) -> None:
    log(f"STATUS from={meta.get('from')} topic={meta.get('topic')}")
    reply = (
        "PINKCADY status: watcher active, vault accessible at D:\\Work\\Torus Coffee Company LLC, "
        "comms bridge read-only via Z:\\Developer_Brain\\Shared_With_Pink."
    )
    write_reply(meta.get("id", ""), "status", reply, meta)
    update_shared_bus(meta, "status", reply)


def handle_vault(meta: dict, body: str) -> None:
    log(f"VAULT from={meta.get('from')} body={body[:120]}")
    reply = "Vault path confirmed. Local vault is source of truth. Git remote: toruscoffeecompany/Torus_Ops."
    write_reply(meta.get("id", ""), "vault", reply, meta)
    update_shared_bus(meta, "vault", reply)


def handle_alert_router(meta: dict, body: str) -> None:
    log(f"ALERT_ROUTER from={meta.get('from')} body={body[:120]}")
    reply = "Alert router acknowledged. Known issues: Gmail send scope invalid; Trello creds need rotation. See VAULT_AUDIT_2026-08-04.md."
    write_reply(meta.get("id", ""), "alert-router", reply, meta)
    update_shared_bus(meta, "alert-router", reply)


def handle_backup(meta: dict, body: str) -> None:
    log(f"BACKUP from={meta.get('from')} body={body[:120]}")
    reply = "Backup path accepted. Current backup target is Torus_Ops GitHub mirror via vault_sync_to_github.py."
    write_reply(meta.get("id", ""), "backup", reply, meta)
    update_shared_bus(meta, "backup", reply)


def handle_secret(meta: dict, body: str) -> None:
    log(f"SECRET from={meta.get('from')} action_required={meta.get('action_required')}")
    reply = "Secret handoff requires secure channel. Do not pass secrets in plaintext. Use Captain passoff or approved credentials file."
    write_reply(meta.get("id", ""), "secret", reply, meta)
    update_shared_bus(meta, "secret", reply)


def handle_error(meta: dict, body: str) -> None:
    log(f"ERROR from={meta.get('from')} body={body[:200]}")
    reply = "Error received. If recovery hint is present, execute it. Otherwise escalate to Captain."
    write_reply(meta.get("id", ""), "ops", reply, meta)
    update_shared_bus(meta, "ops", reply)


def handle_ops(meta: dict, body: str) -> None:
    log(f"OPS from={meta.get('from')} body={body[:120]}")
    reply_body = (
        "Ops loop received. "
        "Next asks: Square links, contact/wholesale flow, social account progress, "
        "and any blockers that do not require secrets. "
        "If you need secrets, reply with topic=secret and I will route to Captain."
    )
    write_reply(meta.get("id", ""), "ops", reply_body, meta)
    update_shared_bus(meta, "ops", reply_body)


HANDLERS = {
    "status": handle_status,
    "vault": handle_vault,
    "alert-router": handle_alert_router,
    "backup": handle_backup,
    "secret": handle_secret,
    "error": handle_error,
    "ops": handle_ops,
}


def process_inbox(inbox: Path, state: dict, state_key: str) -> None:
    if not inbox.exists():
        log(f"MISSING_INBOX {inbox}")
        return
    files = sorted(inbox.glob("*.msg.md"))
    seen = 0
    changed = 0
    skipped_auto = 0
    for path in files:
        seen += 1
        if path.name.startswith("AUTO_") or "AUTO_CYCLE" in path.name or path.name.startswith("RE_") or "_misspink" in path.name:
            skipped_auto += 1
            continue
        mtime = path.stat().st_mtime
        known = state.get(state_key, {}).get(path.name)
        if known and mtime == known:
            continue
        try:
            meta, body = read_message(path)
            topic = meta.get("topic", "ops")
            handler = HANDLERS.get(topic, handle_ops)
            handler(meta, body)
            if inbox != GREEN_INBOX:
                move_to_archive(path, subfolder="archive")
            state.setdefault(state_key, {})[path.name] = mtime
            changed += 1
        except Exception as exc:
            log(f"PROCESS_FAIL {path}: {exc}")
    if seen:
        log(f"INBOX_SCAN {inbox} files={seen} auto_skipped={skipped_auto} changed={changed}")


if __name__ == "__main__":
    if not acquire_instance_lock():
        log("WATCHER_ALREADY_RUNNING")
        raise SystemExit(0)
    try:
        log("Pinkcady Comms Watcher starting...")
        state = load_state()
        while True:
            try:
                process_inbox(PINK_INBOX, state, "last_pink")
                save_state(state)
                process_inbox(GREEN_INBOX, state, "last_green")
                save_state(state)
            except KeyboardInterrupt:
                log("Shutting down...")
                break
            except Exception as exc:
                log(f"ERROR {exc}")
            time.sleep(SCAN_LOG_EVERY)
    finally:
        release_instance_lock()
