#!/usr/bin/env python3
"""
Centralized alert router for Torus Coffee Company.
Routes alerts to appropriate channels based on severity.
"""
import json
import logging
import os
import urllib.request
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "logs"
ALERT_LOG = LOG_DIR / "alerts.json"
DASHBOARD_STATUS = VAULT / "10_Skills_Library" / "05_Operations" / "automation_status.json"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "0") or "0")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
OBSIDIAN_VAULT = os.environ.get("OBSIDIAN_VAULT", str(VAULT))
_BOT_SECRETS = VAULT / "02_Business_Operations/Communications/Discord/miss_pink_bot/secrets.local.json"

EMAIL_COOLDOWN = 4 * 60 * 60
MAX_EMAILS_PER_DAY = 3

TIER1_ALERT_TYPES = {
    "inventory_zero": "URGENT: Inventory at zero",
    "system_down": "CRITICAL: System/service down",
    "auth_failure": "CRITICAL: Authentication failure",
}

def _can_send_email(alert_type: str) -> bool:
    if not ALERT_LOG.exists():
        return True
    try:
        with open(ALERT_LOG, "r", encoding="utf-8") as f:
            alerts = json.load(f)
    except json.JSONDecodeError:
        return True
    email_log = alerts.get("email_log", {})
    last_sent = email_log.get(alert_type)
    if not last_sent:
        return True
    elapsed = (datetime.now() - datetime.fromisoformat(last_sent)).total_seconds()
    return elapsed > EMAIL_COOLDOWN

def _record_email_sent(alert_type: str):
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ALERT_LOG, "r", encoding="utf-8") as f:
            alerts = json.load(f)
    except (FileNotFoundError, json.JSONError):
        alerts = {}
    alerts.setdefault("email_log", {})[alert_type] = datetime.now().isoformat()
    with open(ALERT_LOG, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)


def _update_dashboard_status(alert_type: str, message: str, severity: str = "info") -> None:
    entry = {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "ship": "PINKCADY",
    }
    data = {}
    if DASHBOARD_STATUS.exists():
        try:
            data = json.loads(DASHBOARD_STATUS.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data.setdefault("alerts", []).append(entry)
    if len(data.get("alerts", [])) > 200:
        data["alerts"] = data["alerts"][-200:]
    DASHBOARD_STATUS.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_bot_secrets() -> dict:
    try:
        if _BOT_SECRETS.exists():
            return json.loads(_BOT_SECRETS.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _send_discord_message(message: str) -> None:
    token = _load_bot_secrets().get("DISCORD_MISS_PINK_TOKEN") or _load_bot_secrets().get("DISCORD_BOT_TOKEN") or os.environ.get("DISCORD_MISS_PINK_TOKEN", "")
    channel_id = os.environ.get("DISCORD_CONFIRM_CHANNEL_ID", "")
    if not token or not channel_id:
        return
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
        })
        urllib.request.urlopen(req, timeout=10)
    except (OSError, Exception):
        pass


def _send_discord_webhook(message: str) -> None:
    webhook = DISCORD_WEBHOOK or _load_bot_secrets().get("DISCORD_WEBHOOK_URL", "")
    if not webhook:
        return
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        try:
            import requests as req
            req.post(webhook, data=payload, timeout=10)
        except Exception:
            from urllib.request import Request, urlopen
            req = Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            urlopen(req, timeout=10)
    except (OSError, Exception):
        pass

def _append_to_daily_note(message: str):
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = VAULT / "00_Inbox" / "01_Daily" / f"{today}.md"
    daily_file.parent.mkdir(parents=True, exist_ok=True)
    if daily_file.exists():
        content = daily_file.read_text(encoding="utf-8")
        if message not in content:
            daily_file.write_text(content + f"\n## Alert\n{message}\n", encoding="utf-8")
    else:
        daily_file.write_text(f"# Daily Ops Log - {today}\n\n## Alerts\n{message}\n", encoding="utf-8")

def _log_alert(alert: dict, channel: str):
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ALERT_LOG, "r", encoding="utf-8") as f:
            alerts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        alerts = {"alerts": []}
    alerts.setdefault("alerts", []).append(alert)
    if len(alerts["alerts"]) > 1000:
        alerts["alerts"] = alerts["alerts"][-1000:]
    with open(ALERT_LOG, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

def route_alert(alert_type: str, message: str, severity: str = "info"):
    alert = {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
    }
    if severity == "critical" and alert_type in TIER1_ALERT_TYPES:
        if _can_send_email(alert_type):
            subject = TIER1_ALERT_TYPES[alert_type]
            msg = f"{subject}: {message}"
            print(f"[EMAIL ALERT] {msg}")
            _log_alert({"type": "email", "subject": subject, "message": message}, "email")
            _record_email_sent(alert_type)
            _send_discord_webhook(msg)
        else:
            msg = f"[EMAIL SUPPRESSED - COOLDOWN] {message}"
            _append_to_daily_note(msg)
            _log_alert(alert, "email_suppressed")
    elif severity == "warning":
        msg = f"[WARNING] {message}"
        _append_to_daily_note(msg)
        _log_alert(alert, "obsidian")
        _send_discord_webhook(msg)
    elif severity == "info":
        msg = f"[INFO] {message}"
        _log_alert(alert, "log")
    else:
        msg = f"[DEBUG] {alert_type}: {message}"
        print(msg)
    _update_dashboard_status(alert_type, message, severity)

if __name__ == "__main__":
    route_alert("test", "Alert router test", "info")
    print("Alert router test complete")
