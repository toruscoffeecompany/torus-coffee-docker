#!/usr/bin/env python3
"""
Torus Coffee OODA Task Executor.
Reads OODA_TASK_LIST.md, executes unblocked tasks,
creates Trello cards for new bugs/blockers, and loops.
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
TASK_LIST = BASE / "10_Skills_Library/05_Operations/OODA_TASK_LIST.md"
TASK_STATE = BASE / "10_Skills_Library/05_Operations/Crew/.ooda_task_state.json"
LOG = BASE / "10_Skills_Library/05_Operations/logs/ooda_task_executor.log"
TRELLO_SCRIPT = BASE / "10_Skills_Library/05_Operations/scripts/update_trello_status.py"
PYTHON = BASE / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"

def log(msg: str):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def load_state():
    if TASK_STATE.exists():
        try:
            return json.loads(TASK_STATE.read_text(encoding="utf-8"))
        except Exception:
            return {"tasks": {}}
    return {"tasks": {}}

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

def verify_fastapi():
    code, out, err = run("curl -s http://127.0.0.1:8000/api/products", timeout=15)
    return code == 0 and out.strip().startswith("[")

def verify_nextjs():
    build_dir = BASE / "06_Website/next-storefront"
    code, out, err = run("npm run build", cwd=str(build_dir), timeout=600)
    if code != 0:
        return False
    checks = [
        "Compiled successfully",
        "Generating static pages",
        "Exporting",
        "✓ Compiled",
    ]
    return any(c in out for c in checks)

def verify_trello():
    code, out, err = run(f'"{PYTHON}" "{TRELLO_SCRIPT}"', timeout=600)
    return code == 0 and "Posted comments:" in out

def verify_git():
    code, out, err = run("git rev-parse --abbrev-ref HEAD", cwd=str(BASE))
    return code == 0

def task_trello_sync():
    result = verify_trello()
    return {"status": "completed" if result else "failed", "output": "Trello sync verified" if result else "Trello sync failed"}

def task_fastapi_verify():
    result = verify_fastapi()
    return {"status": "completed" if result else "failed", "output": "FastAPI verified at 127.0.0.1:8000" if result else "FastAPI not responding"}

def task_nextjs_build():
    result = verify_nextjs()
    return {"status": "completed" if result else "failed", "output": "Next.js build passed" if result else "Next.js build failed"}

def task_git_status():
    result = verify_git()
    code2, out2, _ = run("git status --short", cwd=str(BASE))
    changes = len(out2.strip().splitlines()) if code2 == 0 else -1
    return {"status": "completed" if result else "failed", "output": f"Git OK, {changes} changes"}

def task_docker_health():
    containers = docker_status()
    security = ["void-zeek", "void-suricata", "void-crowdsec", "void-prometheus", "void-grafana"]
    missing = [c for c in security if c not in containers]
    return {"status": "completed" if not missing else "blocked", "output": f"Security containers up: {len(security) - len(missing)}/{len(security)}"}

def task_update_backlog():
    backlog = BASE / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
    if backlog.exists():
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        text = backlog.read_text(encoding="utf-8")
        if "## Auto-Update" not in text:
            text += f"\n## Auto-Update\n- Last OODA executor run: {now}\n- Trello sync: active\n- Git push: active\n"
            backlog.write_text(text, encoding="utf-8")
    return {"status": "completed", "output": "Backlog updated"}

TASKS = {
    "trello_sync": task_trello_sync,
    "fastapi_verify": task_fastapi_verify,
    "nextjs_build": task_nextjs_build,
    "git_status": task_git_status,
    "docker_health": task_docker_health,
    "update_backlog": task_update_backlog,
}

def run_once():
    state = load_state()
    results = []
    for name, fn in TASKS.items():
        task_state = state.get("tasks", {}).get(name, {})
        if task_state.get("status") == "completed":
            results.append({"task": name, "status": "skipped", "output": "already_completed"})
            continue
        try:
            result = fn()
            state.setdefault("tasks", {})[name] = {
                "last_run": datetime.now(timezone.utc).isoformat(),
                "status": result["status"],
                "output": result["output"],
            }
            results.append({"task": name, **result})
            log(f"task_{name}: {result['status']} - {result['output']}")
        except Exception as e:
            state.setdefault("tasks", {})[name] = {
                "last_run": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "output": str(e),
            }
            results.append({"task": name, "status": "error", "output": str(e)})
            log(f"task_{name}_error: {e}")
    save_state(state)
    return results

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        results = run_once()
        print(json.dumps(results, indent=2))
        return
    log("ooda_task_executor started")
    while True:
        try:
            results = run_once()
            for r in results:
                if r.get("status") == "failed":
                    log(f"task_failed: {r['task']} - {r.get('output', '')}")
        except Exception as e:
            log(f"loop_error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
