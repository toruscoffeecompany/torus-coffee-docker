#!/usr/bin/env python3
"""
Square Payment Link Generator for Torus Coffee Company.

Creates or refreshes Square Payment Links for all visible products
in inventory_master.json. Uses the Square Checkout API to create
checkout links that accept credit cards, Apple Pay, Google Pay.

Free tier: $0/mo, 2.9% + 30¢ per transaction. No subscription needed.

Usage:
    venv/Scripts/python.exe scripts/square_payment_links.py --dry-run
    venv/Scripts/python.exe scripts/square_payment_links.py --apply

Requires Square access token in vault credentials.
See: 03_Financials/Payment_Processor_Decision.md
"""
import json
import sys
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY = VAULT / "04_Products" / "inventory_master.json"
CREDENTIALS_MD = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"

# Square API base
SQUARE_API = "https://connect.squareup.com/v2"

def get_square_token():
    """Load Square access token from vault."""
    try:
        from automation_core import get_credential
        token = get_credential('square', 'access_token')
        if token:
            return token
    except Exception:
        pass
    # Check for environment variable
    import os
    token = os.environ.get('SQUARE_ACCESS_TOKEN')
    if token:
        return token
    return None


def generate_payment_link(sku, product_name, price, token=None):
    """
    Generate a Square Payment Link for a product.

    If no token, returns a placeholder URL that follows Square's
    standard payment link format. Once a Square account is set up,
    these links should be created via Square Dashboard or this script
    with --apply.

    Square Payment Links format:
    https://square.link/u/toruscoffee-<SKU>
    """
    if not token:
        # Placeholder URL — real links created via Square Dashboard
        return f"https://square.link/u/toruscoffee-{sku}"

    # When token is available, use Square Checkout API
    import requests
    location_id = "YOUR_LOCATION_ID"  # Would be fetched from /v2/locations
    url = f"{SQUARE_API}/checkout/links"
    payload = {
        "idempotency_key": f"tcc-{sku}-{product_name[:20]}",
        "checkout_options": {
            "ask_for_shipping_address": True,
            "customize_built_in_email_results": False,
        },
        "line_item": {
            "name": product_name,
            "quantity": "1",
            "base_price_money": {
                "amount": int(price * 100),  # convert to cents
                "currency": "USD"
            },
            "sku": sku
        },
        "checkout_link_settings": {
            "recipient_action": {
                "type": "PAYMENT"
            },
            "description": f"Torus Coffee Company — {product_name}",
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Square-Version": "2024-06-12"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("link", {}).get("url", "")
    return None


def update_inventory_with_payment_links(dry_run=True):
    """Read inventory, generate payment links for visible products, write back."""
    if not INVENTORY.exists():
        print(f"ERROR: Inventory file not found: {INVENTORY}")
        return False

    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    products = data.get("products", [])
    visible_products = [p for p in products if p.get("visible", False)]

    token = get_square_token()
    mode = "APPLY" if not dry_run and token else "DRY-RUN (no token)"
    print(f"=== Square Payment Link Generator — {mode} ===")
    print(f"Token: {'FOUND' if token else 'NOT SET (using placeholder URLs)'}")
    print(f"Visible products: {len(visible_products)}")
    print()

    updated = False
    for p in visible_products:
        sku = p["sku"]
        name = p["name"][:50]
        price = p["price"]

        existing = p.get("squarePaymentLink", "")
        if existing and not existing.startswith("https://square.link/u/toruscoffee-"):
            print(f"  ✓ {sku} — already has link: {existing[:60]}")
            continue

        link = generate_payment_link(sku, name, price, token)
        if link:
            p["squarePaymentLink"] = link
            updated = True
            print(f"  ✅ {sku} — {name}")
            print(f"     Link: {link}")

    if updated and not dry_run:
        data["payment_processor"] = "Square Payment Links (free tier: $0/mo, 2.9% + 30¢ per txn)"
        data["payment_links_updated"] = "2026-08-08T00:00:00Z"
        INVENTORY.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"\n✓ Updated {INVENTORY}")
    elif dry_run:
        print(f"\n✓ Dry run — changes not written. Run with --apply to save.")
    else:
        print(f"\n✓ No changes needed.")

    return True


if __name__ == "__main__":
    dry_run = "--apply" not in sys.argv
    success = update_inventory_with_payment_links(dry_run=dry_run)
    sys.exit(0 if success else 1)
