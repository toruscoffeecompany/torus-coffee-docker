import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description: "Learn about Torus Coffee Company, an Iowa-made freeze-dried snack business with cosmic crunch and Midwest heart.",
};

export default function AboutPage() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">About Torus</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Small-batch snacks with cosmic curiosity.</h1>
      <div className="mt-8 grid gap-6 text-lg leading-8 text-ink/75">
        <p>Torus Coffee Company is building a freeze-dried snack world from Iowa: fruit, candy, recipes, market stories, and pantry-friendly treats for regular days and deeply irregular ones.</p>
        <p>The voice is playful, but the goals are practical: clear products, secure checkout, honest inventory, U.S. shipping, and a business foundation that can grow into wholesale later.</p>
      </div>
    </section>
  );
}
