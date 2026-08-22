export type ProductCategory = "Freeze-Dried Candy" | "Freeze-Dried Fruit";

export type Product = {
  name: string;
  slug: string;
  sku: string;
  category: ProductCategory;
  priceCents: number;
  quantityOnHand: number;
  lowStockThreshold: number;
  weightOz: number;
  costCents?: number;
  shortDescription: string;
  fullDescription: string;
  imageAlt: string;
  imageUrl: string;
  squarePaymentLink?: string;
  seoDescription: string;
  badge?: string;
  featured?: boolean;
};

export const products: Product[] = [
  {
    name: "Star-Dusted Banana Crunch 1.15oz",
    slug: "star-dusted-banana-crunch-115oz",
    sku: "TCC-SDB-115",
    category: "Freeze-Dried Fruit",
    priceCents: 600,
    quantityOnHand: 15,
    lowStockThreshold: 5,
    weightOz: 1.15,
    costCents: 87,
    shortDescription: "Freeze-dried banana slices with a cozy cinnamon-sugar sparkle and a light cosmic crunch.",
    fullDescription: "Ripe banana slices are freeze-dried for a light, crispy texture, then finished with cinnamon-sugar warmth. It is banana bread energy with a cleaner crunch and a little stardust.",
    imageAlt: "Star-Dusted Banana Crunch freeze-dried banana snack from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Star-Dusted Banana Crunch from Torus Coffee Company: freeze-dried banana slices with cinnamon-sugar flavor and a light cosmic crunch.",
    featured: true,
  },
  {
    name: "Apple Cinnamon Comets 1.15oz",
    slug: "apple-cinnamon-comets-115oz",
    sku: "TCC-ACC-115",
    category: "Freeze-Dried Fruit",
    priceCents: 500,
    quantityOnHand: 17,
    lowStockThreshold: 5,
    weightOz: 1.15,
    costCents: 90,
    shortDescription: "Crisp freeze-dried apple slices dusted with cinnamon sweetness for an orchard-meets-orbit snack.",
    fullDescription: "Crisp green apples meet cinnamon, brown sugar, and cane sugar for a warm freeze-dried crunch. Cozy, tart, sweet, and ready for lunch boxes, road trips, or suspiciously dramatic weather.",
    imageAlt: "Apple Cinnamon Comets freeze-dried apple snack from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Apple Cinnamon Comets from Torus Coffee Company: freeze-dried apple slices with cinnamon sweetness and a crisp orchard crunch.",
    featured: true,
  },
  {
    name: "Aurora Berryalis 2.6oz",
    slug: "aurora-berryalis-26oz",
    sku: "TCC-ARB-26",
    category: "Freeze-Dried Candy",
    priceCents: 600,
    quantityOnHand: 21,
    lowStockThreshold: 5,
    weightOz: 2.6,
    costCents: 87,
    shortDescription: "A bold berry-flavored freeze-dried candy with bright color, big crunch, and cosmic energy.",
    fullDescription: "Aurora Berryalis is a wild berry freeze-dried candy with a crackly, melt-in-your-mouth bite. It is bright, punchy, and built for snackers who like their treats a little extra.",
    imageAlt: "Aurora Berryalis freeze-dried berry candy from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Aurora Berryalis from Torus Coffee Company: bold berry freeze-dried candy with bright flavor, cosmic color, and satisfying crunch.",
  },
  {
    name: "Sour Aurora Bites 2.6oz",
    slug: "sour-aurora-bites-26oz",
    sku: "TCC-SAB-26",
    category: "Freeze-Dried Candy",
    priceCents: 600,
    quantityOnHand: 10,
    lowStockThreshold: 5,
    weightOz: 2.6,
    costCents: 91,
    shortDescription: "A sour-sweet freeze-dried candy with a tart snap and a bright cosmic crunch.",
    fullDescription: "Sour Aurora Bites bring the tart side of the cosmos: light, crunchy, sour-sweet, and easy to keep reaching for after the first handful.",
    imageAlt: "Sour Aurora Bites freeze-dried sour candy from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Sour Aurora Bites from Torus Coffee Company: sour-sweet freeze-dried candy with a tart snap and crunchy cosmic bite.",
    badge: "Low Stock Soon",
  },
  {
    name: "Solar Strawberries 0.5oz",
    slug: "solar-strawberries-05oz",
    sku: "TCC-SS-05",
    category: "Freeze-Dried Fruit",
    priceCents: 700,
    quantityOnHand: 18,
    lowStockThreshold: 5,
    weightOz: 0.5,
    costCents: 116,
    shortDescription: "Sweet, tart freeze-dried strawberries with berry flavor and a light, crispy bite.",
    fullDescription: "Solar Strawberries are crisp, bright, and berry-forward. They are good for snacking, topping, gifting, or quietly building your pantry for whatever life decides to throw next.",
    imageAlt: "Solar Strawberries freeze-dried strawberry snack from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Solar Strawberries from Torus Coffee Company: sweet and tart freeze-dried strawberries with bright berry flavor and crisp texture.",
    featured: true,
  },
  {
    name: "Cosmic Bananas 1.55oz",
    slug: "cosmic-bananas-155oz",
    sku: "TCC-CB-155",
    category: "Freeze-Dried Fruit",
    priceCents: 500,
    quantityOnHand: 22,
    lowStockThreshold: 5,
    weightOz: 1.55,
    costCents: 59,
    shortDescription: "Freeze-dried banana bites with sweet banana flavor and a satisfying space-age crunch.",
    fullDescription: "Cosmic Bananas are sweet banana bites transformed into a shelf-stable crunch. Simple, snackable, and ready for lunch bags, hiking packs, or mild apocalypse preparation.",
    imageAlt: "Cosmic Bananas freeze-dried banana snack from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Cosmic Bananas from Torus Coffee Company: freeze-dried banana bites with sweet flavor and a satisfying crunchy texture.",
  },
  {
    name: "Aurora Bites 2.6oz",
    slug: "aurora-bites-26oz",
    sku: "TCC-AB-26",
    category: "Freeze-Dried Candy",
    priceCents: 600,
    quantityOnHand: 40,
    lowStockThreshold: 5,
    weightOz: 2.6,
    costCents: 68,
    shortDescription: "Crunchy rainbow freeze-dried candy with fruity flavor and a stellar snap.",
    fullDescription: "Aurora Bites are fruity rainbow candy transformed into a light, crunchy snack. Big color, big snap, and a crowd-friendly flavor for cosmic candy fans.",
    imageAlt: "Aurora Bites freeze-dried rainbow candy from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Aurora Bites from Torus Coffee Company: crunchy rainbow freeze-dried candy with fruity flavor and a stellar snap.",
    featured: true,
    badge: "Best Seller",
  },
  {
    name: "Apple Zephyr Chips 1.15oz",
    slug: "apple-zephyr-chips-115oz",
    sku: "TCC-AZC-115",
    category: "Freeze-Dried Fruit",
    priceCents: 500,
    quantityOnHand: 29,
    lowStockThreshold: 5,
    weightOz: 1.15,
    costCents: 60,
    shortDescription: "Whisper-light freeze-dried apple slices with orchard sweetness and crisp texture.",
    fullDescription: "Apple Zephyr Chips are light, crisp apple slices with a clean orchard sweetness. A simple fruit snack with enough crunch to keep things interesting.",
    imageAlt: "Apple Zephyr Chips freeze-dried apple snack from Torus Coffee Company",
    imageUrl: "/images/products/product-placeholder.svg",
    seoDescription: "Shop Apple Zephyr Chips from Torus Coffee Company: light freeze-dried apple slices with orchard sweetness and crisp crunch.",
  },
];

export function getProductBySlug(slug: string) {
  return products.find((product) => product.slug === slug);
}

export function getFeaturedProducts() {
  return products.filter((product) => product.featured).slice(0, 4);
}

export function getStockLabel(product: Product) {
  if (product.quantityOnHand <= 0) return "Sold Out";
  if (product.quantityOnHand <= product.lowStockThreshold) return "Low Stock";
  return "In Stock";
}
