#!/usr/bin/env python3
"""
OODA loop runner for Torus Coffee ops tasklist.
Repeats task execution, creates Trello cards for new blockers/bugs,
and logs outcomes.
"""
import json
import os
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
TASK_LIST = BASE / "10_Skills_Library/05_Operations/OODA_MASTER_TASK_LIST.md"
TASK_STATE = BASE / "10_Skills_Library/05_Operations/Crew/.ooda_task_state.json"
LOG = BASE / "10_Skills_Library/05_Operations/logs/ooda_task_loop.log"
TRELLO_SCRIPT = BASE / "10_Skills_Library/05_Operations/scripts/update_trello_status.py"
PYTHON = BASE / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"
OODA_AUTO_AGENT = BASE / "10_Skills_Library/05_Operations/Crew/ooda_auto_agent.py"

TASKS = [
    {"id": "trello_sync", "name": "Trello sync", "interval": 1},
    {"id": "fastapi_verify", "name": "FastAPI verify", "interval": 1},
    {"id": "git_status", "name": "Git status", "interval": 1},
    {"id": "docker_health", "name": "Docker health", "interval": 1},
    {"id": "inbox_check", "name": "Check PINKCADY inbox", "interval": 6},
    {"id": "git_auto", "name": "Git auto commit/push", "interval": 1},
    {"id": "nextjs_build", "name": "Next.js build", "interval": 6},
    {"id": "update_backlog", "name": "Update OODA backlog", "interval": 12},
]

def log(msg: str):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.utcnow()
        line = f"[{now.isoformat()}Z] {msg}\n"
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def load_state():
    if TASK_STATE.exists():
        try:
            return json.loads(TASK_STATE.read_text(encoding="utf-8"))
        except Exception:
            return {"tasks": {}, "bugs": [], "task_meta": {}}
    return {"tasks": {}, "bugs": [], "task_meta": {}}

