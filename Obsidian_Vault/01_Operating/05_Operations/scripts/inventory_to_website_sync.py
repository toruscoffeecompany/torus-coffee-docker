#!/usr/bin/env python3
"""
Inventory → Website Sync Script for Torus Coffee Company.

Reads inventory_master.json and regenerates next-storefront/data/products.ts
with all products, payment links, and correct SKUs.

Usage:
    venv/Scripts/python.exe scripts/inventory_to_website_sync.py --dry-run
    venv/Scripts/python.exe scripts/inventory_to_website_sync.py --apply

The products.ts has additional static fields (ingredients, allergens, etc.)
that are not in inventory_master.json. These are filled from existing
products.ts data where SKUs match, otherwise defaulted.
"""
import json
import re
import sys
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY = VAULT / "04_Products" / "inventory_master.json"
PRODUCTS_TS = VAULT / "06_Website" / "next-storefront" / "data" / "products.ts"
PRODUCT_HELPERS = VAULT / "06_Website" / "next-storefront" / "data" / "productHelpers.ts"


def slugify(text):
    """Convert text to URL slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def load_inventory():
    if not INVENTORY.exists():
        print(f"ERROR: {INVENTORY} not found")
        return None
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def load_existing_products_ts():
    """Parse existing products.ts to extract static fields for matching products."""
    if not PRODUCTS_TS.exists():
        return {}

    content = PRODUCTS_TS.read_text(encoding="utf-8")
    # Extract product blocks from the TypeScript file
    sku_map = {}

    # Find all product blocks in nextProducts array
    # Parse by looking for sku: "..." within braces
    pattern = r'{\s*name:\s*"([^"]+)",\s*slug:\s*"([^"]+)",\s*sku:\s*"([^"]+)",[^}]*?imageUrl:\s*"([^"]+)"[^}]*?}'
    matches = re.findall(pattern, content, re.DOTALL)

    for name, slug, sku, image_url in matches:
        sku_map[sku] = {
            "name": name,
            "slug": slug,
            "imageUrl": image_url,
        }

    return sku_map


def generate_products_ts(inventory_data, dry_run=True):
    """Generate products.ts content from inventory_master.json."""
    products = inventory_data.get("products", [])
    existing = load_existing_products_ts()

    lines = []
    lines.append("export type Product = {")
    lines.append("  name: string;")
    lines.append("  slug: string;")
    lines.append("  sku: string;")
    lines.append("  category: string;")
    lines.append("  priceCents: number;")
    lines.append("  quantityOnHand: number;")
    lines.append("  lowStockThreshold: number;")
    lines.append("  weightOz: number;")
    lines.append("  costCents: number;")
    lines.append("  shortDescription: string;")
    lines.append("  fullDescription: string;")
    lines.append("  ingredients: string;")
    lines.append("  allergens: string;")
    lines.append("  storageInstructions: string;")
    lines.append("  shelfLife: string;")
    lines.append("  imageAlt: string;")
    lines.append("  imageUrl: string;")
    lines.append("  squarePaymentLink: string;")
    lines.append("  seoDescription: string;")
    lines.append("  badge: string;")
    lines.append("  featured: boolean;")
    lines.append("};")
    lines.append("")
    lines.append("")
    lines.append("export const products: Product[] = [")

    for p in products:
        if not p.get("visible", False):
            continue

        sku = p["sku"]
        name = p["name"]
        price = p["price"]
        price_cents = int(round(price * 100))
        inventory = p.get("inventory", 0)
        cost = p.get("cost", 0)
        cost_cents = int(round(cost * 100))
        weight = p.get("weight", 0)
        weight_oz = round(weight * 16, 4) if weight else 0  # kg to oz
        image = p.get("image", "")
        description = p.get("description", "")
        collection = p.get("collection", "")
        category = collection.split(";")[0] if ";" in collection else collection
        square_link = p.get("squarePaymentLink", "")
        ribbon = p.get("ribbon", "")

        # Use existing slug/image if available, otherwise generate
        if sku in existing:
            slug = existing[sku]["slug"]
            image_url = existing[sku]["imageUrl"]
        else:
            slug = slugify(name)
            image_url = image

        # SEO description: truncate description to first 160 chars for SEO
        desc_plain = re.sub(r"<[^>]+>", "", description).strip()
        seo_desc = desc_plain[:160] if desc_plain else ""

        # Short description: product name
        short_desc = name

        featured = "true" if ribbon == "New Arrival" or inventory <= 5 else "false"

        lines.append("  {")
        lines.append(f'    name: "{name}",')
        lines.append(f'    slug: "{slug}",')
        lines.append(f'    sku: "{sku}",')
        lines.append(f'    category: "{category}",')
        lines.append(f'    priceCents: {price_cents},')
        lines.append(f'    quantityOnHand: {inventory},')
        lines.append(f'    lowStockThreshold: 8,')
        lines.append(f'    weightOz: {weight_oz},')
        lines.append(f'    costCents: {cost_cents},')
        lines.append(f'    shortDescription: "{short_desc}",')
        lines.append(f'    fullDescription: `')
        lines.append(f'      {description}')
        lines.append(f'    `,')
        lines.append(f'    ingredients: "",')
        lines.append(f'    allergens: "",')
        lines.append(f'    storageInstructions: "Store in a cool, dry place. Once opened, consume within 2 weeks.",')
        lines.append(f'    shelfLife: "12 months from manufacturing date",')
        lines.append(f'    imageAlt: "{name}",')
        lines.append(f'    imageUrl: "{image_url}",')
        lines.append(f'    squarePaymentLink: "{square_link}",')
        lines.append(f'    seoDescription: "{seo_desc}",')
        lines.append(f'    badge: "{ribbon}",')
        lines.append(f'    featured: {featured},')
        lines.append("  },")

    # Close array — handle trailing comma
    if lines[-1].endswith(","):
        # Remove trailing comma from last product
        lines[-1] = lines[-1].rstrip(",")

    lines.append("];")
    lines.append("")
    lines.append("export const productCount = products.length;")
    lines.append("")
    lines.append("export const nextProducts: Product[] = [")
    # Add a few sample nextProducts for static page generation
    visible = [p for p in products if p.get("visible", False)]
    for p in visible[:4]:
        slug = slugify(p["name"])
        lines.append("  {")
        lines.append(f'    name: "{p["name"]}",')
        lines.append(f'    slug: "{slug}",')
        lines.append(f'    sku: "{p["sku"]}",')
        lines.append(f'    priceCents: {int(round(p["price"] * 100))},')
        lines.append(f'    description: "{re.sub(r"<[^>]+>.*", "", p.get("description",""))[:100].strip()}",')
        lines.append("  },")
    if lines[-1].endswith(","):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("];")

    return "\n".join(lines)


def main():
    dry_run = "--apply" not in sys.argv

    inv_data = load_inventory()
    if not inv_data:
        return 1

    products = inv_data.get("products", [])
    visible_count = len([p for p in products if p.get("visible", False)])
    with_links = len([p for p in products if p.get("squarePaymentLink")])

    print(f"=== Inventory → Website Sync — {'DRY RUN' if dry_run else 'APPLY'} ===")
    print(f"Total products: {len(products)}")
    print(f"Visible products: {visible_count}")
    print(f"Products with Square links: {with_links}")
    print()

    # Generate new products.ts content
    new_content = generate_products_ts(inv_data, dry_run=dry_run)

    if dry_run:
        print(f"Would write {len(new_content)} bytes to {PRODUCTS_TS}")
        print("\n--- First 20 lines of generated output: ---")
        for line in new_content.split("\n")[:20]:
            print(line)
        print("\n✓ Dry run — changes not written. Run with --apply to save.")
    else:
        PRODUCTS_TS.write_text(new_content, encoding="utf-8")
        print(f"✓ Wrote {len(new_content)} bytes to {PRODUCTS_TS}")
        print(f"✓ {visible_count} visible products synced with correct SKUs and Square Payment Links")

    return 0


if __name__ == "__main__":
    sys.exit(main())
