#!/usr/bin/env python3
"""
Order Manager for Torus Coffee Company.

Manages order lifecycle: creates records from Square payment confirmations,
syncs to Trello cards for fulfillment, and exports to HubSpot as deals.

Usage:
    venv/Scripts/python.exe scripts/order_manager.py --create-order \
        --sku TCC-NOCC-200 --quantity 1 \
        --customer-name "Jane Doe" --customer-email "jane@example.com" \
        --source website --payment-method square --square-link-id "abc123"

    venv/Scripts/python.exe scripts/order_manager.py --list-pending
    venv/Scripts/python.exe scripts/order_manager.py --list --status paid
"""
import json
import uuid
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
ORDERS = VAULT / "04_Products" / "orders.json"
INVENTORY = VAULT / "04_Products" / "inventory_master.json"


def generate_order_number():
    """Generate a human-readable order number: TCC-YYYY-NNN."""
    year = datetime.now(timezone.utc).year
    existing = json.loads(ORDERS.read_text(encoding="utf-8")) if ORDERS.exists() else {"orders": []}
    # Find highest sequence number for this year
    seq = 1
    for order in existing.get("orders", []):
        if order.get("orderNumber", "").startswith(f"TCC-{year}-"):
            num = int(order["orderNumber"].split("-")[-1])
            seq = max(seq, num + 1)
    return f"TCC-{year}-{seq:04d}"


def load_inventory():
    """Load products from inventory_master.json."""
    if not INVENTORY.exists():
        return []
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return data.get("products", [])


def find_product(sku, products):
    """Find a product by SKU."""
    for p in products:
        if p.get("sku") == sku:
            return p
    return None


def create_order(args):
    """Create a new order record."""
    products = load_inventory()
    product = find_product(args.sku, products)

    if not product:
        print(f"ERROR: Product with SKU '{args.sku}' not found in inventory")
        return False

    if not product.get("visible", False):
        print(f"WARNING: Product '{product['name']}' is not visible")

    price = product["price"]
    total = round(price * args.quantity, 2)

    order = {
        "id": str(uuid.uuid4()),
        "orderNumber": generate_order_number(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "source": args.source,
        "customer": {
            "name": args.customer_name,
            "email": args.customer_email,
            "phone": args.customer_phone or "",
        },
        "items": [
            {
                "sku": product["sku"],
                "name": product["name"],
                "price": price,
                "quantity": args.quantity,
            }
        ],
        "total": total,
        "payment": {
            "method": args.payment_method,
            "squarePaymentId": args.square_payment_id or "",
            "squareLinkId": args.square_link_id or "",
            "transactionFee": round(total * 0.029 + 0.30, 2) if args.payment_method == "square" else 0,
            "paidAt": datetime.now(timezone.utc).isoformat() if args.payment_method != "cash" else "",
        },
        "fulfillment": {
            "shippingMethod": args.shipping_method or "standard",
            "carrier": "",
            "trackingNumber": "",
            "shippedAt": "",
            "deliveredAt": "",
        },
        "notes": "",
        "trelloCardId": "",
    }

    # If payment method is square and paidAt is set, mark as paid
    if args.payment_method == "square" and order["payment"]["paidAt"]:
        order["status"] = "paid"

    # Load existing orders
    if ORDERS.exists():
        data = json.loads(ORDERS.read_text(encoding="utf-8"))
    else:
        data = {"schema": "orders_schema.json", "description": "", "count": 0, "orders": []}

    # Prepend new order (most recent first)
    data["orders"].insert(0, order)
    data["count"] = len(data["orders"])

    ORDERS.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"✅ Order created: {order['orderNumber']}")
    print(f"   Customer: {order['customer']['name']} ({order['customer']['email']})")
    print(f"   Product: {product['name']} x{args.quantity}")
    print(f"   Total: ${total:.2f}")
    print(f"   Status: {order['status']}")
    print(f"   Source: {order['source']}")
    print(f"   Payment: {order['payment']['method']}")
    if order["payment"]["transactionFee"]:
        print(f"   Fee (Square 2.9% + 30¢): ${order['payment']['transactionFee']:.2f}")
    print(f"   Net: ${total - order['payment']['transactionFee']:.2f}")

    return True


def list_orders(status_filter=None):
    """List orders, optionally filtered by status."""
    if not ORDERS.exists():
        print("No orders file found.")
        return

    data = json.loads(ORDERS.read_text(encoding="utf-8"))
    orders = data.get("orders", [])

    if not orders:
        print("No orders yet — ready for first sale! 🚀")
        return

    if status_filter:
        orders = [o for o in orders if o.get("status") == status_filter]

    print(f"\n{'='*80}")
    print(f"Order List — Showing {len(orders)} order(s)")
    if status_filter:
        print(f"Filter: status = {status_filter}")
    print(f"{'='*80}\n")

    for o in orders:
        print(f"  {o['orderNumber']} | {o['status']:10} | ${o['total']:7.2f} | {o['customer']['name']}")
        print(f"    Items: {len(o['items'])} | Source: {o['source']} | Payment: {o['payment']['method']}")
        print(f"    Created: {o['createdAt'][:10]} | Updated: {o['updatedAt'][:10]}")
        if o.get("trelloCardId"):
            print(f"    Trello: {o['trelloCardId']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Torus Coffee Order Manager")
    parser.add_argument("--create-order", action="store_true", help="Create a new order")
    parser.add_argument("--list", action="store_true", help="List all orders")
    parser.add_argument("--list-pending", action="store_true", help="List pending orders")
    parser.add_argument("--sku", required=False, help="Product SKU")
    parser.add_argument("--quantity", type=int, default=1, help="Quantity")
    parser.add_argument("--customer-name", required=False, help="Customer name")
    parser.add_argument("--customer-email", required=False, help="Customer email")
    parser.add_argument("--customer-phone", default="", help="Customer phone")
    parser.add_argument("--source", default="website",
                        choices=["website", "instagram", "tiktok", "facebook", "phone", "wholesale", "flea_market", "subscription"],
                        help="Order source")
    parser.add_argument("--payment-method", default="square",
                        choices=["square", "paypal", "cash", "venmo", "check"],
                        help="Payment method")
    parser.add_argument("--square-payment-id", default="", help="Square payment ID")
    parser.add_argument("--square-link-id", default="", help="Square payment link ID")
    parser.add_argument("--shipping-method", default="standard",
                        choices=["standard", "expedited", "local_pickup", "digital"],
                        help="Shipping method")
    parser.add_argument("--status", help="Filter orders by status")

    args = parser.parse_args()

    if args.create_order:
        if not args.sku or not args.customer_name or not args.customer_email:
            print("ERROR: --sku, --customer-name, and --customer-email are required for --create-order")
            return 1
        success = create_order(args)
        return 0 if success else 1
    elif args.list_pending:
        list_orders("pending")
        return 0
    elif args.list:
        list_orders(args.status)
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
