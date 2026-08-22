#!/usr/bin/env python3
"""
Zapier Integration Script - Torus Coffee Company
Connects vault to Zapier via webhooks and API.
"""
import os
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
CONFIG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "scripts" / "zapier_config.json"

logger = logging.getLogger('zapier')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

def load_config():
    """Load Zapier configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "zapier_webhook_url": None,
        "zaps": [],
        "last_sync": None
    }

def save_config(config):
    """Save Zapier configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_existing_webhook():
    """Load webhook URL from vault credentials."""
    try:
        from automation_core import get_credential
        url = get_credential('zapier', 'webhook_url')
        if url:
            config = load_config()
            config['zapier_webhook_url'] = url
            save_config(config)
            logger.info("✓ Loaded Zapier webhook URL from vault credentials")
            return url
    except Exception as e:
        logger.warning(f"⚠ Could not load credentials: {e}")
    return None

def send_to_zapier(data):
    """Send data to Zapier webhook."""
    config = load_config()
    if not config.get('auto_send_enabled', False):
        logger.info("Zapier auto-send disabled; skipping webhook delivery")
        return False
    webhook_url = config.get('zapier_webhook_url')
    if not webhook_url:
        logger.error("✗ No webhook URL configured. Run setup first.")
        return False
    
    try:
        import urllib.request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            logger.info(f"✓ Sent to Zapier: {data.get('type', 'unknown')}")
            return True
    except Exception as e:
        logger.error(f"✗ Failed to send to Zapier: {e}")
        return False

def sync_trello_to_vault():
    """Sync Trello cards to Obsidian vault."""
    print("\n=== TRELLO → VAULT SYNC ===\n")
    print("This feature requires:")
    print("1. Zapier webhook URL configured")
    print("2. Zapier Zap: Trello → Webhook")
    print("3. This script running as webhook receiver")
    print("\nManual sync: Use Trello API directly in vault scripts.")

def sync_social_to_vault():
    """Sync social media posts to vault."""
    print("\n=== SOCIAL MEDIA → VAULT SYNC ===\n")
    print("This feature requires:")
    print("1. Zapier webhook URL configured")
    print("2. Zapier Zap: Instagram/Twitter → Webhook")
    print("3. This script running as webhook receiver")

def create_zap_templates():
    """Create Zap templates for common workflows."""
    templates = [
        {
            "name": "Trello → Obsidian",
            "trigger": "Trello: New Card",
            "action": "Webhook: POST",
            "description": "Create Obsidian note when Trello card is created"
        },
        {
            "name": "Google Form → Trello",
            "trigger": "Google Forms: New Response",
            "action": "Trello: Create Card",
            "description": "Create vendor application card from form response"
        },
        {
            "name": "Email → Obsidian",
            "trigger": "Gmail: New Email",
            "action": "Webhook: POST",
            "description": "Save email to 00_Inbox"
        },
        {
            "name": "Calendar → Social Post",
            "trigger": "Google Calendar: New Event",
            "action": "Buffer: Create Post",
            "description": "Create social post for market event"
        },
        {
            "name": "Inventory Alert → Social Post",
            "trigger": "Google Sheets: New Row",
            "action": "Buffer: Create Post",
            "description": "Post when product is back in stock"
        }
    ]
    
    print("\n=== ZAP TEMPLATES ===\n")
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['name']}")
        print(f"   Trigger: {template['trigger']}")
        print(f"   Action: {template['action']}")
        print(f"   {template['description']}\n")
    
    return templates

def main():
    """Main automation entry point."""
    logger.info("=== TORUS COFFEE ZAPIER INTEGRATION ===")
    
    # Auto-load webhook from credentials if available
    if not load_config().get('zapier_webhook_url'):
        load_existing_webhook()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            load_existing_webhook()
        elif command == "trello":
            sync_trello_to_vault()
        elif command == "social":
            sync_social_to_vault()
        elif command == "templates":
            create_zap_templates()
        elif command == "status":
            config = load_config()
            print(f"Webhook URL: {config.get('zapier_webhook_url', 'Not set')}")
            print(f"Zaps configured: {len(config.get('zaps', []))}")
            print(f"Last sync: {config.get('last_sync', 'Never')}")
        elif command == "test":
            payload = {
                "type": sys.argv[2] if len(sys.argv) > 2 else "test",
                "data": json.loads(sys.argv[3]) if len(sys.argv) > 3 else {},
                "timestamp": datetime.now().isoformat()
            }
            send_to_zapier(payload)
        else:
            print(f"Unknown command: {command}")
            print("Usage: zapier_automation.py [setup|trello|social|templates|status|test]")
    else:
        create_zap_templates()

if __name__ == "__main__":
    main()
