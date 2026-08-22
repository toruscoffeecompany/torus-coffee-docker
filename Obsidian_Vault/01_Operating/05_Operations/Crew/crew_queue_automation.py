#!/usr/bin/env python3
"""
Crew queue bridge: Torus_Ops crew queues -> crew notification -> VOID Ops card creation.
Closed-loop workflow:
- New queue cards: notify crew via local outbox bridge
- Crew moves card out of queue in Torus_Ops: create mirrored card on VOID Ops
- Track all transfers in CREW_QUEUE_TRANSFER_LOG.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

VAULT = Path(os.environ.get("TORUS_VAULT", r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault"))
SCRIPT_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "Crew"
STATE_FILE = SCRIPT_DIR / "CREW_QUEUE_STATE.json"
TRANSFER_LOG = VAULT / "10_Skills_Library" / "05_Operations" / "CREW_QUEUE_TRANSFER_LOG.json"
CONFIG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "crew_queue_config.json"
CRED_FILE = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
OUTBOX = VAULT / "02_Business_Operations" / "Communications" / "Outbox"

DEFAULT_CONFIG = {
    "source_board": "Torus_Ops",
    "source_lists": ["Sir Green's Queue", "Sir Azure's Queue"],
    "routes": {
        "Sir Green": {
            "member_username": "sirgreen",
            "to": "sirgreen",
            "source_list": "Sir Green's Queue",
            "destination_list": "Sir Green's Queue",
            "destination_board": "VOID Ops",
            "ack_required": True,
        },
        "Sir Azure": {
            "member_username": "sirazure",
            "to": "sirazure",
            "source_list": "Sir Azure's Queue",
            "destination_list": "Sir Azure's Queue",
            "destination_board": "VOID Ops",
            "ack_required": True,
        },
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, default=str)
    for attempt in range(5):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except OSError:
            if attempt < 4:
                time.sleep(0.2 * (attempt + 1))
            else:
                raise


def load_trello_creds() -> tuple[str, str]:
    text = CRED_FILE.read_text(errors="ignore")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello API credentials missing")
    return api_key, token


def trello_get(url: str, params: dict, api_key: str, token: str):
    p = {"key": api_key, "token": token}
    p.update(params or {})
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def trello_post(url: str, data: dict, api_key: str, token: str):
    d = {"key": api_key, "token": token}
    d.update(data or {})
    r = requests.post(url, data=d, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Trello POST failed: {r.status_code} {r.text[:200]}")
    return r.json()


def trello_put(url: str, data: dict, api_key: str, token: str):
    d = {"key": api_key, "token": token}
    d.update(data or {})
    r = requests.put(url, data=d, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Trello PUT failed: {r.status_code} {r.text[:200]}")
    return r.json()


def find_board_id(api_key: str, token: str, board_name: str) -> str:
    boards = trello_get("https://api.trello.com/1/members/me/boards", {"fields": "name"}, api_key, token)
    match = next((b["id"] for b in boards if b["name"] == board_name), None)
    if not match:
        raise RuntimeError(f"Board not found: {board_name}")
    return match


def find_list_id(api_key: str, token: str, board_id: str, list_name: str) -> str:
    lists = trello_get(f"https://api.trello.com/1/boards/{board_id}/lists", {"fields": "name"}, api_key, token)
    match = next((l["id"] for l in lists if l["name"] == list_name), None)
    if not match:
        raise RuntimeError(f"List not found on board {board_id}: {list_name}")
    return match


def ensure_list(api_key: str, token: str, board_id: str, list_name: str) -> str:
    try:
        return find_list_id(api_key, token, board_id, list_name)
    except RuntimeError:
        created = trello_post(
            "https://api.trello.com/1/boards/{board_id}/lists".replace("{board_id}", board_id),
            {"name": list_name, "pos": "bottom"},
            api_key,
            token,
        )
        return created["id"]


def move_card(api_key: str, token: str, card_id: str, list_id: str) -> None:
    trello_put(
        f"https://api.trello.com/1/cards/{card_id}",
        {"idList": list_id},
        api_key,
        token,
    )


def append_card_comment(api_key: str, token: str, card_id: str, text: str) -> None:
    trello_post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        {"text": text},
        api_key,
        token,
    )


def find_existing_card_by_name(api_key: str, token: str, board_id: str, name: str) -> str | None:
    """Check if a card with the given name already exists on the board (open)."""
    try:
        cards = trello_get(
            f"https://api.trello.com/1/boards/{board_id}/cards",
            {"fields": "id,name,closed"},
            api_key, token,
        )
        for c in cards:
            if c.get("name") == name and not c.get("closed", False):
                return c["id"]
    except Exception:
        pass
    return None


def create_void_card(api_key: str, token: str, board_id: str, list_id: str, card: dict) -> dict:
    name = card.get("name") or "Crew Task"
    # ANTI-DUPLICATION: check if card with same name already exists on destination board
    existing_id = find_existing_card_by_name(api_key, token, board_id, name)
    if existing_id:
        return {"id": existing_id, "name": name, "duplicate_skipped": True}
    desc = card.get("desc") or ""
    desc += f"\n\nSynced from Torus_Ops: {card.get('url','')}\nAuto-created by crew queue automation."
    return trello_post(
        "https://api.trello.com/1/cards",
        {"idBoard": board_id, "idList": list_id, "name": name, "desc": desc},
        api_key,
        token,
    )


def write_crew_notification(crew: str, list_name: str, cards: list[dict]) -> Path:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    msg_id = f"queue-{crew.lower()}-{now}"
    lines = [
        "---",
        f"from: misspink",
        f"to: {crew.lower()}",
        "topic: queue-notify",
        f"id: {msg_id}",
        "requires_response: true",
        "action_required: true",
        f"ts: {now}",
        "---",
        "",
        f"Action required: connect to Torus_Ops -> {list_name}.",
        "",
        f"Pending cards: {len(cards)}",
    ]
    for c in cards[:20]:
        lines.append(f"- {c.get('name','')} | {c.get('url','')}")
    if len(cards) > 20:
        lines.append(f"- ... and {len(cards)-20} more")
    lines.extend([
        "",
        "Please:",
        "1. Open Torus_Ops",
        "2. Read assigned cards in your queue",
        "3. Move cards to your destination list",
        "4. Update card status/comments",
        "",
        "This is automated crew ops messaging. Reply with 'ACK' when connected.",
    ])
    out_path = OUTBOX / f"{msg_id}.msg.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def log_transfer(record: dict) -> None:
    data = load_json(TRANSFER_LOG, {"entries": []})
    data.setdefault("entries", []).append(record)
    data["last_updated"] = now_iso()
    save_json(TRANSFER_LOG, data)


def run() -> dict:
    # Crew coordination: claim queue sync lock to prevent concurrent execution across rigs
    lock_acquired = False
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from crew_coordination import claim_work_item, release_work_item
        lock_acquired = claim_work_item("crew_queue_sync", "misspink", "Crew queue synchronization batch processing")
    except ImportError:
        pass
    if not lock_acquired:
        return {"result": {"notifications": 0, "processed": 0, "processed_count": 0, "failed": [{"error": "lock held by another rig"}], "skipped": True}}

    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    if not config:
        config = DEFAULT_CONFIG
        save_json(CONFIG_FILE, config)
    api_key, token = load_trello_creds()
    source_board_id = find_board_id(api_key, token, config["source_board"])

    previous_state = load_json(STATE_FILE, {"queue_cards": {}, "last_run": None})
    previous_queue: dict[str, str] = previous_state.get("queue_cards", {})

    current_queue: dict[str, dict] = {}
    processed = []
    failed = []
    notifications = []

    for list_name in config["source_lists"]:
        try:
            list_id = find_list_id(api_key, token, source_board_id, list_name)
        except Exception as exc:
            failed.append({"list": list_name, "error": str(exc)})
            continue

        try:
            cards = trello_get(
                f"https://api.trello.com/1/lists/{list_id}/cards",
                {"fields": "name,id,url,desc,dateLastActivity"},
                api_key, token,
            )
        except Exception as exc:
            failed.append({"list": list_name, "error": str(exc)})
            continue

        crew = None
        if "Green" in list_name:
            crew = "Sir Green"
        elif "Azure" in list_name:
            crew = "Sir Azure"
        if not crew:
            continue

        route = (config.get("routes", {}) or {}).get(crew)
        if not route:
            failed.append({"list": list_name, "error": "no route for crew"})
            continue

        current_ids = {c["id"]: c for c in cards}
        current_queue.update({cid: {"crew": crew, "list": list_name, "card": c} for cid, c in current_ids.items()})

        new_cards = [c for cid, c in current_ids.items() if cid not in previous_queue]
        if new_cards:
            path = write_crew_notification(crew, list_name, new_cards)
            notifications.append({"crew": crew, "path": str(path), "count": len(new_cards)})

        moved_ids = [cid for cid, data in previous_queue.items() if cid not in current_ids and data.get("crew") == crew]
        if not moved_ids:
            continue

        dest_board_id = None
        dest_list_id = None
        try:
            dest_board_id = find_board_id(api_key, token, route["destination_board"])
            dest_list_id = ensure_list(api_key, token, dest_board_id, route["destination_list"])
        except Exception as exc:
            failed.append({"list": list_name, "error": f"destination setup failed: {exc}"})
            continue

        for cid in moved_ids:
            card = previous_queue[cid]
            try:
                void_card = create_void_card(api_key, token, dest_board_id, dest_list_id, card)
                if void_card.get("duplicate_skipped"):
                    continue  # Skip notification for duplicates
                log_transfer({
                    "ts": now_iso(),
                    "crew": crew,
                    "card_id": cid,
                    "card_name": card.get("name"),
                    "from_list": list_name,
                    "to_list": route["destination_list"],
                    "to_board": route["destination_board"],
                    "void_card_id": void_card.get("id"),
                    "status": "transferred",
                })
                processed.append({
                    "crew": crew,
                    "card_id": cid,
                    "card_name": card.get("name"),
                    "to_list": route["destination_list"],
                    "to_board": route["destination_board"],
                })
            except Exception as exc:
                failed.append({"list": list_name, "card_id": cid, "error": str(exc)})

    state = {
        "last_run": now_iso(),
        "queue_cards": {cid: {"crew": v["crew"], "list": v["list"], "name": v["card"].get("name"), "url": v["card"].get("url")} for cid, v in current_queue.items()},
        "processed_count": len(processed) + previous_state.get("processed_count", 0),
        "failed_count": len(failed) + previous_state.get("failed_count", 0),
        "processed": processed,
        "failed": failed,
        "notifications": notifications,
    }
    save_json(STATE_FILE, state)

    if lock_acquired:
        try:
            release_work_item("crew_queue_sync")
        except Exception:
            pass

    return {
        "state": state,
        "result": {
            "notifications": len(notifications),
            "processed": len(processed),
            "failed": len(failed),
            "failed_details": failed,
            "queue_snapshot": {k: v["card"].get("name") for k, v in current_queue.items()},
        },
    }


def main() -> int:
    result = run()
    print(json.dumps(result["result"], indent=2))
    return 0 if not result["result"]["failed_details"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