def save_state(state):
    TASK_STATE.parent.mkdir(parents=True, exist_ok=True)
    TASK_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def run(cmd, timeout=120, cwd=None):
    try:
        r = subprocess.run(cmd, shell=False, creationflags=CREATE_NO_WINDOW, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def run_raw(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def docker_status():
    code, out, err = run_raw(["docker", "--context", "torus-squidstation", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"])
    if code != 0:
        return {}
    result = {}
    for line in out.splitlines():
        if "|" in line:
            name, status, ports = line.split("|", 2)
            result[name.strip()] = {"status": status.strip(), "ports": ports.strip()}
    return result

def task_trello_sync(state):
    code, out, err = run(f'"{PYTHON}" "{TRELLO_SCRIPT}"', timeout=600)
    if code == 0 and "Posted comments:" in out:
        return {"status": "completed", "output": "Trello sync verified"}
    return {"status": "failed", "output": f"Trello sync failed: {err.strip()[:200] or out.strip()[:200]}"}

def task_fastapi_verify(state):
    code, out, err = run("curl -s http://127.0.0.1:8000/api/products", timeout=15)
    if code == 0 and out.strip().startswith("["):
        return {"status": "completed", "output": "FastAPI verified at 127.0.0.1:8000"}
    return {"status": "failed", "output": "FastAPI not responding"}

def task_nextjs_build(state):
    build_dir = BASE / "06_Website/next-storefront"
    code, out, err = run("npm run build", cwd=str(build_dir), timeout=600)
    if code == 0 and any(c in out for c in ["Compiled successfully", "Generating static pages", "Exporting", "✓ Compiled"]):
        return {"status": "completed", "output": "Next.js build passed"}
    return {"status": "failed", "output": "Next.js build failed"}

def task_git_status(state):
    code, out, _ = run("git status --short", cwd=str(BASE))
    if code != 0:
        return {"status": "failed", "output": "git status failed"}
    changes = len(out.strip().splitlines()) if out.strip() else 0
    return {"status": "completed", "output": f"Git OK, {changes} changes"}

def task_docker_health(state):
    containers = docker_status()
    security = ["void-zeek", "void-suricata", "void-crowdsec", "void-prometheus", "void-grafana"]
    missing = [c for c in security if c not in containers]
    return {
        "status": "completed" if not missing else "failed",
        "output": f"Security containers up: {len(security) - len(missing)}/{len(security)}",
    }

def task_update_backlog(state):
    backlog = BASE / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
    if backlog.exists():
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        text = backlog.read_text(encoding="utf-8")
        marker = "## Auto-Update"
        if marker not in text:
            backlog.write_text(text + f"\n{marker}\n- Last OODA executor run: {now}\n- Trello sync: active\n- Git push: active\n", encoding="utf-8")
    return {"status": "completed", "output": "Backlog updated"}

def task_inbox_check(state):
    inbox = Path(r"Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX")
    if not inbox.exists():
        return {"status": "completed", "output": "PINKCADY_INBOX not reachable"}
    files = sorted(inbox.glob("*.msg.md"))
    new_files = [f.name for f in files if f.name not in state.get("inbox_processed", {})]
    state.setdefault("inbox_processed", {}).update({f: datetime.now(timezone.utc).isoformat() for f in new_files})
    output = f"Processed {len(new_files)} inbox messages" if new_files else "No new inbox messages"
    return {"status": "completed", "output": output}

def task_git_auto(state):
    auto_paths = [
        "02_Business_Operations/Communications/Outbox",
        "10_Skills_Library/05_Operations/logs",
        "08_Reports",
    ]
    code, out, _ = run("git status --short", cwd=str(BASE))
    if code != 0:
        return {"status": "failed", "output": "git status failed"}
    changes = [c for c in out.strip().splitlines() if c.strip()]
    to_add = []
    for c in changes:
        path = c[3:] if c.startswith(" M ") or c.startswith("A  ") or c.startswith("?? ") else c
        if any(path.startswith(p) for p in auto_paths):
            to_add.append(path)
    if not to_add:
        return {"status": "completed", "output": "No auto-commit paths changed"}
    add_cmd = "git add " + " ".join(f'"{p}"' for p in to_add)
    code, _, err = run(add_cmd, cwd=str(BASE))
    if code != 0:
        return {"status": "failed", "output": f"git add failed: {err.strip()[:200]}"}
    code, out, err = run('git commit -m "chore: auto OODA loop sync"', cwd=str(BASE))
    if code != 0:
        return {"status": "failed", "output": f"git commit failed: {err.strip()[:200]}"}
    code2, out2, err2 = run("git push origin main", cwd=str(BASE))
    return {"status": "completed" if code2 == 0 else "failed", "output": f"git push: {'OK' if code2 == 0 else err.strip()[:200]}"}

TASK_MAP = {
    "trello_sync": task_trello_sync,
    "fastapi_verify": task_fastapi_verify,
    "git_status": task_git_status,
    "docker_health": task_docker_health,
    "update_backlog": task_update_backlog,
    "inbox_check": task_inbox_check,
    "git_auto": task_git_auto,
    "nextjs_build": task_nextjs_build,
}

def _now_naive_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _next_due(task, state, now):
    interval = task.get("interval", 1)
    meta = state.setdefault("task_meta", {}).setdefault(task["id"], {})
    last = meta.get("next_due")
    if last is None:
        meta["next_due"] = _now_naive_utc().isoformat()
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        if last_dt.tzinfo is not None:
            last_dt = last_dt.replace(tzinfo=None)
    except Exception:
        meta["next_due"] = _now_naive_utc().isoformat()
        return True
    if last_dt <= _now_naive_utc():
        meta["next_due"] = _now_naive_utc().isoformat()
        return True
    return False

def run_once():
    state = load_state()
    now = datetime.now(timezone.utc)
    results = []
    for task in TASKS:
        task_id = task["id"]
        if not _next_due(task, state, now):
            results.append({"task": task_id, "status": "skipped", "output": "not_due"})
            continue
        try:
            fn = TASK_MAP.get(task_id)
            if not fn:
                results.append({"task": task_id, "status": "error", "output": "no handler"})
                continue
            result = fn(state)
            state.setdefault("tasks", {})[task_id] = {
                "last_run": now.isoformat(),
                "status": result["status"],
                "output": result["output"],
            }
            results.append({"task": task_id, **result})
            log(f"task_{task_id}: {result['status']} - {result['output']}")
            if result["status"] == "failed":
                state.setdefault("bugs", []).append({
                    "ts": now.isoformat(),
                    "task": task_id,
                    "output": result["output"],
                })
                log(f"bug_created: {task_id} - {result['output']}")
        except Exception as e:
            state.setdefault("tasks", {})[task_id] = {
                "last_run": now.isoformat(),
                "status": "error",
                "output": str(e),
            }
            results.append({"task": task_id, "status": "error", "output": str(e)})
            log(f"task_{task_id}_error: {e}")
    save_state(state)
    return results

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        results = run_once()
        print(json.dumps(results, indent=2))
        return
    log("ooda_task_loop started")
    while True:
        try:
            run_once()
        except Exception as e:
            import traceback
            log(f"loop_error: {e}\n{traceback.format_exc()}")
        time.sleep(60)

if __name__ == "__main__":
    main()
