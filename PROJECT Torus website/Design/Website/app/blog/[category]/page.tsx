import type { Metadata } from "next";
import { notFound } from "next/navigation";

const categories: Record<string, { title: string; description: string }> = {
  "the-orbit-report": { title: "The Orbit Report", description: "Stories, community updates, market notes, and Midwest snack life." },
  "the-orbit-workshop": { title: "The Orbit Workshop", description: "Freeze-drying lessons, business notes, packaging experiments, and practical how-tos." },
  "the-orbit-kitchen": { title: "The Orbit Kitchen", description: "Recipes, snack pairings, and ways to use Torus products." },
};

type BlogCategoryPageProps = { params: { category: string } };

export function generateStaticParams() {
  return Object.keys(categories).map((category) => ({ category }));
}

export function generateMetadata({ params }: BlogCategoryPageProps): Metadata {
  const category = categories[params.category];
  if (!category) return {};
  return { title: category.title, description: category.description };
}

export default function BlogCategoryPage({ params }: BlogCategoryPageProps) {
  const category = categories[params.category];
  if (!category) notFound();

  return (
    <section className="mx-auto max-w-5xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Blog Category</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">{category.title}</h1>
      <p className="mt-6 text-lg leading-8 text-ink/75">{category.description}</p>
      <div className="mt-8 rounded-lg border border-midnight/10 bg-white p-6 text-ink/70">
        Posts will appear here once the blog editor/content import phase is ready.
      </div>
    </section>
  );
}
