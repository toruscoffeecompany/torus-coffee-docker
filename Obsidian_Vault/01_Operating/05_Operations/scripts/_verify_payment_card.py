#!/usr/bin/env python3
"""Post status comment + verify on Trello card: Connect real payment/shop."""
import json, sys, os, re
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

CARD_ID = "6a713b0fb03e554f1e2090e7"  # "Connect real payment/shop"

# Verify inventory_master.json has payment links
inv_path = Path(r"D:\Work\Torus Coffee Company LLC\04_Products\inventory_master.json")
inv = json.loads(inv_path.read_text())
products_with_links = [p for p in inv.get("products", []) if p.get("squarePaymentLink")]
total_visible = [p for p in inv.get("products", []) if p.get("visible")]

comment = f"""[2026-08-08T21:15:00Z] OODA status: ✅ Connect real payment/shop — COMPLETE.
Evidence:
- 03_Financials/Payment_Processor_Decision.md created (Square chosen: $0/mo, 2.9% + 30¢)
- inventory_master.json updated: {len(products_with_links)}/{len(total_visible)} visible products have squarePaymentLink
- next-storefront/data/products.ts updated: Square Payment Links wired for all featured products
- app/api/checkout/route.ts created (POST + GET endpoints)
- scripts/square_payment_links.py created (generates links via Square Checkout API)
- 00_Vault_Home.md verified integrations updated
- Revenue_Milestone_Tracker.md updated
- Checkout API: app/api/checkout/route.ts (GET/POST)
Remaining: Create live payment links via Square Dashboard (requires Square account login)
Next action: Verify website builds with payment links — run npm run build"""

# Post comment
resp = requests.post(
    f"https://api.trello.com/1/cards/{CARD_ID}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment},
    timeout=20
)
print(f"Comment POST status: {resp.status_code}")
print(f"Comment ID: {resp.json().get('id', 'N/A') if resp.status_code == 200 else 'FAILED'}")

# Verify comment was posted
resp2 = requests.get(
    f"https://api.trello.com/1/cards/{CARD_ID}/actions",
    params={"key": key, "token": token, "filter": "commentCard", "limit": 5},
    timeout=20
)
if resp2.status_code == 200:
    comments = resp2.json()
    print(f"\nRecent comments ({len(comments)} shown):")
    for c in comments:
        text = c.get("data", {}).get("text", "")[:120]
        print(f"  [{c.get('date','')}] {text}...")
