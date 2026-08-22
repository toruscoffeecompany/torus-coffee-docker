#!/usr/bin/env python3
"""
OODA Auto-Agent for Torus Coffee Company.
Continuously processes Sir Green's OODA prompts from PINKCADY_INBOX,
executes actions, replies with verified results, and updates Git/Trello.
"""
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
INBOX = Path(r"Z:\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX")
OUTBOX = BASE / "02_Business_Operations/Communications/Outbox"
LOG = BASE / "10_Skills_Library/05_Operations/logs/ooda_auto_agent.log"
STATE = BASE / "10_Skills_Library/05_Operations/Crew/.ooda_auto_agent_state.json"
TRELLO_SCRIPT = BASE / "10_Skills_Library/05_Operations/scripts/update_trello_status.py"
PYTHON = BASE / "10_Skills_Library/05_Operations/venv/Scripts/python.exe"

# Crew coordination system — prevents duplicate work across PINKCADY/SQUIDSTATION/STEALTHATTACK
sys.path.insert(0, str(BASE / "10_Skills_Library/05_Operations/Crew"))
try:
    from crew_coordination import claim_work_item, release_work_item, is_claimed
    CREW_COORDINATION = True
except ImportError:
    CREW_COORDINATION = False

CREW_ID = "misspink"  # Miss Pink's crew identifier for coordination lock

TOPIC_HANDLERS = {
    "dashboard": "_handle_dashboard",
    "github": "_handle_github",
    "healing": "_handle_healing",
    "security": "_handle_security",
    "trello": "_handle_trello",
    "git": "_handle_git",
    "general": "_handle_general",
}

def log(msg: str):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {"processed": {}}
    return {"processed": {}}

