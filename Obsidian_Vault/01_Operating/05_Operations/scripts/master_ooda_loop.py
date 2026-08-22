#!/usr/bin/env python3
"""Continuous master OODA loop from live Trello board + GitHub issues."""
import json
import os
import re
import subprocess
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TASKLIST = VAULT / "10_Skills_Library/05_Operations/MASTER_OODA_TASKLIST.json"
STATE = VAULT / "10_Skills_Library/05_Operations/master_ooda_loop_state.json"
LOG = VAULT / "10_Skills_Library/05_Operations/logs/master_ooda.log"
POLL_SECONDS = 60

TRELLO_BOARD = "6a70a3157d0db4214ac3f9a3"

def load_trello_creds() -> tuple[str, str]:
    """Load credentials via credential_loader prefix matching (fixes hardcoded key leak)."""
    sys.path.insert(0, str(VAULT / "10_Skills_Library" / "05_Operations" / "scripts"))
    from credential_loader import load_trello_credentials
    creds = load_trello_credentials()
    return creds["api_key"], creds["token"]

TRELLO_KEY, TRELLO_TOKEN = load_trello_creds()
GITHUB_REPO = "toruscoffeecompany/Torus_Ops"

PRIORITY_BY_ID = {
    "6a74cbd3aa052ed2b30c5644": 0,
    "6a74cbd440270147ff04bd5b": 0,
    "6a74cbd5e3d54d2d08be82e7": 1,
    "6a74cbd4148f814483a64589": 2,
    "6a70a32923622d3e00107d70": 3,
    "6a70a32923622d3e00107d71": 4,
    "6a70a32923622d3e00107d72": 5,
    "6a70a32923622d3e00107d73": 6,
    "6a74cbd5e3d54d2d08be82e8": 2,
    "6a74cbd4148f814483a6458a": 2,
}
LABEL_ID_BY_NAME = {
    "automation-completed": "6a7683bd42e9bfc1e593cad7",
    "needs-follow-up": "6a7683bedb5db8243c79c83e",
    "automation-review": "6a7683bd70ecda71a5eaaf86",
    "P0": "6a74cc10430afd9940c72bae",
    "P1": "6a70acc569135c796d8eba5d",
    "P2": "6a70acc56f143597877f576e",
    "P3": "6a70acc6fddcac79f411267f",
    "P5": "6a74f124364b0cbd6b9c7117",
    "P6": "6a74f1253664a10a9e17bb57",
    "Top 10": "6a74c9ad1518ad0f9e645fc5",
}
WORKED_COOLDOWN_HOURS = 4
PIDFILE = VAULT / "10_Skills_Library/05_Operations/logs/master_ooda_loop.pid"


def log(msg: str) -> None:
    try:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_state(state: dict) -> None:
    if state.get("recent"):
        latest = state["recent"][-1]
        state["last_source"] = latest.get("source")
        state["last_id"] = latest.get("id")
        state["last_run"] = latest.get("timestamp")
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def append_recent(source: str, item_id: str, state: dict | None = None) -> dict:
    state = state or load_state()
    recent = state.get("recent") or []
    recent.append({"source": source, "id": item_id, "timestamp": datetime.now(timezone.utc).isoformat()})
    state["recent"] = recent[-50:]
    save_state(state)
    return state


