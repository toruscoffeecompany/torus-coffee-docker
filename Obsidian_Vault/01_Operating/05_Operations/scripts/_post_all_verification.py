#!/usr/bin/env python3
"""Post correct Trello comments for all completed cards."""
import json, sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

comments = {
    # Fleet comms watcher
    "6a752e3eff4d9d4cca8945a1": """[2026-08-08T22:15:00Z] OODA status: ✅ FLEET COMMS WATCHER — DEPLOYED.
Evidence:
- scripts/pinkcady_comms_watcher.py created (file-based inbox watcher)
- Watches /z/Developer_Brain/Shared_With_Pink/PINKCADY_INBOX/ for *.msg.md
- Skips RE_/AUTO_ prefixed files (reply-loop suppression per COMMS_SCHEMA)
- Creates Trello cards on Torus_Ops board (Backlog list) for new messages
- Replies to shared inbox with structured status format
- Archives processed messages to PINKCADY_ARCHIVE
- State saved to .pinkcady_comms_state.json — no reprocessing after crashes
- Local outbox fallback when Z: write-blocked
- 3 messages from Sir Green processed (Trello setup confirmation replied)
- py_compile syntax check: PASS

Note: Inbox currently has 122 RE_/AUTO_ reply files from Sir Green's auto-loop — all correctly skipped. Only 3 markdown messages remain (Trello setup instructions) — reply posted to shared inbox.""",

    # Order management
    "6a714fb860bbdbb20853d4a4": """[2026-08-08T22:15:00Z] OODA status: ✅ ORDER MANAGEMENT WORKFLOW — COMPLETE.
Evidence:
- 04_Products/orders_schema.json created (JSON schema for order records)
- 04_Products/orders.json initialized (empty array with schema reference)
- scripts/order_manager.py created (create/list orders from inventory)
- app/api/orders/route.ts created (POST + GET endpoints)
- Tested: --list shows no orders, --create-order creates TCC-2026-0001 successfully
- Order includes: customer, items, payment (Square fee auto-calc), fulfillment, Trello link
- Square 2.9% + 30¢ fee auto-calculated = $0.70 on $13.96 order""",

    # Inventory sync
    "6a714fb82b64998c93bdbad4": """[2026-08-08T22:20:00Z] OODA status: ✅ INVENTORY → WEBSITE SYNC — COMPLETE.
Evidence:
- scripts/inventory_to_website_sync.py created (--dry-run and --apply modes)
- inventory_master.json has squarePaymentLink for all 10 visible products
- products.ts regenerated with correct SKUs from inventory (was using old placeholder SKUs)
- All 10 visible products synced: SKUs, prices, images, descriptions, payment links
- --apply run successfully: 10 products synced, 18,140 bytes written
- productHelpers.ts image map verified compatible""",

    # Bug hunt — consolidated
    "6a712433d986e5476af125d7": """[2026-08-08T22:20:00Z] OODA status: ✅ BUG HUNT — COMPLETE (all 8 scripts).
Evidence:
- social_media_automation.py: Fixed auto_send_enabled default (was missing → Zapier always skipped delivery)
- buffer_automation.py: Implemented create_text_post() (was stub 'not_implemented' → now creates real Buffer posts)
- daily_ops_automation.py: Fixed inventory path (was Current.xlsx → now inventory_master.json) + removed os.chdir() side effect
- weekly_review_automation.py: No bugs found — runs clean
- monthly_review_automation.py: No bugs found — runs clean
- zapier_automation.py: No bugs found — runs clean
- hubspot_crm.py: Fixed credential key ('token' → 'hubspot_api_key' with fallback) + import_vault_contacts() now actually scans vault + fixed UnboundLocalError token scoping
- inventory_tracker.py: No bugs found — runs clean
- All 8 scripts pass py_compile syntax checks
- Tested: daily_ops, social_media, buffer status, hubspot import (dry-run) all run successfully""",

    # HubSpot import
    "6a71242f938a65812243a9a9": """[2026-08-08T22:20:00Z] OODA status: ✅ HUBSPOT IMPORT SCRIPT — COMPLETE.
Evidence:
- scripts/hubspot_crm.py import_vault_contacts() function implemented (was stub)
- Scans: markdown files (Vendor_Packet_Checklist.md), CSV files (vendor/customer/contact), orders.json
- Email regex pattern matching + name extraction from surrounding text
- Dry-run mode when API key is placeholder (REPLACE_WITH)
- Tested: found 1 order customer (jane@example.com) → dry-run import successful
- HubSpot credentials: needs API key (currently placeholder)""",

    # Runbook
    "6a7124389e62f6bd1c35b508": """[2026-08-08T22:25:00Z] OODA status: ✅ AUTOMATION RUNBOOK — CREATED.
Evidence:
- 10_Skills_Library/05_Operations/Automation_Runbook.md created
- 7 common failure modes documented (popups, stale processes, Docker, Trello 401, Next.js, Buffer, HubSpot)
- Daily/Weekly/Monthly checklists
- 14 recovery scripts documented
- 15-script inventory table
- Includes cmd popup elimination audit + Docker healthcheck verification""",
}

for card_id, comment in comments.items():
    resp = requests.post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        params={"key": key, "token": token},
        json={"text": comment}, timeout=20
    )
    print(f"Card {card_id[:8]}: {resp.status_code}")
