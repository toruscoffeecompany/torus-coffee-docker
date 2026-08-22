import type { Metadata } from "next";
import { ProductCard } from "@/components/product-card";
import { products } from "@/data/products";

export const metadata: Metadata = {
  title: "Shop Freeze-Dried Snacks",
  description: "Shop Torus Coffee Company freeze-dried candy and fruit snacks. Secure checkout powered by Square during launch.",
};

export default function ShopPage() {
  const categories = ["All", "Freeze-Dried Candy", "Freeze-Dried Fruit"];

  return (
    <section className="mx-auto max-w-7xl px-5 py-14">
      <div className="max-w-3xl">
        <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Shop</p>
        <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Freeze-dried snacks for curious snackers.</h1>
        <p className="mt-5 text-lg leading-8 text-ink/72">
          Browse our launch collection. Product photos and Square checkout links are being wired in as Phase 1 comes together.
        </p>
      </div>
      <div className="mt-8 flex flex-wrap gap-3">
        {categories.map((category) => (
          <span key={category} className="rounded-full border border-midnight/15 bg-white px-4 py-2 text-sm font-bold text-midnight">
            {category}
          </span>
        ))}
      </div>
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {products.map((product) => <ProductCard key={product.sku} product={product} />)}
      </div>
    </section>
  );
}