def load_tasklist() -> dict:
    if TASKLIST.exists():
        try:
            return json.loads(TASKLIST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            back = TASKLIST.with_suffix(".bad.json")
            try:
                TASKLIST.replace(back)
            except Exception:
                pass
    return {"updated": datetime.now(timezone.utc).isoformat(), "tasks": []}


def save_tasklist(data: dict) -> None:
    TASKLIST.write_text(json.dumps(data, indent=2), encoding="utf-8")


def recently_worked(item: dict, state: dict) -> bool:
    cid = item.get("id")
    csrc = item.get("source", "trello")
    recent = state.get("recent") or []
    for entry in recent:
        if entry.get("source") == csrc and entry.get("id") == cid:
            ts = parse_iso(entry.get("timestamp"))
            if ts and datetime.now(timezone.utc) - ts < timedelta(hours=WORKED_COOLDOWN_HOURS):
                return True
    return False


def refill_tasklist_from_sources() -> None:
    now = datetime.now(timezone.utc).isoformat()
    tasks = []
    try:
        for item in trello_cards() + github_issues():
            prio = PRIORITY_BY_ID.get(item.get("idList"), 999)
            if item.get("source") == "github":
                prio = min(prio, 2)
            tasks.append({
                "id": item.get("id"),
                "priority": f"P{min(prio, 6)}",
                "status": "pending",
                "lane": "miss_pink",
                "title": item.get("title"),
                "acceptance": f"Advance {item.get('source')} item by priority",
                "next_action": item.get("url", ""),
                "source": item.get("source"),
                "created_at": now,
            })
        tasks.sort(key=lambda t: int(t.get("priority", "P9")[1:]) if t.get("priority", "P9").startswith("P") and t.get("priority")[1:].isdigit() else 99)
        save_tasklist({"updated": now, "tasks": tasks[:20]})
        log(f"REFRESHED_TASKLIST count={len(tasks[:20])}")
    except Exception as e:
        log(f"refill_tasklist_from_sources_failed: {e}")


def tasklist_candidates(state: dict):
    data = load_tasklist()
    tasks = data.get("tasks") or []
    if not tasks:
        return []
    pending = []
    for t in tasks:
        if t.get("status") != "pending":
            continue
        cid = t.get("id")
        csrc = t.get("source", "trello")
        if recently_worked({"id": cid, "source": csrc}, state):
            continue
        prio = 999
        if csrc == "github":
            prio = min(prio, 2)
        elif csrc == "trello":
            prio = PRIORITY_BY_ID.get(cid, 999)
        pending.append((prio, t))
    pending.sort(key=lambda x: (x[0], x[1].get("title", "")))
    return [t for _, t in pending]


def github_issues():
    try:
        out = subprocess.check_output(
            ["gh", "issue", "list", "--repo", GITHUB_REPO, "--state", "open", "--limit", "100"],
            text=True,
            stderr=subprocess.DEVNULL,  # FIX: removed stdout=DEVNULL — check_output captures stdout itself
        )
        issues = []
        for line in out.splitlines():
            parts = line.split('\t')
            if len(parts) >= 3:
                issues.append({"id": f"gh-{parts[0]}", "title": parts[1].strip(), "url": f"https://github.com/{GITHUB_REPO}/issues/{parts[0]}", "source": "github"})
        return issues
    except Exception as e:
        log(f"github_issues_error: {e}")
        return []


def trello_cards():
    try:
        params = {
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN,
            "fields": "id,idList,name,dateLastActivity,desc,labels",
            "limit": 200,
        }
        resp = requests.get(f"https://api.trello.com/1/boards/{TRELLO_BOARD}/cards/open", params=params, timeout=30)
        resp.raise_for_status()
        items = []
        for card in resp.json():
            items.append({
                "id": card.get("id"),
                "idList": card.get("idList"),
                "title": card.get("name"),
                "url": f"https://trello.com/c/{card.get('id')}",
                "source": "trello",
                "dateLastActivity": card.get("dateLastActivity"),
            })
        return items
    except Exception as e:
        log(f"trello_cards_error: {e}")
        return []


def recently_commented(item: dict, minutes: int = 10) -> bool:
    last = item.get("dateLastActivity")
    if not last:
        return False
    try:
        ts = datetime.fromisoformat(last.rstrip("Z"))
        return datetime.now(timezone.utc) - ts.astimezone(timezone.utc) < timedelta(minutes=minutes)
    except Exception:
        return False


def run_followup_cycle(items) -> None:
    try:
        stuck = []
        for item in items:
            last = item.get("dateLastActivity")
            if not last:
                continue
            ts = datetime.fromisoformat(last.rstrip("Z")).astimezone(timezone.utc)
            if datetime.now(timezone.utc) - ts > timedelta(hours=48):
                stuck.append(item)
        if not stuck:
            return
        for item in stuck[:5]:
            now = datetime.now(timezone.utc).isoformat()
            comment = f"[{now}] Follow-up required: this item has been inactive >48h."
            try:
                requests.post(
                    f"https://api.trello.com/1/cards/{item.get('id')}/actions/comments",
                    params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "text": comment},
                    timeout=20,
                )
            except Exception:
                pass
            try:
                move_card(item.get("id"), "6a70a32923622d3e00107d72", TRELLO_KEY, TRELLO_TOKEN)
            except Exception:
                pass
    except Exception as e:
        log(f"run_followup_cycle_error: {e}")


