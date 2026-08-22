#!/usr/bin/env python3
"""
Sync local SQLite product data and vault images into next-storefront.
Reads torus_local.db and copies best available product images into public/images/products/.
Writes data/products.ts with real product data.
"""
from pathlib import Path
import sqlite3
import shutil
import re

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DB_PATH = VAULT / "10_Skills_Library/05_Operations/data/torus_local.db"
NEXT_STORE = VAULT / "06_Website/next-storefront"
PRODUCTS_TS = NEXT_STORE / "data/products.ts"
PUBLIC_IMAGES = NEXT_STORE / "public/images/products"
PUBLIC_IMAGES.mkdir(parents=True, exist_ok=True)

# Mapping from SQLite sku/slug to vault image folder/keywords
IMAGE_SOURCES = {
    "TCC-SDB-001": [
        "04_Products/Product_Photos/Star-Dusted_Banana_Crunch",
        "04_Products/Freeze-Dried Fruit/Star-Dusted Banana Crunch - Freeze-dried Bananas with Cin Sug",
        "08_Design_Brand",
    ],
    "TCC-ACC-001": [
        "04_Products/Freeze-Dried Fruit/Apple Cinnamon Comets - Freeze-Dried Green Apples w  Cin Sug",
    ],
    "TCC-AZC-001": [
        "04_Products/Freeze-Dried Fruit/Apple Zephyr Chips - Freeze Dried Apples",
    ],
    "TCC-ABB-001": [
        "04_Products/Freeze-Dried Candy/Aurora Bites - Freeze dried Skittles",
    ],
    "TCC-SAB-001": [
        "04_Products/Freeze-Dried Candy/Sour Aurora Bites - Freeze Dried Sour Skittles",
    ],
    "TCC-CBC-001": [
        "04_Products/Freeze-Dried Fruit/Cosmic Bananas - Freeze Dried Bananas",
    ],
    "TCC-SSB-001": [
        "04_Products/Freeze-Dried Fruit/Solar Strawberries - Freeze-Dried Strawberries",
    ],
}

KEYWORD_PRIORITY = [
    "website picture",
    "website v1",
    "website v2",
    "website v3",
    "website v4",
    "website v5",
    "photo_001",
    "photo_002",
    "front website",
    "front label",
]


def find_best_image(sku: str) -> Path | None:
    candidates = IMAGE_SOURCES.get(sku, [])
    for base in candidates:
        base_path = VAULT / base
        if not base_path.exists():
            continue
        files = [p for p in base_path.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        if not files:
            continue
        # Prefer filenames matching keywords
        scored = []
        for f in files:
            name = f.name.lower()
            score = 0
            for i, kw in enumerate(KEYWORD_PRIORITY):
                if kw in name:
                    score = max(score, 100 - i)
            scored.append((score, f))
        scored.sort(key=lambda x: (x[0], x[1].name), reverse=True)
        return scored[0][1]
    return None


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def sync():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    products = conn.execute("SELECT * FROM products ORDER BY sort_order, id").fetchall()
    conn.close()

    out_lines = [
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

    for p in products:
        sku = p["sku"]
        slug = p["slug"]
        name = p["name"]
        image_src = find_best_image(sku)
        image_filename = None
        if image_src:
            ext = image_src.suffix.lower()
            if ext in {".jpeg", ".jpg"}:
                ext = ".jpg"
            elif ext == ".png":
                ext = ".png"
            else:
                ext = ".jpg"
            image_filename = f"{slug}{ext}"
            dest = PUBLIC_IMAGES / image_filename
            shutil.copy2(image_src, dest)

        image_url = f"/images/products/{image_filename}" if image_filename else "/images/products/product-placeholder.svg"
        image_alt = f"{name} from Torus Coffee Company"

        out_lines.append("  {")
        out_lines.append(f"    name: '{name}',")
        out_lines.append(f"    slug: '{slug}',")
        out_lines.append(f"    sku: '{sku}',")
        out_lines.append(f"    category: '{p['category']}',")
        out_lines.append(f"    priceCents: {p['price_cents']},")
        out_lines.append(f"    quantityOnHand: {p['quantity_on_hand']},")
        out_lines.append(f"    lowStockThreshold: {p['low_stock_threshold']},")
        out_lines.append(f"    weightOz: {p['net_weight_oz'] or 0},")
        if p["cost_cents"] is not None:
            out_lines.append(f"    costCents: {p['cost_cents']},")
        out_lines.append(f"    shortDescription: '{p['seo_description'] or name}',")
        out_lines.append(f"    fullDescription: '{p['seo_description'] or name}',")
        if p["ingredients"]:
            out_lines.append(f"    ingredients: '{p['ingredients']}',")
        if p["allergens"]:
            out_lines.append(f"    allergens: '{p['allergens']}',")
        if p["storage_instructions"]:
            out_lines.append(f"    storageInstructions: '{p['storage_instructions']}',")
        if p["shelf_life"]:
            out_lines.append(f"    shelfLife: '{p['shelf_life']}',")
        out_lines.append(f"    imageAlt: '{image_alt}',")
        out_lines.append(f"    imageUrl: '{image_url}',")
        if p["main_image_url"]:
            out_lines.append(f"    squarePaymentLink: '{p['main_image_url']}',")
        out_lines.append(f"    seoDescription: '{p['seo_description'] or name}',")
        if p["featured"]:
            out_lines.append("    featured: true,")
        out_lines.append("  },")

    out_lines.append("];")
    out_lines.append("")

    PRODUCTS_TS.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Wrote {PRODUCTS_TS}")
    print(f"Images dir: {PUBLIC_IMAGES}")
    print(f"Images copied: {len(list(PUBLIC_IMAGES.glob('*')))}")


if __name__ == "__main__":
    sync()
