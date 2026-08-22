#!/usr/bin/env python3
"""
Generate Next.js static product data from inventory_master.json.
Writes 06_Website/next-storefront/data/products.ts.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
INVENTORY_FILE = VAULT / "04_Products" / "inventory_master.json"
WEBSITE_DATA = VAULT / "06_Website" / "next-storefront" / "data" / "products.ts"


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace(" - ", " ")
    text = text.replace("'", "")
    tokens = []
    for token in text.split():
        token = "".join(ch for ch in token if ch.isalnum())
        if token:
            tokens.append(token)
    return "-".join(tokens)


def build_description(raw: str, short: str) -> str:
    desc = raw.strip()
    desc = desc.replace("\n\n&nbsp;\n\n", "\n\n")
    desc = desc.replace("&nbsp;", " ")
    desc = desc.replace("<ul>", "").replace("</ul>", "")
    desc = desc.replace("<li>", "\n- ").replace("</li>", "")
    desc = desc.replace("\t", " ")
    if not desc and short:
        desc = short
    return desc.strip()


def to_cents(value: float) -> int:
    return int(round(float(value) * 100))


def generate() -> None:
    if not INVENTORY_FILE.exists():
        raise FileNotFoundError(f"Inventory file missing: {INVENTORY_FILE}")

    with INVENTORY_FILE.open("r", encoding="utf-8") as f:
        inventory = json.load(f)

    items = inventory.get("products", [])
    if not isinstance(items, list):
        raise TypeError("inventory.products must be a list")

    lines = [
        "// Auto-generated from inventory_master.json",
        f"// Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "export type ProductCategory = 'Freeze-Dried Candy' | 'Freeze-Dried Fruit';",
        "",
        "export type Product = {",
        "  name: string;",
        "  slug: string;",
        "  sku: string;",
        "  category: ProductCategory;",
        "  priceCents: number;",
        "  quantityOnHand: number;",
        "  lowStockThreshold: number;",
        "  weightOz: number;",
        "  costCents?: number;",
        "  shortDescription: string;",
        "  fullDescription: string;",
        "  ingredients?: string;",
        "  allergens?: string;",
        "  storageInstructions?: string;",
        "  shelfLife?: string;",
        "  imageAlt: string;",
        "  imageUrl: string;",
        "  squarePaymentLink?: string;",
        "  seoDescription: string;",
        "  badge?: string;",
        "  featured?: boolean;",
        "};",
        "",
        "export const products: Product[] = [",
    ]

    for item in items:
        category = "Freeze-Dried Candy" if "Candy" in item.get("collection", "") else "Freeze-Dried Fruit"
        short = item.get("name", item.get("sku", ""))
        full = build_description(item.get("description", ""), short)
        lines.extend([
            "  {",
            f"    name: {json.dumps(item.get('name', ''), ensure_ascii=False)},",
            f"    slug: {json.dumps(slugify(item.get('name', item.get('sku', ''))), ensure_ascii=False)},",
            f"    sku: {json.dumps(item.get('sku', ''), ensure_ascii=False)},",
            f"    category: {json.dumps(category, ensure_ascii=False)},",
            f"    priceCents: {to_cents(item.get('price', 0))},",
            f"    quantityOnHand: {item.get('inventory', 0)},",
            f"    lowStockThreshold: 5,",
            f"    weightOz: {item.get('weight', 0)},",
            f"    costCents: {to_cents(item.get('cost', 0))},",
            f"    shortDescription: {json.dumps(short, ensure_ascii=False)},",
            f"    fullDescription: {json.dumps(full, ensure_ascii=False)},",
            f"    ingredients: {json.dumps(item.get('ingredients', ''), ensure_ascii=False)},",
            f"    allergens: {json.dumps(item.get('allergens', ''), ensure_ascii=False)},",
            f"    storageInstructions: {json.dumps(item.get('storageInstructions', ''), ensure_ascii=False)},",
            f"    shelfLife: {json.dumps(item.get('shelfLife', ''), ensure_ascii=False)},",
            f"    imageAlt: {json.dumps(short, ensure_ascii=False)},",
            f"    imageUrl: {json.dumps(item.get('image', ''), ensure_ascii=False)},",
            f"    squarePaymentLink: {json.dumps(item.get('squarePaymentLink', ''), ensure_ascii=False)},",
            f"    seoDescription: {json.dumps(full[:160], ensure_ascii=False)},",
            f"    badge: {json.dumps(item.get('ribbon', ''), ensure_ascii=False)},",
            "    featured: false,",
            "  },",
        ])

    lines.extend([
        "];",
        "",
        "export const productCount = products.length;",
    ])

    WEBSITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    WEBSITE_DATA.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ Generated {len(items)} products -> {WEBSITE_DATA}")


if __name__ == "__main__":
    generate()