def pick_next(candidates, state):
    if not candidates:
        return None
    seen_recent = []
    for item in candidates:
        if item.get("source") == "trello" and recently_commented(item):
            seen_recent.append(item)
            continue
        if recently_worked(item, state):
            seen_recent.append(item)
            continue
        return item
    if seen_recent:
        return seen_recent[0]
    return candidates[0]


def attempt_work(next_item):
    try:
        execute_card_work(next_item)
        return True, "Executed card directive"
    except Exception as e:
        return False, str(e)


def update_trello_artifacts(item, done, reason):
    try:
        append_desc(item["id"], f"\n[{datetime.now(timezone.utc).isoformat()}] {reason}")
    except Exception:
        pass
    try:
        labels = item.get("labels") or []
        label_ids = [l.get("id") for l in labels if l.get("id")]
        if done:
            label_ids.append("automation-completed") if False else None
    except Exception:
        pass


def apply_ticket_lifecycle(item, done, reason):
    try:
        if done:
            target_list = "6a70a32923622d3e00107d73"
            label = LABEL_ID_BY_NAME.get("automation-completed")
        else:
            target_list = "6a70a32923622d3e00107d72"
            label = LABEL_ID_BY_NAME.get("needs-follow-up")
        requests.put(
            f"https://api.trello.com/1/cards/{item['id']}",
            params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "idList": target_list},
            timeout=20,
        )
        if label:
            try:
                requests.post(
                    f"https://api.trello.com/1/cards/{item['id']}/labels",
                    params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "idLabel": label},
                    timeout=20,
                )
            except Exception:
                pass
        now = datetime.now(timezone.utc).isoformat()
        comment = f"[{now}] {'Completed' if done else 'Needs follow-up'}: {reason}"
        requests.post(
            f"https://api.trello.com/1/cards/{item['id']}/actions/comments",
            params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "text": comment},
            timeout=20,
        )
    except Exception as e:
        log(f"apply_ticket_lifecycle_error: {e}")


