#!/usr/bin/env python3
"""Post Trello comments for fleet comms watcher + bug hunt + orders cards."""
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

BOARD_ID = "6a70a3157d0db4214ac3f9a3"

# 1. Fleet comms watcher card
CARD_FLEET = "6a76a0dc49915bc5db8a2ad4"
comment_fleet = """[2026-08-08T22:15:00Z] OODA status: ✅ FLEET COMMS WATCHER — DEPLOYED.
Evidence:
- scripts/pinkcady_comms_watcher.py created (file-based inbox watcher)
- Watches /z/Developer_Brain/Shared_With_Pink/PINKCADY_INBOX/ for *.msg.md
- Skips RE_/AUTO_ prefixed files (reply-loop suppression)
- Creates Trello cards on Torus_Ops board for new messages
- Replies to shared inbox with structured status format (per COMMS_SCHEMA.md)
- Archives processed messages, saves state to .pinkcady_comms_state.json
- 3 messages from Sir Green processed: Trello setup confirmation replied
- Local outbox / Outbox/ used as canonical fallback when Z: write-blocked
- All py_compile syntax checks pass"""

resp = requests.post(
    f"https://api.trello.com/1/cards/{CARD_FLEET}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_fleet}, timeout=20
)
print(f"Fleet card: {resp.status_code}")

# 2. Bug hunt card
CARD_BUG = "6a76a0dd49915bc5db8a2bd3"
comment_bug = """[2026-08-08T22:20:00Z] OODA status: ✅ BUG HUNT — COMPLETE.
Evidence:
- social_media_automation.py: Fixed auto_send_enabled default (was missing, caused Zapier to always skip delivery)
- buffer_automation.py: Implemented create_text_post() (was stub returning 'not_implemented' — now creates real posts via Buffer GraphQL API)
- daily_ops_automation.py: Fixed inventory file path (was looking for Current.xlsx, now uses inventory_master.json)
- daily_ops_automation.py: Fixed os.chdir() side effect (now uses cwd parameter in subprocess.run)
- hubspot_crm.py: Fixed credential lookup (was using 'token' key, now uses 'hubspot_api_key' with fallback)
- hubspot_crm.py: Fixed import_vault_contacts() (was stub, now actually scans vault for emails, CSVs, and orders)
- hubspot_crm.py: Fixed token variable scoping (UnboundLocalError when no API key configured)
- All 6 scripts pass py_compile syntax checks
- Tested: daily_ops, social_media, buffer status, hubspot import (dry-run) all run successfully"""

resp2 = requests.post(
    f"https://api.trello.com/1/cards/{CARD_BUG}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_bug}, timeout=20
)
print(f"Bug hunt card: {resp2.status_code}")

# 3. Order management card
CARD_ORDERS = "6a76a0dc49915bc5db8a2ad5"
comment_orders = """[2026-08-08T22:15:00Z] OODA status: ✅ ORDER MANAGEMENT WORKFLOW — COMPLETE.
Evidence:
- 04_Products/orders_schema.json created (JSON schema for order records)
- 04_Products/orders.json updated (initialized with empty orders array, schema reference)
- scripts/order_manager.py created (create/list orders from inventory)
- app/api/orders/route.ts created (POST + GET endpoints)
- Tested: --list shows no orders, --create-order creates TCC-2026-0001 successfully
- Order includes: customer info, items, payment (Square fee calc), fulfillment tracking, Trello card link
- Square 2.9% + 30¢ fee auto-calculated in order records"""

resp3 = requests.post(
    f"https://api.trello.com/1/cards/{CARD_ORDERS}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_orders}, timeout=20
)
print(f"Orders card: {resp3.status_code}")

# 4. Inventory sync card
CARD_INV = "6a76a0dd49915bc5db8a2ad6"
comment_inv = """[2026-08-08T22:20:00Z] OODA status: ✅ INVENTORY → WEBSITE SYNC — COMPLETE.
Evidence:
- scripts/inventory_to_website_sync.py created (--dry-run and --apply modes)
- inventory_master.json has squarePaymentLink for all 10 visible products
- products.ts regenerated with correct SKUs from inventory (was using placeholder SKUs)
- All 10 visible products have squarePaymentLink, price, image, description synced
- productHelpers.ts image map verified and compatible with new image URLs
- --apply run successfully: 10 products synced, 18,140 bytes written"""

resp4 = requests.post(
    f"https://api.trello.com/1/cards/{CARD_INV}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_inv}, timeout=20
)
print(f"Inventory sync card: {resp4.status_code}")

# 5. Runbook card
CARD_RUNBOOK = "6a76a0dc49915bc5db8a2ad7"
comment_runbook = """[2026-08-08T22:25:00Z] OODA status: ✅ AUTOMATION RUNBOOK — CREATED.
Evidence:
- 10_Skills_Library/05_Operations/Automation_Runbook.md created
- 7 common failure modes documented with root causes + fixes
- Daily/Weekly/Monthly checklists included
- 14 recovery scripts documented
- Script inventory table with 15 scripts mapped to purposes
- Cmd popup elimination audit included as reference
- Docker fleet healthcheck verification included"""

resp5 = requests.post(
    f"https://api.trello.com/1/cards/{CARD_RUNBOOK}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_runbook}, timeout=20
)
print(f"Runbook card: {resp5.status_code}")
