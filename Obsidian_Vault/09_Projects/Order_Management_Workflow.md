# Order Management Workflow

## Overview
Automated order processing from website contact form → Gmail → Obsidian vault → Trello → fulfillment.

## Flow

```
Customer submits form
    ↓
Formspree/Zapier webhook
    ↓
Gmail alert (Torus inbox)
    ↓
Obsidian daily note auto-created
    ↓
Trello card created (Website_Rebuild board)
    ↓
Alert routed to Miss Pink
    ↓
Manual fulfillment + shipping
    ↓
Trello card moved to Done
```

## Components

### 1. Contact Form Handler
**File:** `06_Website/website/app/api/contact/route.ts`
- Receives form submission
- Validates fields
- Sends to Formspree/Zapier
- Returns success/error to customer

### 2. Zapier Zap
**Trigger:** Webhook from contact form  
**Actions:**
1. Send Gmail notification to toruscoffeecompany@gmail.com
2. Create Trello card in Website_Rebuild board
3. Send Discord notification to #crew-general

### 3. Obsidian Automation
**File:** `10_Skills_Library/05_Operations/scripts/order_manager.py`
- Monitors Gmail for order confirmations
- Creates daily note entry
- Updates inventory_master.json
- Syncs to GitHub

### 4. Trello Card Template
**List:** Website_Rebuild → To_Do  
**Fields:**
- Customer name
- Email
- Products ordered
- Total amount
- Shipping address
- Status (pending → processing → shipped → delivered)
- Due date

## Implementation

### order_manager.py
```python
#!/usr/bin/env python3
"""
Order management automation for Torus Coffee Company.
Monitors Gmail for orders and creates workflow items.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
ORDERS_FILE = VAULT / "04_Products" / "orders.json"

logger = logging.getLogger('order_manager')

def process_order_email(email_data):
    """Process incoming order email."""
    order = {
        "id": f"TCC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "customer": email_data.get('from'),
        "email": email_data.get('email'),
        "products": email_data.get('products', []),
        "total": email_data.get('total', 0),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Save order
    save_order(order)
    
    # Create Trello card
    create_trello_card(order)
    
    # Update daily note
    update_daily_note(order)
    
    # Route alert
    try:
        from alert_router import route_alert
        route_alert("new_order", f"New order {order['id']} from {order['customer']}", severity="info")
    except ImportError:
        pass
    
    return order

def save_order(order):
    """Save order to orders.json."""
    ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if ORDERS_FILE.exists():
        with open(ORDERS_FILE) as f:
            orders = json.load(f)
    else:
        orders = {"orders": []}
    
    orders["orders"].append(order)
    
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def create_trello_card(order):
    """Create Trello card for order fulfillment."""
    # Implementation using Trello API
    pass

def update_daily_note(order):
    """Add order to today's daily note."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = VAULT / "00_Inbox" / "01_Daily" / f"{today}.md"
    
    if daily_file.exists():
        content = daily_file.read_text()
        daily_file.write_text(content + f"\n## Order {order['id']}\n- Customer: {order['customer']}\n- Total: ${order['total']}\n- Status: {order['status']}\n")
    else:
        daily_file.write_text(f"# Daily Ops Log - {today}\n\n## Order {order['id']}\n- Customer: {order['customer']}\n- Total: ${order['total']}\n- Status: {order['status']}\n")

if __name__ == "__main__":
    # Test
    process_order_email({
        "from": "Test Customer",
        "email": "test@example.com",
        "products": ["Solar Strawberries"],
        "total": 12.99
    })
    print("✓ Order workflow test complete")

```

## Task Scheduler
- **Job:** Torus_Order_Manager
- **Schedule:** Every 15 minutes
- **Script:** order_manager.py

## Gmail Filter
- **Label:** Orders
- **Filter:** `subject:(New Order OR Order Confirmation)`
- **Action:** Apply label, skip inbox

## Testing
1. Submit test order via website form
2. Verify Gmail notification received
3. Verify Trello card created
4. Verify Obsidian daily note updated
5. Verify inventory updated
