import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Shipping Policy",
  description: "Shipping Policy for Torus Coffee Company.",
};

export default function PolicyPage() {
  return (
    <section className="mx-auto max-w-4xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Policy</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Shipping Policy</h1>
      <div className="mt-8 rounded-lg border border-midnight/10 bg-white p-6 text-lg leading-8 text-ink/75">
        <p>This placeholder must be replaced with updated 2026 shipping language before launch. Current design direction is United States shipping only.</p>
      </div>
    </section>
  );
}
