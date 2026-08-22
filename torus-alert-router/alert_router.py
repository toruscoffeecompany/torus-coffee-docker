#!/usr/bin/env python3
"""Torus Coffee Company Alert Router with integrations."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
import os
import requests
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("torus-alert-router")

app = FastAPI(title="Torus Alert Router")

CONFIG_DIR = Path(__file__).parent / "config"
ALERTS_DIR = Path("/data/alerts")
ALERTS_FILE = ALERTS_DIR / "alerts.json"

# Cooldown tracking (prevent alert spam)
_COOLDOWN_TRACKER = defaultdict(lambda: defaultdict(datetime.min))
COOLDOWN_MINUTES = 5

class Alert(BaseModel):
    severity: str
    service: str
    message: str
    details: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "torus-alert-router"}

@app.post("/alert")
def route_alert(alert: Alert):
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        record = {
            "timestamp": timestamp,
            "severity": alert.severity,
            "service": alert.service,
            "message": alert.message,
            "details": alert.details,
        }
        
        logger.info(f"[{alert.severity.upper()}] {alert.service}: {alert.message}")
        
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(ALERTS_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        # Load integration configs from env or files
        discord_config = _load_discord_config()
        gmail_config = _load_gmail_config()
        obsidian_config = _load_obsidian_config()
        
        # Check cooldown
        cooldown_key = f"{alert.service}:{alert.severity}"
        last_alert = _COOLDOWN_TRACKER["alerts"][cooldown_key]
        now = datetime.utcnow()
        
        if (now - last_alert).total_seconds() < (COOLDOWN_MINUTES * 60):
            logger.info(f"Alert cooldown active for {cooldown_key}")
            return {"status": "cooldown", "message": f"Rate limited (cooldown {COOLDOWN_MINUTES}m)"}
        
        _COOLDOWN_TRACKER["alerts"][cooldown_key] = now
        
        routed_channel = None
        
        # Route by severity
        if alert.severity == "critical":
            if gmail_config.get("enabled"):
                _send_email_alert(alert, gmail_config)
                routed_channel = "email"
            elif discord_config.get("enabled"):
                _send_discord_alert(alert, discord_config)
                routed_channel = "discord"
        
        elif alert.severity == "warning":
            if obsidian_config.get("enabled"):
                _send_obsidian_alert(alert, obsidian_config)
                routed_channel = "obsidian"
            elif discord_config.get("enabled"):
                _send_discord_alert(alert, discord_config)
                routed_channel = "discord"
        
        elif alert.severity == "info":
            if discord_config.get("enabled"):
                _send_discord_alert(alert, discord_config)
                routed_channel = "discord"
        
        routed_channel = routed_channel or "log"
        return {"status": "routed", "channel": routed_channel, "severity": alert.severity}
    
    except Exception as e:
        logger.error(f"Alert routing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
def get_alerts():
    try:
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, "r") as f:
                return {"alerts": [json.loads(line) for line in f if line.strip()]}
        return {"alerts": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Integration Helpers
# ============================================================================

def _load_discord_config():
    """Load Discord config from file or env."""
    # Try file first
    try:
        return json.loads((CONFIG_DIR / "discord.json").read_text())
    except Exception:
        pass
    
    # Try env vars
    webhook = os.getenv("DISCORD_WEBHOOK")
    if webhook:
        return {"enabled": True, "webhook_url": webhook}
    
    return {"enabled": False}

def _load_gmail_config():
    """Load Gmail config from file or env."""
    try:
        return json.loads((CONFIG_DIR / "gmail.json").read_text())
    except Exception:
        pass
    
    # Try env vars
    if os.getenv("SMTP_HOST") and os.getenv("SMTP_USER"):
        return {
            "enabled": True,
            "smtp_host": os.getenv("SMTP_HOST"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_user": os.getenv("SMTP_USER"),
            "smtp_pass": os.getenv("SMTP_PASS"),
            "smtp_to": os.getenv("SMTP_TO"),
        }
    
    return {"enabled": False}

def _load_obsidian_config():
    """Load Obsidian config from file or env."""
    try:
        return json.loads((CONFIG_DIR / "obsidian.json").read_text())
    except Exception:
        pass
    
    # Try env vars
    vault_path = os.getenv("OBSIDIAN_VAULT")
    if vault_path:
        return {"enabled": True, "vault_path": vault_path}
    
    return {"enabled": False}

def _send_discord_alert(alert: Alert, config: dict):
    """Send alert to Discord webhook."""
    try:
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            logger.warning("Discord webhook URL not configured")
            return
        
        # Color by severity
        color_map = {
            "critical": 16711680,  # Red
            "warning": 16776960,   # Yellow
            "info": 65280,         # Green
        }
        
        payload = {
            "embeds": [{
                "title": f"[{alert.severity.upper()}] {alert.service}",
                "description": alert.message,
                "color": color_map.get(alert.severity, 0),
                "fields": [
                    {"name": "Details", "value": alert.details or "N/A"},
                    {"name": "Time", "value": datetime.utcnow().isoformat() + "Z"},
                ] if alert.details else [],
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code == 204:
            logger.info(f"Discord alert sent: {alert.service}")
        else:
            logger.error(f"Discord webhook failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send Discord alert: {e}")

def _send_email_alert(alert: Alert, config: dict):
    """Send alert via SMTP (Gmail)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_host = config.get("smtp_host")
        smtp_port = config.get("smtp_port", 587)
        smtp_user = config.get("smtp_user")
        smtp_pass = config.get("smtp_pass")
        smtp_to = config.get("smtp_to")
        
        if not all([smtp_host, smtp_user, smtp_pass, smtp_to]):
            logger.warning("SMTP config incomplete")
            return
        
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = smtp_to
        msg["Subject"] = f"[{alert.severity.upper()}] Torus: {alert.service}"
        
        body = f"""Alert from Torus Coffee Company

Service: {alert.service}
Severity: {alert.severity.upper()}
Message: {alert.message}
Details: {alert.details or 'N/A'}
Time: {datetime.utcnow().isoformat()}Z
"""
        
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Email alert sent to {smtp_to}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")

def _send_obsidian_alert(alert: Alert, config: dict):
    """Send alert to Obsidian daily note."""
    try:
        vault_path = config.get("vault_path")
        if not vault_path:
            logger.warning("Obsidian vault path not configured")
            return
        
        vault_path = Path(vault_path)
        today = datetime.utcnow().date()
        daily_note = vault_path / "00_Inbox" / f"{today.isoformat()}.md"
        
        # Append to daily note
        entry = f"\n## ⚠️ [{alert.severity.upper()}] {alert.service}\n- **Message:** {alert.message}\n- **Details:** {alert.details or 'N/A'}\n- **Time:** {datetime.utcnow().isoformat()}Z\n"
        
        if daily_note.exists():
            with open(daily_note, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            with open(daily_note, "w", encoding="utf-8") as f:
                f.write(f"# {today.isoformat()}\n")
                f.write(entry)
        
        logger.info(f"Obsidian alert written to {daily_note}")
    except Exception as e:
        logger.error(f"Failed to send Obsidian alert: {e}")

@app.get("/config")
def get_config_status():
    """Show which integrations are enabled."""
    configs = {
        "discord": {"enabled": _load_discord_config().get("enabled", False)},
        "gmail": {"enabled": _load_gmail_config().get("enabled", False)},
        "obsidian": {"enabled": _load_obsidian_config().get("enabled", False)},
    }
    return {"integrations": configs}
