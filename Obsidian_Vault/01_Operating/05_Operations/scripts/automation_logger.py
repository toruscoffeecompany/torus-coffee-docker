#!/usr/bin/env python3
"""
Logging & Reporting System for Torus Coffee Company Automations.

Collects status from all automation scripts and generates:
  1. Daily summary report (markdown)
  2. Weekly metrics dashboard
  3. Alert notifications for failures

Usage:
    venv/Scripts/python.exe scripts/automation_logger.py report daily
    venv/Scripts/python.exe scripts/automation_logger.py report weekly
    venv/Scripts/python.exe scripts/automation_logger.py report alerts
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
LOG_DIR = AUTOMATION_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = AUTOMATION_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = AUTOMATION_DIR / "logging_state.json"

# Scripts to monitor
MONITORED_SCRIPTS = [
    "master_ooda_loop.py",
    "smart_ticket_cycle.py",
    "pinkcady_comms_watcher.py",
    "miss_pink_inbox_watcher.py",
    "daily_ops_automation.py",
    "social_media_automation.py",
    "buffer_automation.py",
    "zapier_automation.py",
    "hubspot_crm.py",
    "inventory_to_website_sync.py",
    "order_manager.py",
    "unified_automation_orchestrator.py",
]

ALERT_THRESHOLD = 3  # alert after 3 consecutive failures


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_local():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"script_status": {}, "failure_streaks": {}, "last_report": {}}
    return {"script_status": {}, "failure_streaks": {}, "last_report": {}}


def save_state(state: dict):
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def collect_script_status() -> dict:
    """Collect last-run status from logs and orchestrator state."""
    state = load_state()
    statuses = {}

    # Check orchestrator state for last run results
    orch_state = AUTOMATION_DIR / "orchestration_state.json"
    if orch_state.exists():
        try:
            orch = json.loads(orch_state.read_text(encoding="utf-8"))
            if orch.get("runs"):
                last_run = orch["runs"][-1]
                for step in last_run.get("steps", []):
                    statuses[step["script"]] = {
                        "status": step["status"],
                        "duration": step.get("duration", 0),
                        "error": step.get("error"),
                        "timestamp": last_run["timestamp"],
                    }
        except Exception:
            pass

    # Check individual script logs
    for script in MONITORED_SCRIPTS:
        log_file = LOG_DIR / (script.replace(".py", ".log"))
        if log_file.exists():
            try:
                content = log_file.read_text(encoding="utf-8", errors="ignore")
                last_lines = content.strip().split("\n")[-10:]
                last_error = None
                last_success = None
                for line in reversed(last_lines):
                    if "ERROR" in line or "FAILED" in line or "failed" in line:
                        last_error = line.strip()
                    if "SUCCESS" in line or "COMPLETE" in line or "OK" in line:
                        last_success = line.strip()
                if script not in statuses:
                    statuses[script] = {
                        "status": "success" if not last_error else "error",
                        "error": last_error,
                        "last_success": last_success,
                        "timestamp": now_iso(),
                    }
                else:
                    if last_error:
                        statuses[script]["error"] = last_error
            except Exception:
                pass

    # Check for running processes (PID file approach)
    pid_files = {
        "master_ooda_loop.py": LOG_DIR / "master_ooda_loop.pid",
        "pinkcady_comms_watcher.py": LOG_DIR / "pinkcady_comms_watcher.pid",
    }
    for script, pid_file in pid_files.items():
        if pid_file.exists():
            try:
                pid_str = pid_file.read_text().strip()
                if pid_str:
                    import subprocess
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid_str}"],
                        capture_output=True, text=True, timeout=10,
                    )
                    # FIX: ensure the script entry exists before adding 'running' key
                    if script not in statuses:
                        statuses[script] = {"status": "unknown", "timestamp": now_iso()}
                    if pid_str in result.stdout:
                        statuses[script]["running"] = True
                    else:
                        statuses[script]["running"] = False
            except Exception:
                if script not in statuses:
                    statuses[script] = {"status": "unknown", "timestamp": now_iso()}
                statuses[script]["running"] = "unknown"

    return statuses


def generate_daily_report() -> str:
    """Generate a daily markdown report of all automation status."""
    state = load_state()
    statuses = collect_script_status()

    report_time = now_local()
    report_path = REPORTS_DIR / f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"

    lines = [
        f"# Torus Coffee — Daily Automation Report",
        f"",
        f"**Generated:** {report_time}",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"",
        f"## Executive Summary",
        f"",
        f"| Script | Status | Duration | Last Error |",
        f"|--------|--------|----------|------------|",
    ]

    success_count = 0
    error_count = 0
    for script in MONITORED_SCRIPTS:
        s = statuses.get(script, {})
        status = s.get("status", "unknown")
        duration = s.get("duration", 0)
        error = s.get("error", "") or s.get("last_error", "")
        if error:
            error = error[:80]
        if status == "success":
            status_display = "✅ OK"
            success_count += 1
        elif status == "error":
            status_display = "❌ FAILED"
            error_count += 1
        else:
            status_display = "⏱️ N/A"
        lines.append(f"| {script} | {status_display} | {duration}s | {error} |")

    lines.extend([
        f"",
        f"**Totals:** {success_count} OK, {error_count} Failed, {len(MONITORED_SCRIPTS) - success_count - error_count} Unknown",
        f"",
        f"## Detailed Status",
        f"",
    ])

    for script in MONITORED_SCRIPTS:
        s = statuses.get(script, {})
        lines.append(f"### {script}")
        lines.append(f"- **Status:** {s.get('status', 'unknown')}")
        if s.get("duration"):
            lines.append(f"- **Duration:** {s['duration']}s")
        if s.get("error"):
            lines.append(f"- **Last Error:** `{s['error']}`")
        if s.get("running"):
            lines.append(f"- **Process Running:** {s['running']}")
        if s.get("last_success"):
            lines.append(f"- **Last Success:** {s['last_success']}")
        lines.append("")

    report_content = "\n".join(lines)
    report_path.write_text(report_content, encoding="utf-8")
    return f"{report_path.name}"


def generate_alerts_report() -> str:
    """Check for failure streaks and generate alerts."""
    state = load_state()
    statuses = collect_script_status()
    failure_streaks = state.setdefault("failure_streaks", {})

    alerts = []
    for script in MONITORED_SCRIPTS:
        s = statuses.get(script, {})
        status = s.get("status", "unknown")

        if status == "error":
            streak = failure_streaks.get(script, 0) + 1
            failure_streaks[script] = streak

            if streak >= ALERT_THRESHOLD:
                alerts.append({
                    "script": script,
                    "streak": streak,
                    "error": s.get("error", "Unknown error"),
                    "severity": "HIGH" if streak >= 10 else "MEDIUM",
                })
        else:
            failure_streaks[script] = 0

    # Generate alert report
    if not alerts:
        alert_text = "✅ No alerts — all systems running."
    else:
        alert_text = "🚨 ALERTS:\n"
        for a in alerts:
            alert_text += f"  [{a['severity']}] {a['script']}: {a['streak']} consecutive failures — {a['error']}\n"

    # Post alert to local outbox
    if alerts:
        alert_dir = VAULT / "02_Business_Operations" / "Communications" / "Outbox"
        alert_dir.mkdir(parents=True, exist_ok=True)
        alert_file = alert_dir / f"AUTOMATION_ALERT_{datetime.now().strftime('%Y%m%dT%H%M%SZ')}.md"
        alert_file.write_text(
            f"# Automation Alert Report\n\n{alert_text}\n\nGenerated by automation_logger.py\n",
            encoding="utf-8",
        )

    save_state(state)
    return alert_text


def generate_weekly_report() -> str:
    """Generate a weekly metrics report."""
    state = load_state()
    runs = state.get("runs", [])

    # Filter to last 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    week_runs = [
        r for r in runs
        if collect_iso(r.get("timestamp")) and collect_iso(r["timestamp"]) > cutoff
    ] if runs else []

    lines = [
        f"# Torus Coffee — Weekly Automation Metrics Report",
        f"",
        f"**Period:** Last 7 days (since {cutoff.strftime('%Y-%m-%d')})",
        f"**Generated:** {now_local()}",
        f"",
        f"## Orchestration Runs",
        f"",
        f"Total runs: {len(week_runs)}",
    ]

    total_steps = 0
    total_success = 0
    total_failed = 0
    avg_duration = 0

    for run in week_runs:
        summary = run.get("summary", {})
        total_steps += summary.get("total", 0)
        total_success += summary.get("success", 0)
        total_failed += summary.get("failed", 0)
        if summary.get("total"):
            run_dur = sum(s.get("duration", 0) for s in run.get("steps", []))
            avg_duration += run_dur

    if week_runs:
        avg_duration /= len(week_runs)

    lines.extend([
        f"Total steps executed: {total_steps}",
        f"Successful: {total_success} ({round(total_success/max(total_steps,1)*100)}%)",
        f"Failed: {total_failed} ({round(total_failed/max(total_steps,1)*100)}%)",
        f"Avg run duration: {round(avg_duration, 2)}s",
        f"",
        f"## Monitored Scripts",
        f"",
    ])

    for script in MONITORED_SCRIPTS:
        log_file = LOG_DIR / (script.replace(".py", ".log"))
        if log_file.exists():
            size = log_file.stat().st_size
            lines.append(f"- {script}: {size} bytes logged")
        else:
            lines.append(f"- {script}: no log file")

    report_path = REPORTS_DIR / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return f"{report_path.name}"


def collect_iso(dt_str: str):
    """Parse ISO timestamp, return datetime or None."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "report":
        print("Usage: automation_logger.py report <daily|weekly|alerts>")
        return 1

    report_type = sys.argv[2]

    if report_type == "daily":
        name = generate_daily_report()
        print(f"Daily report generated: {name}")
    elif report_type == "weekly":
        name = generate_weekly_report()
        print(f"Weekly report generated: {name}")
    elif report_type == "alerts":
        alert_text = generate_alerts_report()
        print(alert_text)
    else:
        print(f"Unknown report type: {report_type}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
