# Torus Coffee Company — Minimal API Layer

## Goal
Add a local-first, free-tier full-stack API for the website and business operations: **orders**, **customers**, **inventory**, and **basic admin** endpoints. Do not break the existing static Next.js storefront.

## Scope
- **Service**: FastAPI (Python) — zero cost, local SQLite, runs standalone.
- **Port**: `8000` (configurable via `.env`).
- **Database**: Existing `10_Skills_Library/05_Operations/data/torus_local.db` (SQLite). Read/write against the current schema.
- **Frontend coupling**: None. The existing `06_Website/next-storefront` remains a static export. The API is consumed by the dashboard or future dynamic pages.
- **Auth**: None for v1. Admin endpoints are protected by a simple static API key header (`X-Admin-Key`). See `.env.example`.

## Folder Structure
```
10_Skills_Library/05_Operations/api/
├── .env.example
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    ├── main.py
    ├── db.py
    ├── models.py
    ├── schemas.py
    └── routers/
        ├── __init__.py
        ├── products.py
        ├── customers.py
        ├── orders.py
        └── admin.py
```

## Endpoint Contract
### Products / Inventory
- `GET /api/products` — list products, filter by status/featured
- `GET /api/products/{slug}` — single product
- `PATCH /api/products/{id}/inventory` — adjust stock, logs adjustment row

### Customers
- `GET /api/customers` — list customers
- `POST /api/customers` — create customer
- `GET /api/customers/{id}` — single customer with order history

### Orders
- `GET /api/orders` — list orders, filter by status/date
- `POST /api/orders` — create order + order items, decrement inventory
- `GET /api/orders/{id}` — single order with items and customer

### Admin
- `GET /api/admin/health` — health + DB connection check
- `GET /api/admin/stats` — counts + low-stock alerts

## Data Contracts
All request/response bodies are JSON. Errors return `{"detail": "..."}` with standard HTTP status codes.

### Product Response Shape
```json
{
  "id": 1,
  "sku": "TCC-SDB-001",
  "name": "Star-Dusted Banana Crunch",
  "slug": "star-dusted-banana-crunch",
  "category": "Freeze-Dried Fruit",
  "status": "published",
  "price_cents": 899,
  "cost_cents": 350,
  "quantity_on_hand": 42,
  "low_stock_threshold": 5,
  "track_inventory": true,
  "main_image_url": null,
  "ingredients": "...",
  "allergens": "...",
  "storage_instructions": "...",
  "shelf_life": "...",
  "net_weight_oz": 1.5,
  "shipping_weight_oz": null,
  "ships_us_only": true,
  "requires_shipping": true,
  "seo_title": null,
  "seo_description": "...",
  "featured": true,
  "sort_order": 0,
  "created_at": "...",
  "updated_at": "..."
}
```

### Order Create Shape
```json
{
  "customer_id": 1,
  "status": "pending",
  "subtotal_cents": 1798,
  "tax_cents": 144,
  "shipping_cents": 599,
  "total_cents": 2541,
  "payment_method": "square",
  "payment_status": "pending",
  "shipping_name": "Jane Doe",
  "shipping_address_line1": "123 Main St",
  "shipping_city": "Des Moines",
  "shipping_state": "IA",
  "shipping_zip": "50309",
  "shipping_country": "US",
  "notes": null,
  "items": [
    { "product_id": 1, "quantity": 2, "unit_price_cents": 899, "subtotal_cents": 1798 }
  ]
}
```

## Run Instructions
```bash
cd 10_Skills_Library/05_Operations/api
pip install -r requirements.txt
cp .env.example .env
python run.py
# Docs: http://localhost:8000/docs
```

## Security Notes
- Do not commit `.env`.
- Redact secrets in logs/configs.
- Admin key is static for v1; rotate before public exposure.
- SQLite file path is local-only; ensure `10_Skills_Library/05_Operations/data/` is not web-accessible.

## Non-Goals
- OAuth / Square payments integration (use existing Square payment links).
- Frontend migration. Static storefront stays untouched.
- Migrations. We write to the existing schema directly.
