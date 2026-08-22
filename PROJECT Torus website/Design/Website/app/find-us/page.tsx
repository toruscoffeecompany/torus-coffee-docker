import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Find Us",
  description: "Find Torus Coffee Company at markets, events, and local Iowa appearances.",
};

export default function FindUsPage() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Find Us</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Markets, events, and snack sightings.</h1>
      <p className="mt-6 text-lg leading-8 text-ink/75">
        Event details will live here once the current schedule is confirmed. This page is also a good place for flea market photos, booth updates, and local proof that Torus is out in the world.
      </p>
    </section>
  );
}