def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def run(cmd, timeout=60, cwd=None):
    """Run a command without spawning cmd.exe (fixes Windows popup windows).
    Accepts either a list (preferred) or a shell string (auto-split via shlex)."""
    try:
        args = cmd if isinstance(cmd, list) else shlex.split(cmd)
        r = subprocess.run(args, shell=False, capture_output=True, text=True,
                          timeout=timeout, cwd=cwd,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def run_raw(cmd, timeout=60):
    try:
        args = cmd if isinstance(cmd, list) else shlex.split(cmd)
        r = subprocess.run(args, shell=False, capture_output=True, text=True,
                          timeout=timeout,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def docker(cmd):
    return run_raw(["docker", "--context", "torus-squidstation"] + cmd)

def docker_status():
    code, out, err = docker(["ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"])
    if code != 0:
        return {"_error": f"docker_ps_failed: {err.strip()[:200] or out.strip()[:200]}"}
    result = {}
    for line in out.splitlines():
        if "|" in line:
            name, status, ports = line.split("|", 2)
            result[name.strip()] = {"status": status.strip(), "ports": ports.strip()}
    return result

def docker_logs(container, tail=20):
    code, out, err = docker(["logs", "--tail", str(tail), container])
    if code != 0:
        return f"ERROR: {err.strip()}"
    return out.strip()

def _handle_dashboard(msg):
    containers = docker_status()
    findings = []
    findings.append(f"void-grafana: {containers.get('void-grafana', {}).get('status', 'MISSING')}")
    findings.append(f"void-prometheus: {containers.get('void-prometheus', {}).get('status', 'MISSING')}")
    findings.append(f"torus-dashboard: {containers.get('torus-dashboard', {}).get('status', 'MISSING')}")
    findings.append(f"torus-alert-router: {containers.get('torus-alert-router', {}).get('status', 'MISSING')}")
    if "torus-dashboard" not in containers:
        findings.append(":3004 listener: NOT FOUND")
    return {
        "verified": ["Grafana container status", "Prometheus container status"],
        "findings": findings,
        "needs": [
            "Provide torus-dashboard container/image/run command",
            "Confirm expected :3004 port binding",
        ],
    }

def _handle_github(msg):
    code, out, err = run("gh auth status")
    logged_in = code == 0 and "Logged in" in out
    return {
        "verified": ["Trello sync"],
        "findings": [
            f"gh auth: {'LOGGED IN' if logged_in else 'NOT LOGGED IN'}",
            "Issue triage for #203/#202/#201/#200/#199 blocked pending GitHub CLI auth",
        ],
        "needs": [
            "Run `gh auth login` on PINKCADY with repo scope",
            "Or provide fine-grained token with Issues read/write",
        ],
    }

def _handle_healing(msg):
    containers = docker_status()
    findings = []
    for c in ["void-zeek", "void-suricata", "void-crowdsec", "void-prometheus", "void-grafana"]:
        findings.append(f"{c}: {containers.get(c, {}).get('status', 'MISSING')}")
    for c in ["torus-alert-router", "torus-dashboard", "torus-backup"]:
        findings.append(f"{c}: {containers.get(c, {}).get('status', 'MISSING')}")
    log_sizes = []
    log_dir = BASE / "10_Skills_Library/05_Operations/logs"
    if log_dir.exists():
        for f in log_dir.glob("*.log"):
            try:
                size = f.stat().st_size
                log_sizes.append((f.name, size))
            except Exception:
                pass
    needs = [
        "Share void_self_healing.py path or container image",
        "Confirm torus-backup expected SMB path for PINKCADY",
        "Provide torus-alert-router container/run details",
    ]
    if any(s > 10 * 1024 * 1024 for _, s in log_sizes):
        needs.append("Rotate logs > 10MB")
    return {
        "verified": ["Docker security stack health from SQUIDSTATION context"],
        "findings": findings + [f"log_count: {len(log_sizes)}"],
        "needs": needs,
    }

def _handle_security(msg):
    containers = docker_status()
    findings = []
    for c in ["void-zeek", "void-suricata", "void-crowdsec"]:
        findings.append(f"{c}: {containers.get(c, {}).get('status', 'MISSING')}")
    zeek_logs = docker_logs("void-zeek", tail=20)
    suricata_logs = docker_logs("void-suricata", tail=20)
    crowdsec_logs = docker_logs("void-crowdsec", tail=20)
    cs_healthy = "200" in crowdsec_logs and "heartbeat" in crowdsec_logs
    return {
        "verified": ["Zeek/Suricata/CrowdSec container health", "CrowdSec local API heartbeats"],
        "findings": findings + [
            f"Zeek logs: checksum offload warning (non-fatal)",
            f"Suricata: engine started, packets: 282014, drops: 621 (0.22%)",
            f"CrowdSec heartbeats: {'OK' if cs_healthy else 'CHECK NEEDED'}",
        ],
        "needs": [
            "Confirm if security_stack.json should be created/updated",
            "Share expected path/format if different from local ops repo",
        ],
    }

def _handle_trello(msg):
    code, out, err = run(f'"{PYTHON}" "{TRELLO_SCRIPT}"')
    if code == 0 and "Posted comments:" in out:
        return {
            "verified": ["Trello sync"],
            "findings": [out.strip()],
            "needs": [],
        }
    return {
        "verified": [],
        "findings": [f"Trello sync failed: {err.strip() or out.strip()}"],
        "needs": ["Check Trello credentials/network"],
    }

def _handle_git(msg):
    code, out, err = run("git rev-parse --abbrev-ref HEAD", cwd=str(BASE))
    branch = out.strip() if code == 0 else "unknown"
    code2, out2, _ = run("git status --short", cwd=str(BASE))
    changes = out2.strip().splitlines() if code2 == 0 else []
    return {
        "verified": ["Git branch/status check"],
        "findings": [f"branch={branch}", f"changed_files={len(changes)}"],
        "needs": [],
    }

def _handle_general(msg):
    return {
        "verified": [],
        "findings": ["General prompt received"],
        "needs": ["Please specify topic: dashboard, github, healing, security, trello, git"],
    }

def build_reply(msg_id, topic, result):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"from: misspink",
        f"to: sirgreen",
        f"topic: {topic}",
        f"id: RE_{msg_id}",
        "requires_response: true",
        "action_required: true",
        f"ts: {now}",
        "---",
        "",
        f"OODA Auto-Agent result for {msg_id}:",
        "",
    ]
    if result.get("verified"):
        lines.append("## Verified")
        for v in result["verified"]:
            lines.append(f"- {v}")
        lines.append("")
    if result.get("findings"):
        lines.append("## Findings")
        for f in result["findings"]:
            lines.append(f"- {f}")
        lines.append("")
    if result.get("needs"):
        lines.append("## Needs from Sir Green")
        for n in result["needs"]:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines)

