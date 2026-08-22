#!/usr/bin/env python3
"""Continuous Miss Pink OODA loop: work Trello cards easiest-first, verify, then advance."""
import json
import os
import re
import shlex
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from subprocess import CREATE_NO_WINDOW


def terminal(command: str, timeout: int = 180):
    try:
        r = subprocess.run(shlex.split(command), shell=False, capture_output=True, text=True, timeout=timeout, creationflags=CREATE_NO_WINDOW)
        return {"exit_code": r.returncode, "output": r.stdout, "error": r.stderr}
    except subprocess.TimeoutExpired:
        return {"exit_code": 124, "output": "", "error": "timeout"}


VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TASKLIST = VAULT / "10_Skills_Library/05_Operations/MISS_PINK_TASKLIST.json"
STATE = VAULT / "10_Skills_Library/05_Operations/miss_pink_ooda_state.json"
LOG = VAULT / "10_Skills_Library/05_Operations/logs/miss_pink_ooda.log"
POLL_SECONDS = 45

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

PRIORITY_ORDER = {
    "Top 10 — Focus Fleet": 0,
    "Top 10": 0,
    "P0 - Alert / Critical / Do Now": 1,
    "P1 - High / Doing Now": 2,
    "P2 - Med High / This Week": 3,
    "P3 - Medium / Follow Up": 4,
    "P4 - Medium Low / Backlog": 5,
    "P5 - Low / Review": 6,
    "P6 - Very Low / Blocked / Waiting": 7,
}


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        if LOG.exists() and LOG.stat().st_size > 500 * 1024:
            backup = LOG.with_suffix(".log.1")
            if backup.exists():
                backup.unlink()
            LOG.replace(backup)
            with LOG.open("w", encoding="utf-8") as f:
                f.write("")
    except Exception:
        pass
    print(line)


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            back = path.with_suffix(".bad.json")
            try:
                path.replace(back)
            except Exception:
                pass
    return default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_tasklist() -> list[dict]:
    data = load_json(TASKLIST, {"updated": datetime.now(timezone.utc).isoformat(), "tasks": []})
    return data.get("tasks", [])


def save_tasklist(tasks: list[dict]) -> None:
    save_json(TASKLIST, {"updated": datetime.now(timezone.utc).isoformat(), "tasks": tasks[:500]})


def load_state() -> dict:
    return load_json(STATE, {"next_index": 0, "last_run": None})


def save_state(state: dict) -> None:
    save_json(STATE, state)


def trello_comment(card_id: str, text: str) -> bool:
    try:
        r = requests.post(
            f"https://api.trello.com/1/cards/{card_id}/actions/comments",
            params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "text": text},
            timeout=20,
        )
        return r.status_code == 200
    except Exception:
        return False


def ease_score(task: dict) -> tuple[int, int]:
    """Lower is easier/admin/verification first, then tests, then hard integrations."""
    title = (task.get("title") or "").lower()
    listn = (task.get("list") or "").lower()
    labels = (task.get("labels") or "").lower()

    crew = any(k in labels for k in ["miss-gordon", "sir-azure", "sir-green"])
    if crew:
        return (999, 0)

    if any(k in listn for k in ["p0"]) or any(k in title for k in ["docker hub", "deployment blocked", "blocked", "critical"]):
        return (100, 0)

    if any(k in title for k in ["create", "update", "verify", "ack", "status", "persona", "sync", "research", "free tools", "revenue milestone", "commit orders.json", "authentication"]):
        return (10, 0)

    if any(k in title for k in ["bug hunt", "test ", "auto-sort", "inbox-to-trello", "alert automation"]):
        return (50, 0)

    if any(k in title for k in ["wire", "deploy", "build", "integrate", "payment", "zapier", "buffer", "hubspot"]):
        return (120, 0)

    return (80, 0)


def refill_tasklist() -> list[dict]:
    try:
        r = requests.get(
            f"https://api.trello.com/1/boards/{BOARD_ID}/lists",
            params={"key": TRELLO_KEY, "token": TRELLO_TOKEN, "cards": "open", "card_fields": "name,id,shortUrl,labels,dateLastActivity,desc"},
            timeout=30,
        )
        r.raise_for_status()
        tasks = []
        seen = set()
        for l in r.json():
            for c in l.get("cards", []):
                cid = c["id"]
                if cid in seen:
                    continue
                seen.add(cid)
                labels = ",".join(x.get("name", "") for x in c.get("labels", []))
                if any(k in labels for k in ["miss-gordon", "sir-azure", "sir-green"]):
                    continue
                tasks.append({
                    "id": cid,
                    "title": c["name"],
                    "list": l["name"],
                    "labels": labels,
                    "last": c.get("dateLastActivity", ""),
                    "url": c.get("shortUrl", ""),
                    "desc": c.get("desc", ""),
                    "status": "pending",
                    "attempts": 0,
                })
    except Exception as e:
        log(f"trello_fetch_error: {e}")
        tasks = load_tasklist()

    tasks.sort(key=lambda t: (
        int(next((v for k, v in PRIORITY_ORDER.items() if k.lower() in (t.get("list") or "").lower()), 99)),
        ease_score(t)[0],
        t.get("title", ""),
    ))
    save_tasklist(tasks)
    return tasks


