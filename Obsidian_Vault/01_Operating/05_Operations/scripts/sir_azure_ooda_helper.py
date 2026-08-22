#!/usr/bin/env python3
"""Advance Sir Azure's actionable Trello cards with local verification/commenting."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD = "6a70a3157d0db4214ac3f9a3"
STATE = VAULT / "10_Skills_Library/05_Operations/sir_azure_ooda_state.json"


def _headers():
    return {"Accept": "application/json", "Content-Type": "application/json"}


def get_json(url, params=None):
    r = requests.get(url, params=dict(params or {}, key=KEY, token=TOKEN), timeout=30, headers=_headers())
    r.raise_for_status()
    return r.json()


def post_json(url, payload):
    r = requests.post(url, params={"key": KEY, "token": TOKEN}, json=payload, timeout=30, headers=_headers())
    return r.status_code, r.text


def comment(card_id, text):
    return post_json(f"https://api.trello.com/1/cards/{card_id}/actions/comments", {"text": text})


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            back = STATE.with_suffix(".bad.json")
            try:
                STATE.replace(back)
            except Exception:
                pass
    return {"last_id": None, "last_run": None}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def verify_azure_task(task: dict) -> tuple[bool, str]:
    title = (task.get("title") or "").strip().lower()
    root = VAULT

    if "queue mapping logic" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/sir_azure_queue_mapping_logic.md"
        if p.exists():
            return True, "Queue mapping doc present"
        return False, "Queue mapping doc missing"

    if "task scheduler" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/review_task_scheduler_jobs.md"
        if p.exists():
            return True, "Task Scheduler review note present"
        return False, "Task Scheduler review note missing"

    if "rename pcs" in title or "pirate rig names" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/rename_pcs_to_pirate_rig_names.md"
        if p.exists():
            return True, "Rename plan note present"
        return False, "Rename plan note missing"

    if "gordon's audit findings" in title or "review gordon" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/review_gordons_audit_findings.md"
        if p.exists():
            return True, "Gordon audit review note present"
        return False, "Gordon audit review note missing"

    if "tailscale" in title or "drive maps" in title or "gh access" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/sir_azure_stealthattack_connectivity_checklist.md"
        if p.exists():
            return True, "STEALTHATTACK connectivity checklist present"
        return False, "STEALTHATTACK connectivity checklist missing"

    if "verify voidpiratetrade github" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/sir_azure_verify_voidpiratetrade_github_access.md"
        if p.exists():
            return True, "VOID GitHub verify note present"
        return False, "VOID GitHub verify note missing"

    if "prepare torus repos list" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/prepare_torus_repos_list_for_sir_azure.md"
        if p.exists():
            return True, "Torus repos list present"
        return False, "Torus repos list missing"

    if "alert automation" in title and "sir green/sir azure" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/alert_automation_sir_green_sir_azure_inbox.md"
        if p.exists():
            return True, "Alert automation inbox note present"
        return False, "Alert automation inbox note missing"

    if "build template" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/sir_azure_build_template_audit.md"
        if p.exists():
            return True, "Build template audit note present"
        return False, "Build template audit note missing"

    if "docker connection established" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/sir_azure_docker_connection_established.md"
        if p.exists():
            return True, "Docker connection note present"
        return False, "Docker connection note missing"

    if "cosmos library" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/add_cosmos_library_update_watcher.md"
        if p.exists():
            return True, "Cosmos watcher note present"
        return False, "Cosmos watcher note missing"

    if "fleet_comms_watcher" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/fleet_comms_watcher_deploy_note.md"
        if p.exists():
            return True, "fleet_comms_watcher note present"
        return False, "fleet_comms_watcher note missing"

    if "security-docs route" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/add_security_docs_route_dashboard_server.md"
        if p.exists():
            return True, "Security docs route note present"
        return False, "Security docs route note missing"

    if "hive-mind mesh automation bridge" in title:
        p = root / "10_Skills_Library/05_Operations/ops_notes/hive_mind_mesh_automation_bridge.md"
        if p.exists():
            return True, "Hive-mind mesh note present"
        return False, "Hive-mind mesh note missing"

    if "website content - about page" in title:
        p = root / "06_Website/website_content_about_page.md"
        if p.exists():
            return True, "About page content present"
        return False, "About page content missing"

    return False, "No local handler"


def ensure_md(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def work_once() -> bool:
    list_ids = [
        "6a74cbd3aa052ed2b30c5644",
        "6a74cbd5e3d54d2d08be82e7",
        "6a74cbd4148f814483a64589",
        "6a70a32923622d3e00107d70",
        "6a74cbd573259cffe8a23cc0",
        "6a74cbd67bbe3ef35a634495",
    ]
    list_map = {}
    for lid in list_ids:
        r = requests.get(f"https://api.trello.com/1/lists/{lid}", params={"key": KEY, "token": TOKEN, "fields": "name"}, timeout=20)
        list_map[lid] = r.json().get("name", lid)

    tasks = []
    seen = set()
    for lid in list_ids:
        r = requests.get(
            f"https://api.trello.com/1/lists/{lid}/cards",
            params={"key": KEY, "token": TOKEN, "fields": "name,id,labels,dateLastActivity,desc"},
            timeout=30,
        )
        for c in r.json():
            cid = c["id"]
            if cid in seen:
                continue
            seen.add(cid)
            labels = [x.get("name", "").lower() for x in c.get("labels", [])]
            if any(k in labels for k in ["sir-azure", "sir azure's queue"]):
                tasks.append({
                    "id": cid,
                    "title": c.get("name", ""),
                    "list": list_map.get(lid, lid),
                    "labels": ",".join(x.get("name", "") for x in c.get("labels", [])),
                    "last": c.get("dateLastActivity", ""),
                    "desc": c.get("desc", ""),
                })

    state = load_state()
    last_id = state.get("last_id")
    candidates = [t for t in tasks if t["id"] != last_id]
    if not candidates:
        print("NO_PENDING_SIR_AZURE_TASKS")
        return False

    candidates.sort(key=lambda t: t.get("last", "") or "")
    task = candidates[0]
    ts = now_iso()
    done, reason = verify_azure_task(task)
    if done:
        ok, _ = comment(task["id"], f"[{ts}] MISS_PINK_OODA completed. {reason}")
        print(f"COMPLETED {task['id']} comment={ok} {task['title']}")
    else:
        ok, _ = comment(task["id"], f"[{ts}] MISS_PINK_OODA review. {reason}")
        print(f"REVIEW {task['id']} comment={ok} {task['title']}")
    save_state({"last_id": task["id"], "last_run": ts})
    return True


if __name__ == "__main__":
    work_once()
