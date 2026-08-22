import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getProductBySlug, getStockLabel, products } from "@/data/products";
import { formatPrice } from "@/lib/format";

type ProductPageProps = {
  params: { slug: string };
};

export function generateStaticParams() {
  return products.map((product) => ({ slug: product.slug }));
}

export function generateMetadata({ params }: ProductPageProps): Metadata {
  const product = getProductBySlug(params.slug);
  if (!product) return {};

  return {
    title: product.name,
    description: product.seoDescription,
    openGraph: {
      title: product.name,
      description: product.seoDescription,
      images: [product.imageUrl],
    },
  };
}

export default function ProductPage({ params }: ProductPageProps) {
  const product = getProductBySlug(params.slug);
  if (!product) notFound();

  const stock = getStockLabel(product);
  const canBuy = stock !== "Sold Out" && Boolean(product.squarePaymentLink);

  return (
    <section className="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[0.95fr_1.05fr]">
      <div className="relative aspect-square overflow-hidden rounded-lg border border-midnight/10 bg-cream shadow-soft">
        <Image src={product.imageUrl} alt={product.imageAlt} fill className="object-cover" priority />
      </div>
      <div>
        <Link href="/shop" className="text-sm font-bold text-berry underline decoration-stardust decoration-4 underline-offset-4">
          Back to shop
        </Link>
        <p className="mt-6 text-sm font-bold uppercase tracking-[0.16em] text-aurora">{product.category}</p>
        <h1 className="mt-3 font-display text-5xl font-bold leading-tight text-midnight">{product.name}</h1>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <span className="font-display text-4xl font-bold text-midnight">{formatPrice(product.priceCents)}</span>
          <span className="rounded-full bg-midnight px-4 py-2 text-sm font-bold text-cream">{stock}</span>
        </div>
        <p className="mt-6 text-lg leading-8 text-ink/75">{product.fullDescription}</p>
        <div className="mt-8 rounded-lg border border-midnight/10 bg-white p-5">
          <dl className="grid gap-4 text-sm sm:grid-cols-2">
            <div><dt className="font-bold text-midnight">SKU</dt><dd className="mt-1 text-ink/70">{product.sku}</dd></div>
            <div><dt className="font-bold text-midnight">Size</dt><dd className="mt-1 text-ink/70">{product.weightOz} oz</dd></div>
            <div><dt className="font-bold text-midnight">Ships</dt><dd className="mt-1 text-ink/70">United States only</dd></div>
            <div><dt className="font-bold text-midnight">Checkout</dt><dd className="mt-1 text-ink/70">Securely powered by Square</dd></div>
          </dl>
        </div>
        <div className="mt-8 flex flex-wrap gap-4">
          {canBuy ? (
            <a href={product.squarePaymentLink} className="rounded-full bg-stardust px-7 py-3 font-bold text-midnight transition hover:bg-midnight hover:text-cream">
              Buy Now
            </a>
          ) : (
            <span className="rounded-full bg-midnight/10 px-7 py-3 font-bold text-midnight">
              Square link coming soon
            </span>
          )}
          <Link href="/contact" className="rounded-full border border-midnight/20 px-7 py-3 font-bold text-midnight transition hover:border-midnight">
            Ask a Question
          </Link>
        </div>
      </div>
    </section>
  );
}
