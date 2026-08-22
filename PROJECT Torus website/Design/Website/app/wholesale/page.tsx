import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Wholesale",
  description: "Wholesale and retail partner inquiries for Torus Coffee Company freeze-dried snacks.",
};

export default function WholesalePage() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Wholesale</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Interested in stocking Torus?</h1>
      <p className="mt-6 text-lg leading-8 text-ink/75">
        We are building toward retail and grocery partnerships while keeping direct online sales as the first launch focus. Use the contact page for wholesale inquiries while the formal retailer packet is being prepared.
      </p>
      <Link href="/contact" className="mt-8 inline-flex rounded-full bg-midnight px-7 py-3 font-bold text-cream transition hover:bg-orbit">
        Contact Torus
      </Link>
    </section>
  );
}
