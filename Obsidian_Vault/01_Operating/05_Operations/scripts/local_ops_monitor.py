#!/usr/bin/env python3
"""
Local Ops Monitor — Torus Coffee Company
Free-tier/local-only health checks for Pink's lanes.
Writes alerts to `logs/alerts.json`.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "logs" / "alerts.json"
API_URL = "http://127.0.0.1:8000/api/health"
WEBSITE_DIR = VAULT / "06_Website" / "next-storefront"
TASK_DAILY = r"\Torus_Daily_Obsidian_Note"
TASK_INVENTORY = r"\Torus_Inventory_Sync"
WATCHER_LOG = VAULT / "10_Skills_Library" / "05_Operations" / "Crew" / "pinkcady_comms.log"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_alerts() -> tuple[list, dict]:
    try:
        if LOG_FILE.exists():
            data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "alerts" in data:
                return data["alerts"], data
            if isinstance(data, list):
                return data, {"alerts": data}
    except Exception:
        pass
    return [], {"alerts": []}


def save_alerts(alerts: list, wrapper: dict) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        wrapper["alerts"] = alerts
        LOG_FILE.write_text(json.dumps(wrapper, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"ALERT_SAVE_FAIL {exc}")


def check_api() -> dict:
    try:
        import urllib.request
        with urllib.request.urlopen(API_URL, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_website_build() -> dict:
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "npm run build"],
            cwd=str(WEBSITE_DIR),
            capture_output=True,
            text=True,
            timeout=180,
            shell=False,
        )
        text = (result.stdout + "\n" + result.stderr).strip().splitlines()
        tail = "\n".join(text[-20:]) if text else ""
        return {"ok": result.returncode == 0, "code": result.returncode, "tail": tail}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_task_scheduler() -> list:
    jobs = []
    for name in [TASK_DAILY, TASK_INVENTORY]:
        try:
            out = subprocess.run(
                ["cmd.exe", "/c", f"schtasks /Query /FO LIST /V /TN {name}"],
                capture_output=True,
                text=True,
                timeout=60,
                shell=False,
            ).stdout
            status = "unknown"
            for line in out.splitlines():
                if line.strip().startswith("Status:"):
                    status = line.split(":", 1)[1].strip()
                    break
            jobs.append({"name": name, "status": status, "raw_tail": out.splitlines()[-8:]})
        except Exception as exc:
            jobs.append({"name": name, "status": "error", "error": str(exc)})
    return jobs


def check_watcher_log() -> dict:
    try:
        if not WATCHER_LOG.exists():
            return {"ok": False, "error": "missing"}
        lines = WATCHER_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        tail = lines[-10:]
        scan_noise = sum(1 for line in tail if line.startswith("[") and "INBOX_SCAN" in line and "files=0" not in line)
        return {"ok": True, "total_lines": len(lines), "recent_scan_lines": scan_noise, "tail": tail}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def append_alert(alerts: list, alert_type: str, message: str, severity: str = "info") -> None:
    alerts.append({
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": now_iso(),
    })


def main() -> int:
    print("=" * 60)
    print("LOCAL OPS MONITOR")
    print("=" * 60)
    alerts, wrapper = load_alerts()

    api = check_api()
    if api["ok"]:
        data = api.get("data", {})
        print(f"✓ API health: {data.get('status')} | products={data.get('product_count')}")
        append_alert(alerts, "api_health", f"API ok: {data}", "info")
    else:
        print(f"✗ API health: {api.get('error')}")
        append_alert(alerts, "api_health", f"API failed: {api.get('error')}", "error")

    web = check_website_build()
    if web["ok"]:
        print("✓ Website build: success")
        append_alert(alerts, "website_build", "Website build success", "info")
    else:
        msg = f"Website build failed: code={web.get('code')} error={web.get('error')}"
        print(f"✗ {msg}")
        append_alert(alerts, "website_build", msg, "error")

    jobs = check_task_scheduler()
    for job in jobs:
        status = job.get("status", "unknown")
        name = job.get("name", "")
        if "Ready" in status or "Running" in status:
            print(f"✓ Task Scheduler {name}: {status}")
            append_alert(alerts, "task_scheduler", f"{name} {status}", "info")
        else:
            msg = f"Task Scheduler {name} status={status}"
            print(f"✗ {msg}")
            append_alert(alerts, "task_scheduler", msg, "error")

    watcher = check_watcher_log()
    if watcher.get("ok"):
        scan = watcher.get("recent_scan_lines", 0)
        total = watcher.get("total_lines", 0)
        print(f"✓ Watcher log: total={total} recent_scan_lines={scan}")
        append_alert(alerts, "watcher_log", f"Watcher log healthy: total={total} recent_scan_lines={scan}", "info")
    else:
        msg = f"Watcher log issue: {watcher.get('error')}"
        print(f"✗ {msg}")
        append_alert(alerts, "watcher_log", msg, "error")

    save_alerts(alerts, wrapper)
    print("\n✓ Alerts written")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