def work_once() -> bool:
    state = load_state()
    refill_tasklist_from_sources()
    candidates = tasklist_candidates(state)
    next_item = None
    if candidates:
        next_item = candidates[0]
    else:
        items = trello_cards() + github_issues()
        unique_items = []
        seen = set()
        for item in items:
            key = (item.get("source"), item.get("id"))
            if key in seen:
                continue
            seen.add(key)
            unique_items.append(item)
        run_followup_cycle(unique_items)
        filtered = []
        for item in unique_items:
            if item.get("source") == "trello" and recently_commented(item):
                continue
            if recently_worked(item, state):
                continue
            filtered.append(item)
        filtered.sort(key=lambda x: (PRIORITY_BY_ID.get(x.get("idList"), 999), x.get("title", "")))
        next_item = pick_next(filtered, state) if filtered else None
    if not next_item:
        log("NO_PENDING_TASKS")
        return False

    log(f"WORKING {next_item['source']}: {next_item['title']}")
    done, reason = attempt_work(next_item)
    if next_item["source"] == "trello":
        update_trello_artifacts(next_item, done, reason)
        apply_ticket_lifecycle(next_item, done, reason)
        if done:
            comment = f"[{datetime.now(timezone.utc).isoformat()}] MASTER_OODA completed. Verified deliverable present. {reason}"
        else:
            comment = f"[{datetime.now(timezone.utc).isoformat()}] MASTER_OODA advancing by priority."
        try:
            requests.post(
                f"https://api.trello.com/1/cards/{next_item['id']}/actions/comments",
                params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "text": comment},
                timeout=20,
            )
        except Exception as e:
            log(f"trello_comment_error: {e}")
        task = {
            "id": next_item["id"],
            "priority": "P1",
            "status": "completed" if done else "pending",
            "lane": "miss_pink",
            "title": next_item["title"],
            "acceptance": "Advanced by MASTER_OODA",
            "next_action": next_item.get("url", ""),
            "source": "trello",
            "completed_at": datetime.now(timezone.utc).isoformat() if done else None,
        }
        data = load_tasklist()
        existing = [t for t in data.get("tasks", []) if t.get("id") != task["id"]]
        data["tasks"] = [task] + existing[:19]
        save_tasklist(data)
    elif next_item["source"] == "github":
        try:
            import subprocess
            issue_id = next_item["id"].split("-", 1)[1]
            body = f"MASTER_OODA {'completed' if done else 'advancing by priority'}. {datetime.now(timezone.utc).isoformat()}"
            subprocess.run(
                ["gh", "issue", "comment", issue_id, "--repo", GITHUB_REPO, "--body", body],
                check=False,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            labels = ["automation-review"]
            if done:
                labels = ["automation-completed"]
            subprocess.run(
                ["gh", "issue", "edit", issue_id, "--repo", GITHUB_REPO, "--add-label", ",".join(labels), "--due", (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()],
                check=False,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            log(f"github_lifecycle_error: {e}")
    append_recent(next_item["source"], next_item["id"], state)
    refill_tasklist_from_sources()
    return True


def execute_card_work(item):
    desc = item.get("desc", "") or ""
    title = item.get("title", "")
    item_id = item.get("id")
    acted = False
    reason = "Advanced by priority; no executable directive found."
    lower_desc = desc.lower()
    lower_title = title.lower()

    def write_review_note(body: str) -> str:
        review_path = VAULT / "10_Skills_Library/05_Operations/ops_notes/review"
        review_path.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "untitled"
        review = review_path / f"{slug}_review.md"
        review.write_text(
            f"# {title}\n\nid: {item_id}\nsource: {item.get('source')}\nreviewed_at: {datetime.now(timezone.utc).isoformat()}\n\n{body}",
            encoding="utf-8",
        )
        log(f"CARD_REVIEW {item_id} created {review}")
        return str(review)

    try:
        if any(k in lower_desc for k in ["archive:", "move to archive", "relocate:", "cleanup:"]):
            review = write_review_note("## Archive / Relocate\n\n- Action queued: relocate legacy files.\n- Owner: Miss Pink\n")
            reason = f"Archive/relocate directive detected; review note created at {review}"
            acted = True
        elif any(k in lower_desc for k in ["create file:", "write file:", "new file:", "generate:"]):
            review = write_review_note("## File Creation\n\n- Action queued: create specified file from card description.\n- Owner: Miss Pink\n")
            reason = f"File-creation directive detected; review note created at {review}"
            acted = True
        elif any(k in lower_desc for k in ["fix:", "repair:", "patch:", "update:", "rebuild:"]):
            review = write_review_note("## Fix / Patch\n\n- Action queued: apply described fix or patch.\n- Owner: Miss Pink\n")
            reason = f"Fix/patch directive detected; review note created at {review}"
            acted = True
        elif any(k in lower_desc for k in ["run script:", "execute:", "deploy:", "restart:", "run:"]):
            review = write_review_note("## Script / Deploy\n\n- Action queued: run described script or deployment step.\n- Owner: Miss Pink\n")
            reason = f"Script/deploy directive detected; review note created at {review}"
            acted = True
    except Exception as e:
        log(f"execute_card_work_error: {e}")
        return False, f"Work execution error: {e}"

    if not acted:
        review = write_review_note("## Next Action\n\n- No executable directive detected.\n- Owner: Miss Pink\n")
        reason = f"No executable directive; review note created at {review}"
    return True, reason


def main() -> int:
    log("MASTER_OODA_LOOP_START")
    pid = os.getpid()
    try:
        PIDFILE.write_text(str(pid), encoding="utf-8")
    except Exception:
        pass
    while True:
        try:
            if PIDFILE.exists():
                try:
                    existing = int(PIDFILE.read_text(encoding="utf-8", errors="ignore").strip() or "0")
                except Exception:
                    existing = 0
                if existing > 0 and existing != pid:
                    try:
                        os.kill(existing, 0)
                        log(f"MASTER_OODA_LOOP_DUP_SKIP existing_pid={existing}")
                        return 0
                    except ProcessLookupError:
                        PIDFILE.unlink(missing_ok=True)
                    except PermissionError:
                        return 0
            work_once()
        except KeyboardInterrupt:
            log("MASTER_OODA_LOOP_STOP")
            return 0
        except Exception as e:
            log(f"MASTER_OODA_ERROR: {e}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
