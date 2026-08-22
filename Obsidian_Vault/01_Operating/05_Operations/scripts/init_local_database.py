#!/usr/bin/env python3
"""
Torus Coffee Company — Local Database Schema & Seed
SQLite database for products, orders, customers, and inventory.
"""
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DB_PATH = VAULT / "10_Skills_Library/05_Operations/data/torus_local.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'Freeze-Dried Fruit',
    status TEXT DEFAULT 'draft',
    price_cents INTEGER NOT NULL,
    cost_cents INTEGER,
    quantity_on_hand INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    track_inventory BOOLEAN DEFAULT 1,
    main_image_url TEXT,
    ingredients TEXT,
    allergens TEXT,
    storage_instructions TEXT,
    shelf_life TEXT,
    net_weight_oz REAL,
    shipping_weight_oz REAL,
    ships_us_only BOOLEAN DEFAULT 1,
    requires_shipping BOOLEAN DEFAULT 1,
    seo_title TEXT,
    seo_description TEXT,
    featured BOOLEAN DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS product_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    alt_text TEXT,
    image_type TEXT DEFAULT 'gallery',
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    marketing_consent BOOLEAN DEFAULT 0,
    marketing_consent_at TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_number TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending',
    subtotal_cents INTEGER NOT NULL,
    tax_cents INTEGER DEFAULT 0,
    shipping_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    payment_method TEXT,
    payment_status TEXT DEFAULT 'pending',
    shipping_name TEXT,
    shipping_address_line1 TEXT,
    shipping_city TEXT,
    shipping_state TEXT,
    shipping_zip TEXT,
    shipping_country TEXT DEFAULT 'US',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    subtotal_cents INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS inventory_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    previous_quantity INTEGER,
    new_quantity INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    reason TEXT DEFAULT 'other',
    note TEXT,
    actor TEXT DEFAULT 'system',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS automation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    topic TEXT,
    message TEXT,
    level TEXT DEFAULT 'info',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_adjustments(product_id);
"""

SEED_PRODUCTS = """
INSERT OR IGNORE INTO products (sku, name, slug, category, status, price_cents, cost_cents, quantity_on_hand, ingredients, allergens, storage_instructions, shelf_life, net_weight_oz, shipping_weight_oz, seo_title, seo_description, featured, sort_order) VALUES
('TCC-SDB-001', 'Star-Dusted Banana Crunch', 'star-dusted-banana-crunch', 'Freeze-Dried Fruit', 'active', 899, 350, 42, 'Freeze-dried bananas, coconut, honey', 'Coconut', 'Store in airtight container', '12 months', 1.5, 2.0, 'Star-Dusted Banana Crunch', 'Crunchy freeze-dried banana bites with coconut and honey.', 1, 1),
('TCC-ACC-001', 'Apple Cinnamon Comets', 'apple-cinnamon-comets', 'Freeze-Dried Fruit', 'active', 899, 320, 35, 'Freeze-dried apples, cinnamon, sugar', 'None', 'Store in airtight container', '12 months', 1.5, 2.0, 'Apple Cinnamon Comets', 'Sweet freeze-dried apple pieces with cinnamon.', 0, 2),
('TCC-AZC-001', 'Apple Zephyr Chips', 'apple-zephyr-chips', 'Freeze-Dried Fruit', 'active', 799, 290, 28, 'Freeze-dried apples', 'None', 'Store in airtight container', '12 months', 1.2, 1.8, 'Apple Zephyr Chips', 'Light and crispy freeze-dried apple chips.', 0, 3),
('TCC-ABB-001', 'Aurora Bites', 'aurora-bites', 'Freeze-Dried Fruit', 'active', 999, 400, 15, 'Freeze-dried mixed berries', 'None', 'Store in airtight container', '12 months', 1.5, 2.0, 'Aurora Bites', 'Colorful freeze-dried mixed berry bites.', 1, 4),
('TCC-SAB-001', 'Sour Aurora Bites', 'sour-aurora-bites', 'Freeze-Dried Fruit', 'active', 999, 400, 12, 'Freeze-dried mixed berries, citric acid', 'None', 'Store in airtight container', '12 months', 1.5, 2.0, 'Sour Aurora Bites', 'Tangy freeze-dried mixed berry bites with a sour kick.', 0, 5),
('TCC-CBC-001', 'Cosmic Bananas', 'cosmic-bananas', 'Freeze-Dried Fruit', 'active', 799, 280, 50, 'Freeze-dried bananas', 'None', 'Store in airtight container', '12 months', 1.2, 1.8, 'Cosmic Bananas', 'Classic freeze-dried banana crunch.', 0, 6),
('TCC-SSB-001', 'Solar Strawberries', 'solar-strawberries', 'Freeze-Dried Fruit', 'active', 899, 340, 22, 'Freeze-dried strawberries', 'None', 'Store in airtight container', '12 months', 1.2, 1.8, 'Solar Strawberries', 'Sweet freeze-dried strawberry pieces.', 0, 7);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        conn.executescript(SEED_PRODUCTS)
        conn.commit()
        
        # Verify
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"DB initialized at {DB_PATH}")
        print(f"Products seeded: {count}")
        
        # List tables
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        print(f"Tables: {[t['name'] for t in tables]}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
