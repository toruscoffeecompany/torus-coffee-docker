#!/usr/bin/env python3
"""Self-learning/self-correcting automation wrapper.
Runs a suite of automation checks and attempts safe auto-remediation when failures match known patterns.
"""
import json
import os
import subprocess
import sys
import time
import traceback
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CREATE_NO_WINDOW

# Ensure Docker kubectl is available without relying on shell PATH
os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + r"C:\Users\torus\AppData\Local\Docker"

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_DIR = BASE / "10_Skills_Library" / "05_Operations" / "logs"
STATUS_FILE = BASE / "10_Skills_Library/05_Operations/automation_status.json"
HASH_FILE = BASE / "10_Skills_Library/05_Operations/file_hashes.json"

# Files to watchdog — git-tracked config files that Sir Green's processes may mutate.
# NOTE: Do NOT include auto-generated files (OODA_TASK_LIST.md, fleet_mesh_state.json)
# as those change legitimately on each OODA/scan cycle.
WATCHED_FILES = [
    "10_Skills_Library/05_Operations/Docker/torus-light/docker-compose.yml",
    "10_Skills_Library/05_Operations/Fleet_Tools_Deployment/tools/fleet_dashboard.py",
    "10_Skills_Library/05_Operations/secrets.local.json",
]

def file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

def load_hashes() -> dict:
    """Load previously saved file hashes."""
    if HASH_FILE.exists():
        try:
            return json.loads(HASH_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_hashes(hashes: dict):
    """Save current file hashes."""
    try:
        HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
        HASH_FILE.write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    except Exception:
        pass

def check_file_mutations() -> list:
    """Check for file mutations and attempt git auto-restore."""
    hashes = load_hashes()
    current = {}
    mutations = []
    
    for rel_path in WATCHED_FILES:
        full_path = BASE / rel_path
        if full_path.exists():
            h = file_hash(full_path)
            current[rel_path] = h
            
            if rel_path in hashes and hashes[rel_path] != h:
                # File has been mutated — attempt git restore
                mutations.append({"file": rel_path, "action": "mutated"})
                log(f"FILE_MUTATION_DETECTED: {rel_path} — attempting git restore")
                try:
                    subprocess.run(
                        ["git", "-C", str(BASE), "checkout", "--", rel_path],
                        capture_output=True, timeout=30,
                        creationflags=CREATE_NO_WINDOW,
                    )
                    # Verify restore worked
                    new_hash = file_hash(full_path)
                    if new_hash == hashes.get(rel_path):
                        mutations[-1]["action"] = "restored"
                        log(f"FILE_RESTORED: {rel_path} via git checkout")
                    else:
                        mutations[-1]["action"] = "restore_failed"
                        log(f"FILE_RESTORE_FAILED: {rel_path} — hash mismatch after git checkout")
                except Exception as e:
                    mutations[-1]["action"] = "restore_error"
                    mutations[-1]["error"] = str(e)
                    log(f"FILE_RESTORE_ERROR: {rel_path}: {e}")
    
    # Save current hashes for next cycle
    save_hashes(current)
    return mutations

# Scripts to run with --once flag (daemon-mode scripts)
SCRIPT_ONCE = [
    ("ooda", BASE / "10_Skills_Library/05_Operations/Crew/ooda_loop.py"),
    ("verifier", BASE / "10_Skills_Library/05_Operations/Crew/verifier_daemon.py"),
]

# One-shot scripts that exit on their own
SCRIPT_ONESHOT = [
    ("top10", BASE / "10_Skills_Library/05_Operations/scripts/trello_top10_sync.py"),
    ("board_audit", BASE / "10_Skills_Library/05_Operations/scripts/board_audit.py"),
    ("vault_audit", BASE / "10_Skills_Library/05_Operations/scripts/vault_audit.py"),
]

FIXES = {
    "dashboard_server": {
        "match": "No connection could be made because the target machine actively refused it",
        "action": "dashboard_unavailable",
    },
    "task_scheduler": {
        "match": "Missing interpreter path",
        "action": "reschedule_venv",
    },
}


def run_script(name: str, script: Path, once: bool = False, timeout: int = 60) -> dict:
    """Run a script and return a result entry."""
    entry = {"name": name, "script": str(script), "status": "unknown"}
    cmd = [sys.executable, str(script)]
    if once:
        cmd.append("--once")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
        )
        entry["exit_code"] = proc.returncode
        entry["stdout_tail"] = proc.stdout.strip().splitlines()[-8:]
        entry["stderr_tail"] = proc.stderr.strip().splitlines()[-8:]
        if proc.returncode == 0:
            entry["status"] = "ok"
        else:
            entry["status"] = "failed"
            text = proc.stderr + proc.stdout
            for fix_name, rule in FIXES.items():
                if rule["match"] in text:
                    entry["fix_triggered"] = fix_name
    except Exception as exc:
        entry["status"] = "error"
        entry["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    return entry


while True:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results = {"timestamp": datetime.now(timezone.utc).isoformat(), "checks": [], "fixes": []}
    
    # Check for file mutations before running scripts
    mutations = check_file_mutations()
    if mutations:
        for m in mutations:
            results["fixes"].append({"type": "file_mutation", "detail": m})
    
    for name, script in SCRIPT_ONCE:
        entry = run_script(name, script, once=True, timeout=60)
        results["checks"].append(entry)

    for name, script in SCRIPT_ONESHOT:
        entry = run_script(name, script, once=False, timeout=120)
        results["checks"].append(entry)

    STATUS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

    # Sleep between cycles
    time.sleep(300)  # Every 5 minutes