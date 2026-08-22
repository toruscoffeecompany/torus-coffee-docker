# Torus Coffee Alert System Design

## Current Problem
- Gmail flooded with "Torus Automation Alert" emails
- Emails sent from `toruscoffeecompany@gmail.com` → `toruscoffeecompany@gmail.com`
- Empty webhook payloads
- Likely Zapier Zap: Webhook → Gmail Send Email

## Alert Routing Design

### Tier 1: Critical Alerts → Email (ONLY for true emergencies)
- Inventory completely out of stock
- System/service down for >1 hour
- Security/authentication failure
- **Rate limit:** Max 1 email per 4 hours per alert type

### Tier 2: Warnings → Obsidian Only
- Low stock (<5 units)
- Task Scheduler job failed
- Git push failed
- Docker container unhealthy
- **Destination:** `00_Inbox/01_Daily/{date}.md`

### Tier 3: Info → Log Files Only
- Daily ops check passed
- Weekly review completed
- Social media status check
- Buffer/HubSpot/Trello connectivity
- **Destination:** `10_Skills_Library/05_Operations/logs/`

### Tier 4: Debug → Console Only
- Script execution traces
- API response details
- Test suite results
- **Destination:** stdout/stderr

## Implementation

### Alert Router Script
New file: `10_Skills_Library/05_Operations/scripts/alert_router.py`

```python
#!/usr/bin/env python3
"""
Centralized alert router for Torus Coffee Company.
Routes alerts to appropriate channels based on severity.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_DIR = VAULT / "10_Skills_Library" / "05_Operations" / "logs"
ALERT_LOG = LOG_DIR / "alerts.json"

# Alert thresholds
EMAIL_COOLDOWN = 4 * 60 * 60  # 4 hours in seconds
MAX_EMAILS_PER_DAY = 3

TIER1_SUBJECTS = {
    "inventory_zero": "URGENT: Inventory at zero",
    "system_down": "CRITICAL: System down",
    "auth_failure": "CRITICAL: Auth failure",
}

def route_alert(alert_type: str, message: str, severity: str = "info"):
    """
    Route alert to appropriate channel.
    
    Args:
        alert_type: Unique alert identifier
        message: Human-readable alert message
        severity: "critical", "warning", "info", "debug"
    """
    alert = {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Tier 1: Critical → Email (with cooldown)
    if severity == "critical" and alert_type in TIER1_SUBJECTS:
        if _can_send_email(alert_type):
            _send_email_alert(TIER1_SUBJECTS[alert_type], message)
            _record_email_sent(alert_type)
        else:
            _log_alert(alert, "email_skipped_cooldown")
    
    # Tier 2: Warning → Obsidian daily note
    elif severity == "warning":
        _append_to_daily_note(message)
        _log_alert(alert, "obsidian")
    
    # Tier 3: Info → Log file
    elif severity == "info":
        _log_alert(alert, "log")
    
    # Tier 4: Debug → Console only
    else:
        print(f"[DEBUG] {alert_type}: {message}")

def _can_send_email(alert_type: str) -> bool:
    """Check if we can send email (cooldown not elapsed)."""
    if not ALERT_LOG.exists():
        return True
    
    with open(ALERT_LOG) as f:
        alerts = json.load(f)
    
    email_log = alerts.get("email_log", {})
    last_sent = email_log.get(alert_type)
    
    if not last_sent:
        return True
    
    elapsed = (datetime.now() - datetime.fromisoformat(last_sent)).total_seconds()
    return elapsed > EMAIL_COOLDOWN

def _record_email_sent(alert_type: str):
    """Record that we sent an email for this alert type."""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    if ALERT_LOG.exists():
        with open(ALERT_LOG) as f:
            alerts = json.load(f)
    else:
        alerts = {}
    
    alerts.setdefault("email_log", {})[alert_type] = datetime.now().isoformat()
    
    with open(ALERT_LOG, "w") as f:
        json.dump(alerts, f, indent=2)

def _send_email_alert(subject: str, message: str):
    """Send email alert via Gmail API."""
    # Implementation requires gmail.send scope
    # For now, log to file and print
    print(f"[EMAIL ALERT] {subject}: {message}")
    _log_alert({"type": "email", "subject": subject, "message": message}, "email")

def _append_to_daily_note(message: str):
    """Append alert to today's daily note."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = VAULT / "00_Inbox" / "01_Daily" / f"{today}.md"
    
    if daily_file.exists():
        content = daily_file.read_text()
        if message not in content:  # Avoid duplicates
            daily_file.write_text(content + f"\n## Alert\n{message}\n")
    else:
        daily_file.write_text(f"# Daily Ops Log - {today}\n\n## Alerts\n{message}\n")

def _log_alert(alert: dict, channel: str):
    """Log alert to central log file."""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    if ALERT_LOG.exists():
        with open(ALERT_LOG) as f:
            alerts = json.load(f)
    else:
        alerts = {"alerts": []}
    
    alerts["alerts"].append(alert)
    
    # Keep only last 1000 alerts
    if len(alerts["alerts"]) > 1000:
        alerts["alerts"] = alerts["alerts"][-1000:]
    
    with open(ALERT_LOG, "w") as f:
        json.dump(alerts, f, indent=2)

if __name__ == "__main__":
    # Test alert
    route_alert("test", "Alert system test", "info")
    print("✓ Alert router test complete")

```

### Update Existing Scripts
Replace all `print()` alerts in:
- `inventory_alert.py`
- `daily_ops_automation.py`
- `social_media_automation.py`

With calls to `alert_router.route_alert()`.

## Gmail Filter Fix

### Manual Fix (NOW)
1. Open Gmail
2. Create filter: `subject:Torus Automation Alert`
3. Action: Delete it / Skip Inbox

### Programmatic Fix (LATER)
1. Regenerate Google OAuth token with `gmail.send` + `gmail.settings.basic` scopes
2. Create filter via API: `POST /gmail/v1/users/me/settings/filters`

## Zapier Redesign

### Remove Old Webhook Zap
1. Log into Zapier
2. Find Zap using webhook `4616r0w`
3. Delete or disable it

### New Zapier Setup (when ready)
Only create Zaps you actually need:
1. **Trello → Obsidian** (card created → vault note)
2. **Buffer → Gmail** (post published → confirmation)
3. **HubSpot → Gmail** (new contact → notification)

Do NOT create a generic "send everything to email" Zap.

## Trello Tracking
Cards will be created to track:
1. Gmail filter creation
2. Alert router implementation
3. Zapier Zap cleanup
4. Gmail scope regeneration

## Timeline
- **NOW:** Manual Gmail filter stops spam
- **TODAY:** Alert router script implemented
- **THIS WEEK:** Existing scripts updated to use router
- **NEXT:** Gmail scope fix for programmatic filter creation