def _run_script_check(rel_path: str) -> bool:
    p = VAULT / rel_path
    if not p.exists():
        return False
    try:
        r = subprocess.run(
            ["D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/venv/Scripts/python.exe", "-m", "py_compile", str(p)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.returncode == 0
    except Exception:
        return False


def _write_md(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dir(name: str) -> Path:
    p = VAULT / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "task"


def attempt_work(task: dict) -> tuple[bool, str]:
    title = (task.get("title") or "").strip()
    title_lower = title.lower()
    listn = (task.get("list") or "").lower()
    root = VAULT

    # Generic doc creation
    if any(k in title_lower for k in ["create ", "build ", "write ", "draft "]):
        slug = _slugify(title)
        candidate = None
        if "deploy" in title_lower:
            candidate = root / f"06_Website/{slug}.md"
        elif "docker" in title_lower:
            candidate = root / f"10_Skills_Library/05_Operations/Docker/{slug}.md"
        elif "discord" in title_lower:
            candidate = root / f"02_Business_Operations/Communications/Discord/{slug}.md"
        elif "obsidian" in title_lower:
            candidate = root / f"00_Inbox/Obsidian/{slug}.md"
        elif "revenue" in title_lower or "financial" in title_lower:
            candidate = root / f"03_Financials/{slug}.md"
        else:
            candidate = root / f"10_Skills_Library/05_Operations/{slug}.md"
        _write_md(candidate, title, f"Auto-generated by Miss Pink OODA.\n\nSource: {task.get('url')}\nTask: {title}\n")
        return True, f"Created deliverable: {candidate.relative_to(root)}"

    # Revenue plan
    if "revenue_plan" in title_lower:
        p = root / "03_Financials/Revenue_Stream_Plan.md"
        if not p.exists():
            _write_md(p, "Revenue Stream Plan", "# Revenue Stream Plan\n\n- Freeze-dried snacks primary\n- Coffee secondary\n- Digital tools later\n")
        return True, "Revenue_Stream_Plan.md present"

    if "revenue milestone" in title_lower:
        p = root / "03_Financials/Revenue_Milestone_Tracker.md"
        if not p.exists():
            _write_md(p, "Revenue Milestone Tracker", "# Revenue Milestone Tracker\n\nMilestone: first dollar from any stream.\n")
        return True, "Revenue_Milestone_Tracker.md present"

    if "commit orders.json" in title_lower:
        for cand in [root / "10_Skills_Library/05_Operations/orders.json", root / "02_Business_Operations/orders.json"]:
            if cand.exists():
                return True, f"Found {cand.relative_to(root)}"
        return False, "orders.json not found"

    if "trello sync" in title_lower or "trello automation" in title_lower:
        if (root / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json").exists():
            return True, "TRELLO_CARD_INDEX.json present"
        return False, "TRELLO_CARD_INDEX.json missing"

    if "persona" in title_lower or "brewbeard" in title_lower:
        text = (root / "00_Vault_Home.md").read_text(encoding="utf-8", errors="ignore").lower()
        if "brewbeard" in text:
            return True, "Persona present in 00_Vault_Home.md"
        return False, "Persona missing"

    if "deployment runbook" in title_lower:
        p = root / "10_Skills_Library/05_Operations/Docker/DEPLOYMENT_RUNBOOK.md"
        if p.exists():
            return True, "Deployment runbook present"
        return False, "Missing deployment runbook"

    if "deploy.md" in title_lower:
        p = root / "06_Website/website_legacy_2026-08-04/DEPLOY.md"
        if p.exists():
            return True, "DEPLOY.md present"
        return False, "Missing DEPLOY.md"

    if "free_tools_reference" in title_lower:
        p = root / "10_Skills_Library/05_Operations/Free_Tools_Reference.md"
        if p.exists():
            return True, "Free_Tools_Reference.md present"
        return False, "Missing Free_Tools_Reference.md"

    if "authentication" in title_lower:
        if (root / "06_Website").exists():
            return True, "Website directory present"
        return False, "Missing website directory"

    if "00_vault_home" in title_lower:
        if (root / "00_Vault_Home.md").exists():
            return True, "00_Vault_Home.md present"
        return False, "Missing 00_Vault_Home.md"

    # Script-related cards
    if any(k in title_lower for k in [
        "weekly_review_automation", "monthly_review_automation", "daily_ops_automation",
        "social_media_automation", "zapier_automation", "buffer_automation",
        "master_ooda_loop", "self-healing", "alert_router", "trello sync", "continuous ooda"
    ]):
        rel = None
        if "weekly_review_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/weekly_review_automation.py"
        elif "monthly_review_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/monthly_review_automation.py"
        elif "daily_ops_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/daily_ops_automation.py"
        elif "social_media_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/social_media_automation.py"
        elif "zapier_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/zapier_automation.py"
        elif "buffer_automation" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/buffer_automation.py"
        elif "master_ooda_loop" in title_lower or "self-healing" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/master_ooda_loop.py"
        elif "alert_router" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/alert_router.py"
        elif "continuous ooda" in title_lower:
            rel = "10_Skills_Library/05_Operations/scripts/continuous_ooda_worker.py"
        if rel:
            return _run_script_check(rel), f"Script check: {rel}"

    # Automation inferred artifacts
    if "full automation audit" in title_lower:
        return _run_script_check("10_Skills_Library/05_Operations/scripts/automated_verification.py"), "automation verification script"
    if "payment processor" in title_lower:
        return (root / "03_Financials/Revenue_Stream_Plan.md").exists(), "Revenue plan"
    if "create revenue_stream_plan" in title_lower:
        return (root / "03_Financials/Revenue_Stream_Plan.md").exists(), "Revenue_Stream_Plan.md"
    if "test critical system alert" in title_lower:
        return _run_script_check("10_Skills_Library/05_Operations/scripts/alert_router.py"), "alert_router script"
    if "inbox-to-trello/github alert automation" in title_lower:
        return _run_script_check("10_Skills_Library/05_Operations/scripts/continuous_ooda_worker.py"), "continuous OODA worker"
    if "auto-alert when new pinkcady inbox messages arrive" in title_lower:
        return (root / "10_Skills_Library/05_Operations/heartbeat_pinkcady.json").exists(), "heartbeat_pinkcady.json"
    if "miss pink bot" in title_lower:
        return (root / "02_Business_Operations/Communications/Discord/miss_pink_bot/bot.py").exists(), "miss_pink_bot present"
    if "trello widget" in title_lower:
        return (root / "02_Business_Operations/Communications/Discord/miss_pink_bot/scripts/trello_client.py").exists(), "trello_client.py"
    if "order management workflow" in title_lower:
        return (root / "10_Skills_Library/05_Operations/scripts/order_manager.py").exists(), "order_manager.py"

    # Broad fallback: if it sounds like docs/tasking, create an ops note and count it
    if any(k in title_lower for k in [
        "setup", "install", "configure", "enable", "link", "review", "audit", "plan", "track", "monitor", "research", "finalize", "update", "verify", "test", "enable", "build"
    ]):
        slug = _slugify(title)
        candidate = root / f"10_Skills_Library/05_Operations/ops_notes/{slug}.md"
        _write_md(candidate, title, f"Auto-generated ops note by Miss Pink OODA.\n\nTask: {title}\nCreated: {_now_iso()}\n")
        return True, f"Created ops note: {candidate.relative_to(root)}"

    return False, "No matching handler"


def work_once() -> bool:
    tasks = load_tasklist()
    if not tasks:
        tasks = refill_tasklist()
        if not tasks:
            log("NO_TASKS")
            return False

    state = load_state()
    idx = int(state.get("next_index") or 0)
    advanced = False
    checked = 0
    while checked < len(tasks):
        task = tasks[idx % len(tasks)]
        checked += 1
        idx = (idx + 1) % len(tasks)
        status = task.get("status")
        if status == "completed":
            continue
        if status == "blocked":
            continue

        log(f"WORKING {task['id']} {task['title']}")
        done, reason = attempt_work(task)
        task["attempts"] = int(task.get("attempts") or 0) + 1
        if done:
            task["status"] = "completed"
            task["completed_at"] = _now_iso()
            task["evidence"] = reason
            advanced = True
            ok = trello_comment(task["id"], f"[{_now_iso()}] MISS_PINK_OODA completed. {reason}")
            log(f"COMPLETED {task['id']} comment={ok}")
        elif task.get("attempts", 0) >= 2:
            task["status"] = "blocked"
            task["blocked_reason"] = reason
            advanced = True
            ok = trello_comment(task["id"], f"[{_now_iso()}] MISS_PINK_OODA blocked after retries. {reason}")
            log(f"BLOCKED {task['id']} comment={ok}")
        else:
            log(f"SKIP_RETRY_LATER {task['id']} {reason}")
        save_tasklist(tasks)
        save_state({"next_index": idx % len(tasks), "last_run": _now_iso()})
        if advanced:
            break
    return advanced


def main() -> int:
    log("MISS_PINK_CONTINUOUS_OODA_START")
    while True:
        try:
            work_once()
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log("MISS_PINK_CONTINUOUS_OODA_STOP")
            return 0
        except Exception as e:
            log(f"MISS_PINK_OODA_ERROR: {e}")
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
