import Link from "next/link";
import { ProductCard } from "@/components/product-card";
import { getFeaturedProducts } from "@/data/products";

export default function HomePage() {
  const featured = getFeaturedProducts();

  return (
    <>
      <section className="cosmic-band text-cream">
        <div className="mx-auto grid min-h-[620px] max-w-7xl items-center gap-12 px-5 py-20 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-stardust">Iowa-made freeze-dried snacks</p>
            <h1 className="mt-5 max-w-4xl font-display text-5xl font-bold leading-tight md:text-7xl">
              Stay Curious. Stay Crunchy. Stay Cosmic.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-cream/82">
              Freeze-dried candy, fruit, snacks, and cosmic kitchen experiments for lunch boxes, road trips, market days, and whatever life decides to throw at you.
            </p>
            <div className="mt-9 flex flex-wrap gap-4">
              <Link href="/shop" className="rounded-full bg-stardust px-7 py-3 font-bold text-midnight transition hover:bg-cream">
                Shop Snacks
              </Link>
              <Link href="/blog" className="rounded-full border border-cream/35 px-7 py-3 font-bold text-cream transition hover:border-stardust hover:text-stardust">
                Read the Blogs
              </Link>
            </div>
          </div>
          <div className="rounded-lg border border-cream/15 bg-cream/10 p-6 shadow-soft backdrop-blur">
            <p className="font-display text-3xl font-bold">Small batch. Big crunch.</p>
            <div className="mt-6 grid gap-4 text-sm leading-6 text-cream/82">
              <p>Secure checkout is handled by Square for launch, so buying stays simple and payment data stays out of our website.</p>
              <p>We ship in the United States and keep inventory simple: In Stock, Low Stock, or Sold Out.</p>
              <p>The zombie-apocalypse pantry joke is allowed here, but the real point is shelf-stable snacks that are fun when life gets weird.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Launch collection</p>
            <h2 className="mt-2 font-display text-4xl font-bold text-midnight">Featured cosmic crunch</h2>
          </div>
          <Link href="/shop" className="font-bold text-midnight underline decoration-stardust decoration-4 underline-offset-4">
            View all products
          </Link>
        </div>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {featured.map((product) => <ProductCard key={product.sku} product={product} />)}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:grid-cols-3">
          {[
            ["Midwest Made", "Small-batch snacks made with Iowa grit, curiosity, and a healthy respect for winter."],
            ["Square Checkout", "Launch checkout runs through Square so payments stay familiar, secure, and simple."],
            ["Blogs Built In", "The Orbit Report, The Orbit Workshop, and The Orbit Kitchen are designed into the site from day one."],
          ].map(([title, body]) => (
            <div key={title} className="rounded-lg border border-midnight/10 bg-cream p-6">
              <h3 className="font-display text-2xl font-bold text-midnight">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-ink/70">{body}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
