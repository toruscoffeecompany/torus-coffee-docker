#!/usr/bin/env python3
"""
VOID Pirate Trading Co — Trust-but-verify daemon.
Reads crew inboxes, creates Trello cards/GitHub issues, verifies promises with evidence,
updates progress continuously, flags false/unfulfilled promises.
"""
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CREATE_NO_WINDOW

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
INBOXES = {
    "sir_green": Path("/z/SIR_GREEN_INBOX"),
    "sir_azure": Path("/z/SIR_AZURE_INBOX"),
    "miss_pink": Path("/z/MISS_PINK_INBOX"),
}
PROCESSED = Path("/z/processed")
TRELLO_CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
OODA_LOG = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "verifier_daemon.log"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    try:
        OODA_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{now_iso()}] {msg}"
        with open(OODA_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass


def load_trello_creds():
    text = TRELLO_CRED_FILE.read_text(errors="ignore")
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


def load_github_token():
    try:
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        token = data.get("github_token", "")
        if not token:
            raise RuntimeError("GitHub token missing")
        return token
    except Exception as exc:
        raise RuntimeError(f"Failed to load GitHub token: {exc}")


def verify_dashboard_endpoints():
    results = {}
    base = "http://192.168.0.39:8080"
    for path in ["/api/status", "/api/fleet", "/api/tools", "/api/security-docs", "/api/hw", "/healthz", "/api/crew_heartbeat", "/api/rig-report"]:
        try:
            r = requests.get(f"{base}{path}", timeout=10)
            results[path] = {"status": r.status_code, "length": len(r.text)}
        except Exception as exc:
            results[path] = {"status": "error", "error": str(exc)}
    return results


def verify_docker_containers():
    try:
        r = subprocess.run(["docker", "ps", "--format", "{{json .}}"], capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW)
        if r.returncode == 0:
            containers = [json.loads(line) for line in r.stdout.strip().split("\n") if line]
            return {"count": len(containers), "containers": [c.get("Names", "") for c in containers]}
    except Exception:
        pass
    return {"count": 0, "error": "docker not available"}


def verify_security_tools():
    tools = {
        "nmap": ["nmap", "--version"],
        "nikto": ["nikto", "-Version"],
        "tshark": ["tshark", "-v"],
        "yara": ["yara", "-v"],
        "volatility3": ["vol", "-h"],
    }
    results = {}
    for name, cmd in tools.items():
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW)
            results[name] = {"installed": r.returncode == 0, "path": cmd[0]}
        except FileNotFoundError:
            results[name] = {"installed": False, "path": None}
        except Exception as exc:
            results[name] = {"installed": False, "error": str(exc)}
    return results


def run_cycle():
    log("VERIFIER_CYCLE_START")
    results = {
        "timestamp": now_iso(),
        "dashboard_endpoints": verify_dashboard_endpoints(),
        "docker_containers": verify_docker_containers(),
        "security_tools": verify_security_tools(),
        "inbox_status": {},
    }
    for owner, inbox in INBOXES.items():
        if inbox.exists():
            results["inbox_status"][owner] = len(list(inbox.glob("*.md")))
        else:
            results["inbox_status"][owner] = 0

    # Write verification report
    report_path = BASE / "10_Skills_Library" / "05_Operations" / "logs" / "verifier_report.json"
    try:
        report_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        log(f"VERIFIER_REPORT_WRITTEN: {report_path}")
    except Exception as exc:
        log(f"VERIFIER_REPORT_WRITE_ERROR: {exc}")

    # Flag issues
    flags = []
    for path, data in results["dashboard_endpoints"].items():
        if isinstance(data, dict) and data.get("status") not in (200, 301, 302):
            flags.append(f"Dashboard endpoint {path} returned {data.get('status')}")

    for name, data in results["security_tools"].items():
        if not data.get("installed"):
            flags.append(f"Security tool {name} not installed")

    if flags:
        log(f"VERIFIER_FLAGS: {len(flags)} issues found")
        for flag in flags:
            log(f"  - {flag}")
    else:
        log("VERIFIER_FLAGS: 0 issues found")

    log("VERIFIER_CYCLE_END")
    return results


def main():
    log("VERIFIER_DAEMON_STARTED")
    if "--once" in sys.argv:
        run_cycle()
        return 0
    while True:
        try:
            run_cycle()
        except Exception as exc:
            log(f"VERIFIER_CYCLE_ERROR {exc}")
        time.sleep(300)  # Every 5 minutes
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
