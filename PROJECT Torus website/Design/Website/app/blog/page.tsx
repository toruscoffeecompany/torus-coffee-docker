import type { Metadata } from "next";
import Link from "next/link";

const categories = [
  { slug: "the-orbit-report", title: "The Orbit Report", description: "Stories, community updates, market notes, and Midwest snack life." },
  { slug: "the-orbit-workshop", title: "The Orbit Workshop", description: "Freeze-drying lessons, business notes, packaging experiments, and practical how-tos." },
  { slug: "the-orbit-kitchen", title: "The Orbit Kitchen", description: "Recipes, snack pairings, and ways to use Torus products when hunger or weird weather appears." },
];

export const metadata: Metadata = {
  title: "Blog",
  description: "Read The Orbit Report, The Orbit Workshop, and The Orbit Kitchen from Torus Coffee Company.",
};

export default function BlogPage() {
  return (
    <section className="mx-auto max-w-7xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Blog</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Three orbits. One snack universe.</h1>
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {categories.map((category) => (
          <Link key={category.slug} href={`/blog/${category.slug}`} className="rounded-lg border border-midnight/10 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-soft">
            <h2 className="font-display text-2xl font-bold text-midnight">{category.title}</h2>
            <p className="mt-3 text-sm leading-6 text-ink/70">{category.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
