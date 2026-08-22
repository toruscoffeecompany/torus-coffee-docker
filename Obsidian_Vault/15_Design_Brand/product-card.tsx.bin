import Image from "next/image";
import Link from "next/link";
import { Product, getStockLabel } from "@/data/products";
import { formatPrice } from "@/lib/format";

export function ProductCard({ product }: { product: Product }) {
  const stock = getStockLabel(product);

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-lg border border-midnight/10 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-soft">
      <Link href={`/shop/${product.slug}`} className="relative block aspect-square overflow-hidden bg-cream">
        <Image src={product.imageUrl} alt={product.imageAlt} fill className="object-cover transition duration-300 group-hover:scale-105" />
        <div className="absolute left-3 top-3 flex flex-wrap gap-2">
          {product.badge ? <span className="rounded-full bg-berry px-3 py-1 text-xs font-bold text-white">{product.badge}</span> : null}
          <span className="rounded-full bg-midnight px-3 py-1 text-xs font-bold text-cream">{stock}</span>
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-aurora">{product.category}</p>
        <h3 className="mt-2 font-display text-xl font-bold text-midnight">
          <Link href={`/shop/${product.slug}`}>{product.name}</Link>
        </h3>
        <p className="mt-3 flex-1 text-sm leading-6 text-ink/70">{product.shortDescription}</p>
        <div className="mt-5 flex items-center justify-between gap-4">
          <span className="font-display text-2xl font-bold text-midnight">{formatPrice(product.priceCents)}</span>
          <Link href={`/shop/${product.slug}`} className="rounded-full bg-midnight px-4 py-2 text-sm font-bold text-cream transition hover:bg-orbit">
            Details
          </Link>
        </div>
      </div>
    </article>
  );
}