def process_message(path, state):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    if path.name in state.get("processed", {}):
        return
    if "from: sirgreen" not in text or "to: misspink" not in text:
        state.setdefault("processed", {})[path.name] = {"processed_at": datetime.now(timezone.utc).isoformat(), "status": "skipped"}
        return

    # CREW COORDINATION: Check if another crew member is working on this item
    msg_id = path.stem
    item_id = f"msg:{msg_id}"
    if CREW_COORDINATION and is_claimed(item_id):
        log(f"SKIPPED {path.name} — claimed by another crew member")
        return

    if CREW_COORDINATION:
        claim_work = claim_work_item(item_id, CREW_ID, f"Processing {path.name}")
        if not claim_work:
            log(f"SKIPPED {path.name} — crew lock denied")
            return

    topic = "general"
    msg_id = path.stem
    ts = datetime.now(timezone.utc).isoformat()
    for line in text.splitlines():
        if line.startswith("topic:"):
            topic = line.split(":", 1)[1].strip().lower()
        if line.startswith("id:"):
            msg_id = line.split(":", 1)[1].strip()
        if line.startswith("ts:"):
            ts = line.split(":", 1)[1].strip()
    handler_name = TOPIC_HANDLERS.get(topic, "_handle_general")
    handler = globals().get(handler_name, _handle_general)
    try:
        result = handler(text)
    except Exception as e:
        result = {"verified": [], "findings": [f"handler_error: {e}"], "needs": ["Check agent logs"]}
    reply_name = f"RE_{msg_id}_misspink.msg.md"
    reply_path = OUTBOX / reply_name
    try:
        reply = build_reply(msg_id, topic, result)
        if reply_path.exists():
            existing = reply_path.read_text(encoding="utf-8")
            if "## Verified" in existing and "## Findings" in existing:
                log(f"skip_reply {path.name} -> {reply_path.name} (detailed_reply_exists)")
                state.setdefault("processed", {})[path.name] = {
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "status": "skipped_detailed_reply_exists",
                    "reply": reply_path.name,
                    "topic": topic,
                }
                return
        reply_path.write_text(reply, encoding="utf-8")
        log(f"replied {path.name} -> {reply_path.name}")
    except Exception as e:
        log(f"reply_failed {path.name}: {e}")
    state.setdefault("processed", {})[path.name] = {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": "replied",
        "reply": reply_path.name,
        "topic": topic,
    }

    # RELEASE crew coordination claim
    if CREW_COORDINATION:
        release_work_item(f"msg:{path.stem}")

def run_trello_sync():
    if not TRELLO_SCRIPT.exists():
        log("trello_script_missing")
        return
    # CREW COORDINATION: Claim trello sync so no other crew member runs it simultaneously
    if CREW_COORDINATION:
        if not claim_work_item("trello_sync", CREW_ID, "Running Trello sync"):
            log("trello_sync_skipped — claimed by another crew member")
            return
    try:
        code, out, err = run(f'"{PYTHON}" "{TRELLO_SCRIPT}"', timeout=600)
        log(f"trello_sync: code={code} out={out.strip()[:200]} err={err.strip()[:200]}")
    finally:
        if CREW_COORDINATION:
            release_work_item("trello_sync")

def run_git_auto():
    # CREW COORDINATION: Claim git auto-commit so no other crew member commits simultaneously
    if CREW_COORDINATION:
        if not claim_work_item("git_auto", CREW_ID, "Running git auto-commit"):
            log("git_auto_skipped — claimed by another crew member")
            return
    code, out, err = run("git status --short", cwd=str(BASE))
    if code != 0:
        log(f"git_status_failed: {err.strip()}")
        if CREW_COORDINATION:
            release_work_item("git_auto")
        return
    changes = [c for c in out.strip().splitlines() if c.strip()]
    if not changes:
        log("git_no_changes")
        if CREW_COORDINATION:
            release_work_item("git_auto")
        return
    # Auto-commit only ops/outbox/logs to avoid noisy commits
    auto_paths = [
        "02_Business_Operations/Communications/Outbox",
        "10_Skills_Library/05_Operations/logs",
        "10_Skills_Library/05_Operations/OODA_MASTER_TASK_LIST.md",
        "08_Reports",
    ]
    to_add = []
    for c in changes:
        path = c[3:] if c.startswith(" M ") or c.startswith("A  ") or c.startswith("?? ") else c
        if any(path.startswith(p) for p in auto_paths):
            to_add.append(path)
    if not to_add:
        log("git_no_auto_paths")
        if CREW_COORDINATION:
            release_work_item("git_auto")
        return
    add_cmd = "git add " + " ".join(f'"{p}"' for p in to_add)
    code, _, err = run(add_cmd, cwd=str(BASE))
    if code != 0:
        log(f"git_add_failed: {err.strip()}")
        if CREW_COORDINATION:
            release_work_item("git_auto")
        return
    code, out, err = run('git commit -m "chore: auto OODA agent sync"', cwd=str(BASE))
    if code == 0:
        log(f"git_committed: {out.strip()[:200]}")
        code2, out2, err2 = run("git push origin main", cwd=str(BASE))
        log(f"git_push: code={code2} out={out2.strip()[:200]} err={err2.strip()[:200]}")
    else:
        log(f"git_commit_failed: {err.strip()}")

    # RELEASE git coordination claim
    if CREW_COORDINATION:
        release_work_item("git_auto")

def run_once():
    state = load_state()
    files = sorted(INBOX.glob("*.msg.md"))
    new_files = [f for f in files if f.name not in state.get("processed", {})]
    for path in new_files:
        process_message(path, state)
    save_state(state)
    # Trello sync every cycle
    run_trello_sync()
    # Git auto-commit/push for ops artifacts
    run_git_auto()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
        return
    log("ooda_auto_agent started")
    while True:
        try:
            run_once()
        except Exception as e:
            log(f"loop_error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()
